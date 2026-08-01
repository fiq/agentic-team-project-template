import unittest

import _support
import environment
import observations
import plan
import router
import skills
import toon

ROOT = _support.ROOT
CONFIG = toon.loads(open(ROOT / ".agents/context/ROUTER.toon").read())

ALL_LAYERS = ("core", "procedure", "verification", "examples", "failure_modes", "references")
FIXTURE_VERIFICATION = ["fixture-verify-a", "fixture-verify-b"]


class TestRiskClassification(unittest.TestCase):
    def test_explicit_flag_wins(self):
        self.assertEqual(plan.classify_risk(ROOT, ["docs/a.md"], "high"), ("high", "flag"))

    def test_no_paths_uses_the_configured_default(self):
        self.assertEqual(plan.classify_risk(ROOT, [], None), ("normal", "default"))

    def test_capability_spec_is_high_risk(self):
        risk, source = plan.classify_risk(ROOT, ["specs/capabilities/CAP-001.toon"], None)
        self.assertEqual(risk, "high")
        self.assertIn("released_capability", source)

    def test_documentation_is_low_risk(self):
        risk, _ = plan.classify_risk(ROOT, ["docs/wiki/index.md"], None)
        self.assertEqual(risk, "low")

    def test_highest_risk_across_touched_paths_wins(self):
        risk, source = plan.classify_risk(
            ROOT, ["docs/wiki/index.md", "compose.yaml"], None
        )
        self.assertEqual(risk, "high")
        self.assertIn("infrastructure", source)

    def test_unmatched_path_uses_the_default(self):
        risk, _ = plan.classify_risk(ROOT, ["src/whatever.rs"], None)
        self.assertEqual(risk, "normal")


class LayerTestCase(unittest.TestCase):
    """Plans are built against a synthetic fully-layered skill.

    Using a fixture rather than a real skill keeps these assertions stable when
    real skills gain or lose a layer, and lets one skill exercise every layer.
    """

    def setUp(self):
        self.tmp, self.root = _support.temp_repo()
        _support.write_skill(
            self.root,
            "workflow/fixture-skill",
            layers=ALL_LAYERS,
            verification=FIXTURE_VERIFICATION,
            trigger="fixture_skill_needed",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def document_for(self, qualification="pass", risk="low", effort="standard"):
        env = environment.build(self.root, {}, model="test-model", runtime="codex")
        skill = skills.resolve(self.root, skill_id="fixture_skill")
        task = router.Task(risk=risk, effort=effort, skill_id=skill.id, paths=[])
        lookup = observations.Lookup(
            {"result": qualification, "escalated_profile": None}, "current", None
        )
        decision = router.resolve(env, task, CONFIG, [], lookup.observation)
        return plan.build(self.root, env, task, CONFIG, decision, skill, lookup)["context_plan"]

    def skill_layers(self, document):
        return {entry["layer"] for entry in document["preload"] if entry.get("skill")}


class TestProfileSelectsLayers(LayerTestCase):
    def test_lean_preloads_only_the_summary_layer(self):
        document = self.document_for("pass", risk="low")
        self.assertEqual(document["decision"]["profile"], "lean")
        self.assertEqual(self.skill_layers(document), {"summary"})

    def test_standard_adds_the_core_layer(self):
        document = self.document_for("fail", risk="low")
        self.assertEqual(self.skill_layers(document), {"summary", "core"})

    def test_guarded_adds_procedure_verification_and_failure_modes(self):
        document = self.document_for("pass", risk="high")
        self.assertEqual(
            self.skill_layers(document),
            {"summary", "core", "procedure", "verification", "failure_modes"},
        )

    def test_examples_and_references_are_never_preloaded(self):
        for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high")):
            layers = self.skill_layers(self.document_for(qualification, risk=risk))
            with self.subTest(risk=risk):
                self.assertNotIn("examples", layers)
                self.assertNotIn("references", layers)

    def test_deferred_layers_are_the_complement_of_preloaded_ones(self):
        document = self.document_for("fail", risk="low")
        preloaded = self.skill_layers(document)
        deferred = {entry["layer"] for entry in document["defer"]}
        self.assertEqual(preloaded & deferred, set())
        skill = skills.resolve(self.root, skill_id="fixture_skill")
        self.assertEqual(preloaded | deferred, set(skill.layers))

    def test_a_skill_without_a_layer_never_reports_it(self):
        _support.write_skill(
            self.root, "workflow/thin-skill", layers=("core",), trigger="thin_skill_needed"
        )
        env = environment.build(self.root, {}, model="test-model", runtime="codex")
        skill = skills.resolve(self.root, skill_id="thin_skill")
        task = router.Task(risk="high", effort="standard", skill_id=skill.id, paths=[])
        decision = router.resolve(env, task, CONFIG, [], {"result": "pass"})
        document = plan.build(
            self.root, env, task, CONFIG, decision, skill,
            observations.Lookup({"result": "pass"}, "current", None),
        )["context_plan"]
        self.assertEqual(self.skill_layers(document), {"summary", "core"})
        self.assertEqual(document["defer"], [])


class TestRoutingNeverChangesOutcomes(LayerTestCase):
    def test_required_verification_is_identical_in_every_profile(self):
        required = [
            self.document_for(qualification, risk=risk)["verification"]["required"]
            for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high"))
        ]
        self.assertEqual(required[0], FIXTURE_VERIFICATION)
        self.assertEqual(required[0], required[1])
        self.assertEqual(required[1], required[2])

    def test_effort_changes_directives_but_not_the_profile_or_verification(self):
        light = self.document_for("pass", effort="minimal")
        deep = self.document_for("pass", effort="deep")
        self.assertEqual(light["decision"]["profile"], deep["decision"]["profile"])
        self.assertEqual(light["verification"], deep["verification"])
        self.assertNotEqual(light["effort_directives"], deep["effort_directives"])

    def test_recovery_map_is_identical_in_every_profile(self):
        maps = [
            self.document_for(qualification, risk=risk)["recovery"]
            for qualification, risk in (("pass", "low"), ("fail", "low"), ("pass", "high"))
        ]
        self.assertTrue(maps[0])
        self.assertEqual(maps[0], maps[1])
        self.assertEqual(maps[1], maps[2])


class TestProvenanceAndShape(LayerTestCase):
    def test_every_preloaded_source_carries_a_digest(self):
        for entry in self.document_for("pass")["preload"]:
            with self.subTest(source=entry["source"]):
                self.assertRegex(entry["sha"], r"^[0-9a-f]{16}$")

    def test_plan_renders_as_parseable_toon_with_all_sections(self):
        document = self.document_for("pass")
        parsed = toon.loads(plan.render_toon({"context_plan": document}))["context_plan"]
        for section in (
            "decision",
            "environment",
            "task",
            "preload",
            "defer",
            "verification",
            "recovery",
            "effort_directives",
        ):
            self.assertIn(section, parsed)

    def test_text_rendering_states_the_profile_and_reasons(self):
        text = plan.render_text({"context_plan": self.document_for("pass")})
        self.assertIn("PROFILE", text)
        self.assertIn("lean", text)
        self.assertIn("qualification result is pass", text)

    def test_plan_round_trips_with_an_all_digit_digest(self):
        document = self.document_for("pass")
        document["preload"][0]["sha"] = "0123456789012345"
        parsed = toon.loads(plan.render_toon({"context_plan": document}))["context_plan"]
        self.assertEqual(parsed["preload"][0]["sha"], "0123456789012345")


class TestCommandSurface(unittest.TestCase):
    def _run(self, *args):
        import subprocess

        return subprocess.run(
            [str(_support.BIN / "project"), "context", *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

    def test_explain_exits_zero_and_names_a_profile(self):
        result = self._run("explain", "--skill", "review_loop", "--risk", "low")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PROFILE", result.stdout)

    def test_toon_output_parses(self):
        result = self._run("explain", "--skill", "review_loop", "--format", "toon")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("context_plan", toon.loads(result.stdout))

    def test_invalid_risk_is_rejected_with_the_valid_values(self):
        result = self._run("explain", "--risk", "apocalyptic")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("irreversible", result.stdout)

    def test_unknown_skill_points_at_the_catalog(self):
        result = self._run("explain", "--skill", "no-such-skill")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CATALOG.toon", result.stdout)

    def test_help_lists_the_registered_subcommands(self):
        result = self._run("--help")
        self.assertEqual(result.returncode, 0, result.stdout)
        for name in ("explain", "observe"):
            self.assertIn(name, result.stdout)


if __name__ == "__main__":
    unittest.main()
