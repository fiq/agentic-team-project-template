import unittest

import _support  # noqa: F401
import environment

ROOT = _support.ROOT


class TestRuntimeDetection(unittest.TestCase):
    def test_detects_claude_code(self):
        self.assertEqual(environment.detect_runtime(ROOT, {"CLAUDECODE": "1"}), "claude-code")

    def test_detects_codex_from_either_variable(self):
        self.assertEqual(environment.detect_runtime(ROOT, {"CODEX_HOME": "/x"}), "codex")
        self.assertEqual(environment.detect_runtime(ROOT, {"CODEX_SANDBOX": "1"}), "codex")

    def test_explicit_variable_wins(self):
        self.assertEqual(
            environment.detect_runtime(ROOT, {"AGENTIC_RUNTIME": "roo", "CLAUDECODE": "1"}),
            "roo",
        )

    def test_unrecognised_host_is_unknown(self):
        self.assertEqual(environment.detect_runtime(ROOT, {}), "unknown")


class TestCapabilities(unittest.TestCase):
    def test_unknown_runtime_gets_the_minimal_set(self):
        self.assertEqual(environment.capabilities(ROOT, "unknown"), ["repo_search"])

    def test_declared_runtime_gets_its_declared_set(self):
        self.assertIn("native_skills", environment.capabilities(ROOT, "claude-code"))

    def test_undeclared_runtime_falls_back_to_unknown(self):
        self.assertEqual(
            environment.capabilities(ROOT, "some-new-agent"),
            environment.capabilities(ROOT, "unknown"),
        )


class TestFingerprint(unittest.TestCase):
    def test_is_stable_across_calls(self):
        self.assertEqual(
            environment.contract_fingerprint(ROOT), environment.contract_fingerprint(ROOT)
        )

    def test_changes_when_a_contract_file_changes(self):
        import shutil
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "repo"
            shutil.copytree(ROOT, copy, symlinks=True, ignore=shutil.ignore_patterns(".git"))
            before = environment.contract_fingerprint(copy)
            agents = copy / "AGENTS.md"
            agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
            self.assertNotEqual(before, environment.contract_fingerprint(copy))

    def test_is_independent_of_model_and_runtime(self):
        first = environment.build(ROOT, {"CLAUDECODE": "1"}, model="a")
        second = environment.build(ROOT, {}, model="b", runtime="codex")
        self.assertEqual(first.contract_fingerprint, second.contract_fingerprint)
        self.assertNotEqual(first.fingerprint, second.fingerprint)


class TestBuild(unittest.TestCase):
    def test_model_comes_from_the_environment_variable(self):
        built = environment.build(ROOT, {"AGENTIC_MODEL_ID": "claude-fable-5"})
        self.assertEqual(built.model_id, "claude-fable-5")

    def test_missing_model_is_recorded_as_unreported(self):
        self.assertEqual(environment.build(ROOT, {}).model_id, "unreported")


if __name__ == "__main__":
    unittest.main()
