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
    """Build a correct answers document the same way scoring derives its expectations.

    Nothing here is hard-coded from the scoring config: every expected value is
    read from the fixture through the same `qualification._derive` the scorer
    itself uses, so this fixture cannot reintroduce the answer-key leak the
    scoring config was rewritten to close.
    """
    catalog_path = qualification._derive(
        FIXTURE, None, "catalog_path_for_trigger", "release_gate_required"
    )
    validation_command = qualification._derive(
        FIXTURE, None, "toon_value", "contract.toon#contract.validation_command"
    )
    stop_token = qualification._derive(
        FIXTURE, None, "toon_value", "contract.toon#contract.stop_token"
    )
    acceptance_command = qualification._derive(
        FIXTURE,
        None,
        "toon_value",
        "specs/capabilities/CAP-001-checkout.toon#capability.acceptance_command",
    )
    return {
        "answers": {
            "qualification_version": 1,
            "probes": [
                {"id": "contract_read", "sha": environment.file_digest(FIXTURE / "AGENTS.md")},
                {
                    "id": "catalog_resolve",
                    "path": catalog_path,
                    "source": ".agents/skills/CATALOG.toon",
                },
                {"id": "facade_usage", "command": validation_command},
                {"id": "progressive_disclosure", "files": ".agents/skills/CATALOG.toon"},
                {"id": "stop_condition", "token": stop_token},
                {
                    "id": "evidence_grounding",
                    "command": acceptance_command,
                    "source": "specs/capabilities/CAP-001-checkout.toon",
                },
                {
                    "id": "recovery",
                    "path": catalog_path,
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

    def test_answers_built_from_the_scoring_config_alone_do_not_pass(self):
        # The scoring config must contain pointers, not answers.
        contract = toon.loads((ROOT / qualification.CONTRACT).read_text())
        for probe in contract["probes"]:
            if probe["gating"]:
                with self.subTest(probe=probe["id"]):
                    self.assertNotIn("value", probe)

    def test_evidence_grounding_rejects_a_real_but_wrong_source(self):
        answers = correct_answers()
        for entry in answers["answers"]["probes"]:
            if entry["id"] == "evidence_grounding":
                entry["source"] = "AGENTS.md"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_recovery_rejects_an_unsourced_claim(self):
        answers = correct_answers()
        for entry in answers["answers"]["probes"]:
            if entry["id"] == "recovery":
                entry["recovered_from"] = "I did not actually reload CATALOG.toon"
        self.assertEqual(qualification.score(ROOT, answers).result, "fail")

    def test_a_demonstrated_failure_outranks_an_omission(self):
        answers = correct_answers()
        probes = answers["answers"]["probes"]
        for entry in probes:
            if entry["id"] == "facade_usage":
                entry["command"] = "make check"
        answers["answers"]["probes"] = [e for e in probes if e["id"] != "stop_condition"]
        result = qualification.score(ROOT, answers)
        self.assertEqual(result.result, "fail")
        self.assertEqual(result.probes["facade_usage"], "fail")


class TestAnswerKeyDoesNotLeak(unittest.TestCase):
    """The reviewer built a passing answer set purely from QUALIFICATION.toon's
    `value:` fields, without ever touching the fixture. Prove that attack no
    longer works: build the most generous answer set derivable from the
    scoring config and the answers schema alone, and confirm it cannot pass.
    """

    def test_config_only_answers_cannot_pass(self):
        contract = toon.loads((ROOT / qualification.CONTRACT).read_text())
        attacker_answers = {"answers": {"qualification_version": contract["version"], "probes": []}}
        for probe in contract["probes"]:
            entry = {"id": probe["id"]}
            # The only literal string exposed for a derived probe is `source`,
            # which is a pointer (a trigger id or a "file#key" path), not an
            # answer. An attacker with no fixture access can at best echo it
            # back into the answer field -- this must still fail or leave the
            # probe unanswered, never pass.
            if "source" in probe:
                entry[probe["field"]] = str(probe["source"])
            elif "value" in probe:
                entry[probe["field"]] = str(probe["value"])
            attacker_answers["answers"]["probes"].append(entry)
        result = qualification.score(ROOT, attacker_answers)
        self.assertIn(result.result, ("fail", "uncertain"))
        self.assertNotEqual(result.result, "pass")


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

    def test_unparseable_answers_file_reports_uncertain_not_a_traceback(self):
        import tempfile

        with tempfile.NamedTemporaryFile("w", suffix=".toon", delete=False) as handle:
            # A leading tab is rejected by toon.loads with a ToonError; this is
            # not valid input under any interpretation, unlike a merely wrong
            # answer.
            handle.write("\tqualification_version: 1\n")
            path = handle.name
        result = self._run("--score", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("uncertain", result.stdout)
        self.assertNotIn("Traceback", result.stdout)
        Path(path).unlink()

    def test_missing_answers_file_reports_uncertain_not_a_traceback(self):
        result = self._run("--score", "/nonexistent/answers.toon")
        self.assertEqual(result.returncode, 1)
        self.assertIn("uncertain", result.stdout)
        self.assertNotIn("Traceback", result.stdout)


if __name__ == "__main__":
    unittest.main()
