import unittest
from pathlib import Path

import _support
import environment
import observations
import router
import toon

CONFIG = toon.loads(open(_support.ROOT / ".agents/context/ROUTER.toon").read())


class ObservationTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = _support.temp_repo()
        for stale in (self.root / ".agents/context/observations").glob("*.toon"):
            stale.unlink()
        self.env = environment.build(self.root, {}, model="test-model", runtime="codex")

    def tearDown(self):
        self.tmp.cleanup()


class TestLookup(ObservationTestCase):
    def test_absent_when_nothing_recorded(self):
        found = observations.lookup(self.root, self.env)
        self.assertEqual(found.status, "absent")
        self.assertIsNone(found.observation)

    def test_current_after_recording(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        found = observations.lookup(self.root, self.env)
        self.assertEqual(found.status, "current")
        self.assertEqual(found.observation["result"], "pass")

    def test_invalidated_when_the_contract_changes(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        moved = environment.build(self.root, {}, model="test-model", runtime="codex")
        found = observations.lookup(self.root, moved)
        self.assertEqual(found.status, "invalidated")
        self.assertIsNone(found.observation)
        self.assertIn("AGENTS.md", found.stale_reason)

    def test_invalidated_observation_routes_to_standard(self):
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        moved = environment.build(self.root, {}, model="test-model", runtime="codex")
        found = observations.lookup(self.root, moved)
        decision = router.resolve(
            moved,
            router.Task(risk="low", effort="standard", skill_id=None, paths=[]),
            CONFIG,
            [],
            found.observation,
        )
        self.assertEqual(decision.profile, "standard")


class TestDegradationLadder(ObservationTestCase):
    def setUp(self):
        super().setUp()
        observations.record_qualification(self.root, self.env, "pass", {}, "2026-07-26")

    def test_first_degradation_recovers_before_escalating(self):
        outcome = observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        self.assertEqual(outcome.action, "recover_and_retry")
        self.assertEqual(outcome.reload_source, ".agents/skills/CATALOG.toon")
        self.assertIsNone(outcome.escalated_profile)
        self.assertIsNone(
            observations.lookup(self.root, self.env).observation["escalated_profile"]
        )

    def test_second_degradation_escalates_exactly_one_step(self):
        observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        outcome = observations.record_event(
            self.root, self.env, "degraded", "skill_path_wrong", CONFIG, "lean"
        )
        self.assertEqual(outcome.action, "escalate")
        self.assertEqual(outcome.escalated_profile, "standard")

    def test_escalation_stops_at_guarded(self):
        for _ in range(8):
            observations.record_event(
                self.root, self.env, "degraded", "unknown", CONFIG, "guarded"
            )
        self.assertEqual(
            observations.lookup(self.root, self.env).observation["escalated_profile"],
            "guarded",
        )

    def test_reduction_needs_the_configured_run_of_successes(self):
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        needed = CONFIG["degradation"]["reduce_after_successes"]
        for index in range(needed - 1):
            outcome = observations.record_event(
                self.root, self.env, "success", None, CONFIG, "standard"
            )
            self.assertEqual(outcome.action, "recorded", f"success {index + 1}")
        outcome = observations.record_event(
            self.root, self.env, "success", None, CONFIG, "standard"
        )
        self.assertEqual(outcome.action, "reduced")
        self.assertIsNone(outcome.escalated_profile)

    def test_reduction_is_refused_while_qualification_is_not_passing(self):
        observations.record_qualification(self.root, self.env, "fail", {}, "2026-07-26")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        for _ in range(CONFIG["degradation"]["reduce_after_successes"] + 2):
            outcome = observations.record_event(
                self.root, self.env, "success", None, CONFIG, "standard"
            )
        self.assertEqual(outcome.action, "recorded")

    def test_recorded_file_is_valid_toon(self):
        observations.record_event(self.root, self.env, "degraded", "unknown", CONFIG, "lean")
        path = observations.path_for(self.root, self.env)
        data = toon.loads(path.read_text())
        self.assertEqual(data["observation"]["model_id"], "test-model")
        self.assertEqual(data["observation"]["runtime"], "codex")


class TestRecoverySource(ObservationTestCase):
    def test_known_symptom_maps_to_its_source(self):
        self.assertEqual(
            observations.recovery_source(self.root, "verification_inadequate"),
            "docs/validation.md",
        )

    def test_unknown_symptom_falls_back_to_the_contract(self):
        self.assertEqual(
            observations.recovery_source(self.root, "something-new"), "AGENTS.md"
        )


if __name__ == "__main__":
    unittest.main()
