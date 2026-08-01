"""Tests for `project ready` command selection.

Regression cover for a bug where readiness detected "is this command
specialised?" by parsing `project --list`. That listing always prints the
union of COMMANDS and UNSPECIALISED, so the check could never be false: a
specialised project would try to run every runtime command, including ones
still deliberately unspecialised, and fail readiness for no real reason.
"""
import importlib.machinery
import importlib.util
import unittest

import _support  # noqa: F401

ROOT = _support.ROOT
BIN = _support.BIN


def load_module(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


ready = load_module("_project_ready_under_test", BIN / "project-ready")
dispatcher = load_module("_project_dispatcher_under_test", BIN / "project")


class TestRuntimeCommandSelection(unittest.TestCase):
    def test_template_state_runs_no_runtime_commands(self):
        selected = ready.select_runtime_commands(True, dispatcher.UNSPECIALISED)
        self.assertEqual(selected, [])

    def test_fully_unspecialised_project_runs_no_runtime_commands(self):
        # Not template state, but nothing specialised yet: readiness must not
        # invoke commands that would fail with "harness not specialised".
        everything = {command for command, _ in ready.RUNTIME_COMMANDS}
        self.assertEqual(ready.select_runtime_commands(False, everything), [])

    def test_only_specialised_commands_are_selected(self):
        # A real project part-way through specialisation: lint and test are
        # wired, integration and contract tests are deliberately not.
        unspecialised = {"build", "integration-test", "contract-test"}
        selected = ready.select_runtime_commands(False, unspecialised)
        self.assertEqual([command for command, _ in selected], ["lint", "test"])

    def test_fully_specialised_project_runs_everything_in_shift_left_order(self):
        selected = ready.select_runtime_commands(False, set())
        self.assertEqual(
            [command for command, _ in selected],
            ["lint", "build", "test", "integration-test", "contract-test"],
        )

    def test_lint_precedes_build_and_build_precedes_test(self):
        # AGENTS.md: "project lint runs before project test in CI".
        order = [command for command, _ in ready.RUNTIME_COMMANDS]
        self.assertLess(order.index("lint"), order.index("build"))
        self.assertLess(order.index("build"), order.index("test"))

    def test_build_is_actually_wired_into_readiness(self):
        # `build` was defined as a command but never invoked by readiness.
        self.assertIn("build", [command for command, _ in ready.RUNTIME_COMMANDS])

    def test_every_runtime_command_carries_a_distinct_label(self):
        labels = [label for _, label in ready.RUNTIME_COMMANDS]
        self.assertEqual(len(labels), len(set(labels)))


class TestDispatcherIsTheSourceOfTruth(unittest.TestCase):
    """The detection must read the dispatcher, not `project --list` output."""

    def test_dispatcher_exposes_an_unspecialised_set(self):
        self.assertIsInstance(dispatcher.UNSPECIALISED, set)
        self.assertTrue(dispatcher.UNSPECIALISED)

    def test_ready_can_load_the_dispatcher(self):
        module = ready._load_project_dispatcher()
        self.assertEqual(module.UNSPECIALISED, dispatcher.UNSPECIALISED)

    def test_list_output_cannot_distinguish_specialised_commands(self):
        # Documents *why* the dispatcher is loaded directly: every runtime
        # command appears in --list whether or not it is specialised, so a
        # membership test against that listing is always true.
        listed = set(dispatcher.COMMANDS) | dispatcher.UNSPECIALISED | {"help"}
        for command, _ in ready.RUNTIME_COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, listed)

    def test_template_state_leaves_runtime_commands_unspecialised(self):
        # Guards the template's own shipped state: these must fail clearly
        # until /specialise wires them up.
        for command in ("lint", "build", "test"):
            with self.subTest(command=command):
                self.assertIn(command, dispatcher.UNSPECIALISED)


if __name__ == "__main__":
    unittest.main()
