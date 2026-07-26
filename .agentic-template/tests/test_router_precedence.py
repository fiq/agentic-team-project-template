import unittest

import _support  # noqa: F401
import router
import toon

CONFIG = toon.loads(open(_support.ROOT / ".agents/context/ROUTER.toon").read())

LEAN_OVERRIDE = {
    "match": {"model": "test-model", "runtime": "*"},
    "profile": "lean",
    "reason": "maintainer qualified",
    "expires": "2099-01-01",
}
GUARDED_OVERRIDE = {
    "match": {"model": "test-model", "runtime": "*"},
    "profile": "guarded",
    "reason": "unverified runtime",
    "expires": "2099-01-01",
}
EXPIRED_OVERRIDE = dict(LEAN_OVERRIDE, expires="2020-01-01")


def env(model="test-model", runtime="claude-code", fingerprint="fp-1"):
    return router.Environment(
        model_id=model,
        runtime=runtime,
        capabilities=["shell", "repo_search"],
        fingerprint=fingerprint,
    )


def task(risk="low", effort="standard"):
    return router.Task(risk=risk, effort=effort, skill_id="review-loop", paths=[])


def observation(result, escalated=None):
    return {"result": result, "escalated_profile": escalated}


def profile_for(overrides=(), obs=None, risk="low", effort="standard", model="test-model"):
    decision = router.resolve(env(model=model), task(risk, effort), CONFIG, list(overrides), obs)
    return decision.profile


class TestPrecedenceTable(unittest.TestCase):
    def test_01_override_beats_absent_qualification(self):
        self.assertEqual(profile_for([LEAN_OVERRIDE], None, "low"), "lean")

    def test_02_override_beats_failed_qualification(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("fail"), "normal"), "lean"
        )

    def test_03_risk_floor_applies_after_override(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("pass"), "high"), "guarded"
        )

    def test_04_irreversible_work_is_always_guarded(self):
        self.assertEqual(
            profile_for([LEAN_OVERRIDE], observation("pass"), "irreversible"), "guarded"
        )

    def test_05_guarded_override_raises(self):
        self.assertEqual(
            profile_for([GUARDED_OVERRIDE], observation("pass"), "low"), "guarded"
        )

    def test_06_expired_override_falls_through_to_qualification(self):
        self.assertEqual(
            profile_for([EXPIRED_OVERRIDE], observation("pass"), "low"), "lean"
        )

    def test_07_expired_override_without_qualification_is_standard(self):
        self.assertEqual(profile_for([EXPIRED_OVERRIDE], None, "low"), "standard")

    def test_08_qualification_pass_is_lean(self):
        self.assertEqual(profile_for([], observation("pass"), "low"), "lean")

    def test_09_qualification_fail_is_standard(self):
        self.assertEqual(profile_for([], observation("fail"), "low"), "standard")

    def test_10_qualification_uncertain_is_standard(self):
        self.assertEqual(profile_for([], observation("uncertain"), "low"), "standard")

    def test_12_normal_risk_floor_is_lean(self):
        self.assertEqual(profile_for([], observation("pass"), "normal"), "lean")

    def test_13_floor_raises_standard_to_guarded(self):
        self.assertEqual(profile_for([], observation("fail"), "high"), "guarded")

    def test_15_effort_never_changes_the_profile(self):
        for effort in ("minimal", "standard", "deep"):
            self.assertEqual(
                profile_for([], observation("pass"), "low", effort), "lean", effort
            )

    def test_17_degradation_escalation_is_a_floor(self):
        self.assertEqual(
            profile_for([], observation("pass", escalated="standard"), "low"), "standard"
        )

    def test_local_override_precedes_shared_override(self):
        # load_overrides puts local entries first; resolve takes the first match.
        self.assertEqual(
            profile_for([LEAN_OVERRIDE, GUARDED_OVERRIDE], None, "low"), "lean"
        )


class TestModelIdentityIsNotCapability(unittest.TestCase):
    def test_unknown_model_without_override_routes_identically(self):
        known = profile_for([], observation("pass"), "low", model="test-model")
        unknown = profile_for([], observation("pass"), "low", model="mystery-model-9")
        self.assertEqual(known, unknown)


class TestExplainability(unittest.TestCase):
    def test_every_precedence_step_appears_in_the_trace(self):
        decision = router.resolve(
            env(), task("high"), CONFIG, [LEAN_OVERRIDE], observation("pass")
        )
        self.assertEqual([step for step, _ in decision.trace], CONFIG["precedence"])

    def test_reasons_name_the_deciding_inputs(self):
        decision = router.resolve(env(), task("low"), CONFIG, [], None)
        joined = " ".join(decision.reasons)
        self.assertIn("no force override matched", joined)
        self.assertIn("uncertain", joined)


class TestConfigValidation(unittest.TestCase):
    def test_unknown_risk_is_rejected(self):
        with self.assertRaises(router.RouterError):
            router.resolve(
                env(),
                router.Task(risk="apocalyptic", effort="standard", skill_id=None, paths=[]),
                CONFIG,
                [],
                None,
            )

    def test_high_risk_floor_below_guarded_is_rejected(self):
        broken = dict(CONFIG, risk_floors=dict(CONFIG["risk_floors"], high="lean"))
        with self.assertRaises(router.RouterError):
            router.resolve(env(), task("high"), broken, [], None)


if __name__ == "__main__":
    unittest.main()
