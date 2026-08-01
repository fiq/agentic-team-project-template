"""Tests for the declarative pre-commit hook gate.

The gate must stay fast and honest: checks run concurrently, a blocking
failure stops a commit, an advisory failure does not, and an unspecialised
`project` target is skipped rather than failing the template out of the box.
"""
import importlib.machinery
import importlib.util
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

import _support  # noqa: F401
import toon

ROOT = _support.ROOT
BIN = _support.BIN
CONFIG = ROOT / ".agents/hooks.toon"


def load_runner():
    loader = importlib.machinery.SourceFileLoader("_run_hooks", str(BIN / "run-hooks"))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


runner = load_runner()


class TestHooksConfig(unittest.TestCase):
    def test_config_exists_and_parses(self):
        self.assertTrue(CONFIG.exists())
        data = toon.loads(CONFIG.read_text())
        self.assertIn("pre_commit", data)

    def test_every_check_declares_the_required_fields(self):
        checks = toon.loads(CONFIG.read_text())["pre_commit"]["checks"]
        self.assertTrue(checks)
        for check in checks:
            with self.subTest(check=check.get("id")):
                self.assertIn("id", check)
                self.assertIsInstance(check.get("command"), list)
                self.assertIn("blocking", check)
                self.assertIn("why", check, "a check must say why it earns a slot")

    def test_check_ids_are_unique(self):
        checks = toon.loads(CONFIG.read_text())["pre_commit"]["checks"]
        ids = [check["id"] for check in checks]
        self.assertEqual(len(ids), len(set(ids)))

    def test_secrets_is_blocking(self):
        checks = toon.loads(CONFIG.read_text())["pre_commit"]["checks"]
        secrets = [check for check in checks if check["id"] == "secrets"]
        self.assertTrue(secrets, "the secrets check must be declared")
        self.assertTrue(secrets[0]["blocking"], "a leaked credential must block")

    def test_a_default_timeout_is_declared(self):
        section = toon.loads(CONFIG.read_text())["pre_commit"]
        self.assertIsInstance(section.get("default_timeout_seconds"), int)


class TestUnspecialisedDetection(unittest.TestCase):
    def test_unspecialised_project_target_is_recognised(self):
        self.assertTrue(
            runner.is_unspecialised([".agentic-template/bin/project", "lint"], {"lint"})
        )

    def test_specialised_project_target_is_not_skipped(self):
        self.assertFalse(
            runner.is_unspecialised([".agentic-template/bin/project", "check-secrets"], {"lint"})
        )

    def test_a_non_project_command_is_never_skipped(self):
        self.assertFalse(runner.is_unspecialised(["ruff", "check"], {"check"}))

    def test_bare_toon_booleans_render_as_shell_tokens(self):
        # `command: [true]` parses as the boolean True; str() would make it
        # "True", which is not the binary the author meant.
        self.assertEqual(runner.token(True), "true")
        self.assertEqual(runner.token(False), "false")
        self.assertEqual(runner.token(30), "30")
        self.assertEqual(runner.token("lint"), "lint")

    def test_template_state_skips_lint_rather_than_failing(self):
        # The template ships lint unwired; the gate must not fail because of it.
        self.assertIn("lint", runner.unspecialised_commands())


class TestGateBehaviour(unittest.TestCase):
    """Drive the runner against synthetic configs in a scratch directory."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".agents").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_config(self, body):
        (self.root / ".agents/hooks.toon").write_text(textwrap.dedent(body))

    def run_gate(self):
        return subprocess.run(
            [str(BIN / "run-hooks")],
            cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def test_passing_checks_exit_zero(self):
        self.write_config("""
            version: 1
            pre_commit:
              default_timeout_seconds: 10
              checks:
                - id: always-passes
                  command: [true]
                  blocking: true
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PRE-COMMIT OK", result.stdout)

    def test_a_blocking_failure_stops_the_commit(self):
        self.write_config("""
            version: 1
            pre_commit:
              default_timeout_seconds: 10
              checks:
                - id: blocker
                  command: [false]
                  blocking: true
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("PRE-COMMIT BLOCKED", result.stdout)
        self.assertIn("blocker", result.stdout)

    def test_an_advisory_failure_does_not_stop_the_commit(self):
        self.write_config("""
            version: 1
            pre_commit:
              default_timeout_seconds: 10
              checks:
                - id: advisor
                  command: [false]
                  blocking: false
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("advisory", result.stdout)

    def test_a_timeout_is_reported_and_blocks_when_blocking(self):
        self.write_config("""
            version: 1
            pre_commit:
              checks:
                - id: slow
                  command: [sleep, "30"]
                  blocking: true
                  timeout_seconds: 1
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("TIMEOUT", result.stdout)
        self.assertIn("budget", result.stdout)

    def test_checks_run_concurrently_not_sequentially(self):
        # Three one-second sleeps must finish in about one second, not three.
        self.write_config("""
            version: 1
            pre_commit:
              default_timeout_seconds: 20
              checks:
                - id: a
                  command: [sleep, "1"]
                  blocking: false
                  why: fixture
                - id: b
                  command: [sleep, "1"]
                  blocking: false
                  why: fixture
                - id: c
                  command: [sleep, "1"]
                  blocking: false
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout)
        header = result.stdout.splitlines()[0]
        seconds = float(header.rsplit(maxsplit=1)[-1].rstrip("s"))
        self.assertLess(seconds, 2.5, f"checks did not run in parallel: {header}")

    def test_results_print_in_declaration_order(self):
        # Reproducible output regardless of which check finishes first.
        self.write_config("""
            version: 1
            pre_commit:
              default_timeout_seconds: 20
              checks:
                - id: slower
                  command: [sleep, "1"]
                  blocking: false
                  why: fixture
                - id: faster
                  command: [true]
                  blocking: false
                  why: fixture
            """)
        result = self.run_gate()
        self.assertLess(result.stdout.index("slower"), result.stdout.index("faster"))

    def test_a_missing_command_fails_without_crashing(self):
        self.write_config("""
            version: 1
            pre_commit:
              checks:
                - id: missing
                  command: [definitely-not-a-real-binary-xyz]
                  blocking: true
                  why: fixture
            """)
        result = self.run_gate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("could not run", result.stdout)

    def test_no_config_is_not_an_error(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout)


class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / ".agents").mkdir(parents=True)
        (self.root / ".agents/hooks.toon").write_text(
            "version: 1\npre_commit:\n  checks: []\n"
        )
        binaries = self.root / ".agentic-template/bin"
        binaries.mkdir(parents=True)
        for name in ("project", "run-hooks"):
            target = binaries / name
            target.write_text((BIN / name).read_text())
            target.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def install(self):
        return subprocess.run(
            [str(BIN / "install-hooks")],
            cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def test_installs_a_pre_commit_hook(self):
        result = self.install()
        self.assertEqual(result.returncode, 0, result.stdout)
        hook = self.root / ".git/hooks/pre-commit"
        self.assertTrue(hook.exists())
        self.assertIn("project hooks", hook.read_text())

    def test_hook_delegates_to_the_config_rather_than_naming_checks(self):
        # Editing .agents/hooks.toon must take effect without reinstalling.
        self.install()
        hook = (self.root / ".git/hooks/pre-commit").read_text()
        self.assertIn("hooks.toon", hook)
        self.assertNotIn("check-secrets", hook)

    def test_reinstalling_over_our_own_hook_is_allowed(self):
        self.install()
        self.assertEqual(self.install().returncode, 0)

    def test_a_foreign_pre_commit_hook_is_left_alone(self):
        hook = self.root / ".git/hooks/pre-commit"
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text("#!/bin/sh\necho someone elses hook\n")
        result = self.install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("someone elses hook", hook.read_text())


if __name__ == "__main__":
    unittest.main()
