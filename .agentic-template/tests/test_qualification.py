import subprocess
import unittest
from pathlib import Path

import _support  # noqa: F401
import environment
import qualification
import toon

ROOT = _support.ROOT
FIXTURE = ROOT / ".agentic-template/fixtures/qualification-repo"


def correct_answers():
    return {
        "answers": {
            "qualification_version": 1,
            "probes": [
                {"id": "contract_read", "sha": environment.file_digest(FIXTURE / "AGENTS.md")},
                {
                    "id": "catalog_resolve",
                    "path": "workflow/release-gate/SKILL.md",
                    "source": ".agents/skills/CATALOG.toon",
                },
                {"id": "facade_usage", "command": "bin/project check"},
                {"id": "progressive_disclosure", "files": ".agents/skills/CATALOG.toon"},
                {"id": "stop_condition", "token": "stop_and_request_authorisation"},
                {
                    "id": "evidence_grounding",
                    "command": "bin/project contract-test",
                    "source": "specs/capabilities/CAP-001-checkout.toon",
                },
                {
                    "id": "recovery",
                    "path": "workflow/release-gate/SKILL.md",
                    "recovered_from": ".agents/skills/CATALOG.toon",
                },
            ],
        }
    }


class TestPack(unittest.TestCase):
    def test_pack_lists_every_probe_and_its_version(self):
        pack = qualification.pack(ROOT)
        self.assertEqual(pack["version"], 1)
        self.assertEqual(len(pack["probes"]), 7)

    def test_rendered_pack_names_the_fixture_and_the_scoring_command(self):
        text = qualification.render_pack(qualification.pack(ROOT))
        self.assertIn("qualification-repo", text)
        self.assertIn("--score", text)


class TestScoring(unittest.TestCase):
    def test_correct_answers_pass(self):
        result = qualification.score(ROOT, correct_answers())
        self.assertEqual(result.result, "pass", result.notes)

    def test_wrong_contract_sha_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][0]["sha"] = "0" * 16
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "fail")
        self.assertEqual(result.probes["contract_read"], "fail")

    def test_guessed_skill_path_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][1]["path"] = "workflow/release/SKILL.md"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_ignored_stop_condition_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][4]["token"] = "edited the file"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_unresolvable_evidence_source_fails(self):
        answers = correct_answers()
        answers["answers"]["probes"][5]["source"] = "specs/capabilities/nope.toon"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_advisory_probe_failure_does_not_gate(self):
        answers = correct_answers()
        answers["answers"]["probes"][3]["files"] = "CATALOG.toon, verification.md"
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "pass")
        self.assertEqual(result.probes["progressive_disclosure"], "fail")

    def test_missing_probe_is_uncertain_not_failed(self):
        answers = correct_answers()
        answers["answers"]["probes"] = answers["answers"]["probes"][:3]
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "uncertain")

    def test_version_mismatch_is_uncertain(self):
        answers = correct_answers()
        answers["answers"]["qualification_version"] = 99
        self.assertEqual(qualification.score(ROOT, answers).result, "uncertain")


class TestCommand(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [str(_support.BIN / "project"), "context", "qualify", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_emitting_the_pack_is_non_mutating(self):
        before = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout)
        after = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        self.assertEqual(before, after)

    def test_scoring_without_record_writes_nothing(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".toon", delete=False) as handle:
            handle.write(toon.dumps(correct_answers()))
            path = handle.name
        before = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        result = self._run("--score", path)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("pass", result.stdout)
        after = sorted(p.name for p in (ROOT / ".agents/context/observations").iterdir())
        self.assertEqual(before, after)
        Path(path).unlink()

    def test_failing_score_exits_nonzero_and_names_the_probe(self):
        import tempfile

        answers = correct_answers()
        answers["answers"]["probes"][2]["command"] = "make check"
        with tempfile.NamedTemporaryFile("w", suffix=".toon", delete=False) as handle:
            handle.write(toon.dumps(answers))
            path = handle.name
        result = self._run("--score", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("facade_usage", result.stdout)
        Path(path).unlink()


if __name__ == "__main__":
    unittest.main()
