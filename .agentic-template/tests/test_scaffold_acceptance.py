import filecmp
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import _support  # noqa: F401
import toon

ROOT = _support.ROOT
FIXTURE = ROOT / ".agentic-template/fixtures/generated-project"


def scaffold_into(target, apply=True):
    args = [str(_support.BIN / "project"), "context", "scaffold", "--into", str(target)]
    if apply:
        args.append("--apply")
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def project_run(target, *args):
    return subprocess.run(
        [str(target / ".agentic-template/bin/project"), "context", *args],
        cwd=target,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


class ScaffoldTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "generated"
        shutil.copytree(FIXTURE, self.project)

    def tearDown(self):
        self.tmp.cleanup()


class TestAC1Inheritance(ScaffoldTestCase):
    def test_dry_run_is_the_default_and_writes_nothing(self):
        result = scaffold_into(self.project, apply=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse((self.project / ".agents/context/ROUTER.toon").exists())
        self.assertIn("dry run", result.stdout.lower())

    def test_apply_copies_every_copy_kind_file_byte_identically(self):
        self.assertEqual(scaffold_into(self.project).returncode, 0)
        for relative in ("ROUTER.toon", "RECOVERY.toon", "runtimes.toon", "overrides.toon"):
            source = ROOT / ".agents/context" / relative
            target = self.project / ".agents/context" / relative
            with self.subTest(file=relative):
                self.assertTrue(target.exists())
                self.assertTrue(filecmp.cmp(source, target, shallow=False))

    def test_apply_installs_the_library_command_and_portable_tests(self):
        scaffold_into(self.project)
        for relative in (
            ".agentic-template/lib/router.py",
            ".agentic-template/bin/context",
            ".agentic-template/tests/test_router_precedence.py",
        ):
            with self.subTest(file=relative):
                self.assertTrue((self.project / relative).exists())

    def test_template_specific_tests_are_not_scaffolded(self):
        scaffold_into(self.project)
        self.assertFalse((self.project / ".agentic-template/tests/test_explain.py").exists())

    def test_starter_files_do_not_overwrite_project_versions(self):
        original = (self.project / ".agents/context/risk-rules.toon").read_text()
        scaffold_into(self.project)
        self.assertEqual((self.project / ".agents/context/risk-rules.toon").read_text(), original)

    def test_project_owned_files_are_never_touched(self):
        original = (self.project / ".agents/context/overrides.local.toon").read_text()
        scaffold_into(self.project)
        self.assertEqual(
            (self.project / ".agents/context/overrides.local.toon").read_text(), original
        )

    def test_scaffolded_command_is_executable(self):
        scaffold_into(self.project)
        result = project_run(self.project, "explain", "--skill", "ship_slice")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_reapplying_scaffold_to_an_unchanged_project_reports_no_updates(self):
        # Regression: the scaffold used to report every directory-kind entry
        # (the qualification fixture, the qualification config) as "update"
        # on every run without comparing contents, so an unmodified
        # re-scaffold falsely claimed changes.
        scaffold_into(self.project)
        result = scaffold_into(self.project, apply=False)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("update", result.stdout)


class TestAC2ProjectValidates(ScaffoldTestCase):
    def test_the_generated_project_passes_context_check(self):
        scaffold_into(self.project)
        result = project_run(self.project, "check")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CONTEXT ROUTER OK", result.stdout)

    def test_both_project_skills_are_layered_and_catalogued(self):
        catalog = toon.loads((self.project / ".agents/skills/CATALOG.toon").read_text())
        self.assertIn("ship_slice", catalog["skills"])
        self.assertIn("pricing_rules", catalog["skills"])


class TestAC3toAC5Profiles(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def _plan(self, *args):
        result = project_run(self.project, "explain", "--format", "toon", *args)
        self.assertEqual(result.returncode, 0, result.stdout)
        return toon.loads(result.stdout)["context_plan"]

    def _qualify(self):
        # Record a passing observation for the fixture environment.
        project_run(self.project, "observe", "--event", "success", "--model", "m1")
        path = next((self.project / ".agents/context/observations").glob("*.toon"))
        data = toon.loads(path.read_text())
        data["observation"]["result"] = "pass"
        path.write_text(toon.dumps(data))

    def test_ac3_lean_preloads_only_the_summary(self):
        self._qualify()
        plan = self._plan("--skill", "ship_slice", "--risk", "low", "--model", "m1")
        self.assertEqual(plan["decision"]["profile"], "lean")
        self.assertEqual(
            {e["layer"] for e in plan["preload"] if e.get("skill")}, {"summary"}
        )

    def test_ac4_standard_adds_core_and_defers_procedure(self):
        plan = self._plan("--skill", "ship_slice", "--risk", "low")
        self.assertEqual(plan["decision"]["profile"], "standard")
        self.assertIn("core", {e["layer"] for e in plan["preload"] if e.get("skill")})
        self.assertIn("procedure", {e["layer"] for e in plan["defer"]})

    def test_ac5_guarded_adds_procedure_verification_failure_modes_and_review(self):
        plan = self._plan("--skill", "ship_slice", "--risk", "high")
        self.assertEqual(plan["decision"]["profile"], "guarded")
        layers = {e["layer"] for e in plan["preload"] if e.get("skill")}
        self.assertTrue({"procedure", "verification", "failure_modes"} <= layers)
        self.assertNotEqual(plan["independent_review"], "not_required")


class TestAC6LocalOverride(ScaffoldTestCase):
    def test_local_override_selects_lean_and_names_its_file(self):
        scaffold_into(self.project)
        result = project_run(
            self.project, "explain", "--skill", "ship_slice", "--risk", "low",
            "--model", "fixture-qualified-model",
        )
        self.assertIn("lean", result.stdout)
        self.assertIn("overrides.local.toon", result.stdout)


class TestAC7andAC8Qualification(ScaffoldTestCase):
    def test_pack_and_scoring_run_inside_the_generated_project(self):
        scaffold_into(self.project)
        pack = project_run(self.project, "qualify")
        self.assertEqual(pack.returncode, 0, pack.stdout)
        self.assertIn("contract_read", pack.stdout)

    def test_wrong_contract_sha_fails_inside_the_generated_project(self):
        scaffold_into(self.project)
        answers = self.project / "answers.toon"
        answers.write_text(
            toon.dumps(
                {
                    "answers": {
                        "qualification_version": 1,
                        "probes": [{"id": "contract_read", "sha": "0" * 16}],
                    }
                }
            )
        )
        result = project_run(self.project, "qualify", "--score", str(answers))
        self.assertEqual(result.returncode, 1)


class TestAC9RiskFloorFromPaths(ScaffoldTestCase):
    def test_touching_a_published_rule_forces_guarded_without_a_flag(self):
        scaffold_into(self.project)
        result = project_run(
            self.project, "explain", "--skill", "pricing_rules",
            "--paths", "specs/capabilities/CAP-001-pricing.toon",
        )
        self.assertIn("guarded", result.stdout)
        self.assertIn("published_price_rule", result.stdout)


class TestAC10toAC12RecoveryAndInvalidation(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def test_ac10_first_degradation_reloads_the_authoritative_source(self):
        recorded = project_run(
            self.project, "observe", "--event", "degraded", "--symptom", "skill_path_wrong"
        )
        self.assertIn("CATALOG.toon", recorded.stdout)
        plan = project_run(self.project, "explain", "--skill", "ship_slice")
        self.assertIn("RECOVER FIRST", plan.stdout)
        self.assertIn("CATALOG.toon", plan.stdout)

    def test_ac11_second_degradation_escalates_one_step(self):
        project_run(self.project, "observe", "--event", "degraded", "--symptom", "unknown")
        second = project_run(
            self.project, "observe", "--event", "degraded", "--symptom", "unknown",
            "--profile", "lean",
        )
        self.assertIn("escalate", second.stdout)
        self.assertIn("standard", second.stdout)

    def test_ac12_editing_the_contract_invalidates_the_observation(self):
        project_run(self.project, "observe", "--event", "success")
        agents = self.project / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n<!-- drift -->\n")
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--risk", "low")
        self.assertIn("invalidated", result.stdout)
        self.assertIn("standard", result.stdout)


class TestAC13andAC14Explainability(ScaffoldTestCase):
    def setUp(self):
        super().setUp()
        scaffold_into(self.project)

    def test_ac13_toon_output_has_every_section(self):
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--format", "toon")
        plan = toon.loads(result.stdout)["context_plan"]
        for section in (
            "decision", "environment", "task", "preload", "defer",
            "verification", "recovery", "effort_directives",
        ):
            self.assertIn(section, plan)

    def test_ac14_required_verification_is_identical_across_profiles(self):
        required = []
        for risk in ("low", "normal", "high"):
            result = project_run(
                self.project, "explain", "--skill", "ship_slice", "--risk", risk, "--format", "toon"
            )
            required.append(toon.loads(result.stdout)["context_plan"]["verification"]["required"])
        self.assertEqual(required[0], required[1])
        self.assertEqual(required[1], required[2])
        self.assertTrue(required[0])

    def test_every_decision_states_its_reasons_and_precedence(self):
        result = project_run(self.project, "explain", "--skill", "ship_slice", "--format", "toon")
        decision = toon.loads(result.stdout)["context_plan"]["decision"]
        self.assertTrue(decision["reasons"])
        self.assertEqual(len(decision["precedence_applied"]), 5)


RUST_FIXTURE = ROOT / ".agentic-template/fixtures/rust-sample-project"


class RustFixtureTestCase(unittest.TestCase):
    """Scaffold the router into the synthetic Rust sample project.

    The fixture deliberately stresses the scaffold outside its comfort zone:
    a Rust runtime (not specialised by the template), no existing
    .agents/context/, an existing domain skill + catalog, and a wholly flat
    legacy wiki that must not be forced onto the axis layout.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "orbit"
        shutil.copytree(RUST_FIXTURE, self.project)

    def tearDown(self):
        self.tmp.cleanup()


class TestRustFixtureScaffold(RustFixtureTestCase):
    def test_scaffold_into_rust_project_passes_context_check(self):
        result = scaffold_into(self.project)
        self.assertEqual(result.returncode, 0, result.stdout)
        check = project_run(self.project, "check")
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertIn("CONTEXT ROUTER OK", check.stdout)

    def test_existing_catalog_is_merged_not_clobbered(self):
        scaffold_into(self.project)
        catalog = toon.loads((self.project / ".agents/skills/CATALOG.toon").read_text())
        self.assertIn("orbital_physics", catalog["skills"])
        self.assertIn("context_qualification", catalog["skills"])

    def test_domain_skill_layers_are_preserved(self):
        scaffold_into(self.project)
        for relative in (
            ".agents/skills/domain/orbital-physics/SKILL.md",
            ".agents/skills/domain/orbital-physics/core.md",
            ".agents/skills/domain/orbital-physics/failure-modes.md",
        ):
            with self.subTest(file=relative):
                self.assertTrue((self.project / relative).exists())

    def test_wholly_flat_legacy_wiki_does_not_fail_the_axis_check(self):
        # Pre-adoption state: no axis directories, so the layout is not
        # enforced at all. A project is never forced to adopt it.
        scaffold_into(self.project)
        self.assertTrue((self.project / "docs/wiki/operations.md").exists())
        check = project_run(self.project, "check")
        self.assertEqual(check.returncode, 0, check.stdout)
        self.assertIn("CONTEXT ROUTER OK", check.stdout)

    def test_adopting_the_axis_layout_requires_migrating_every_page(self):
        # Creating the first axis directory opts the project in, and the
        # remaining flat page must move too. Adoption is all-or-nothing:
        # tolerating a half-migrated tree would forfeit the check's real job
        # of catching a page later dropped in the wrong place.
        scaffold_into(self.project)
        migrated = self.project / "docs/wiki/product/architecture.md"
        migrated.parent.mkdir(parents=True, exist_ok=True)
        migrated.write_text("---\naxis: product\n---\n\n# Architecture\n")
        check = project_run(self.project, "check")
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn("operations.md", check.stdout)
        self.assertIn("migrating every page", check.stdout)

    def test_a_fully_migrated_wiki_passes(self):
        # The other side of the same rule: once every page has moved, the
        # check is satisfied.
        scaffold_into(self.project)
        wiki = self.project / "docs/wiki"
        (wiki / "product").mkdir(parents=True, exist_ok=True)
        (wiki / "product/operations.md").write_text(
            "---\naxis: product\n---\n\n# Operations\n"
        )
        (wiki / "operations.md").unlink()
        check = project_run(self.project, "check")
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_a_page_inside_an_axis_directory_must_declare_the_matching_axis(self):
        scaffold_into(self.project)
        bad = self.project / "docs/wiki/product/broken.md"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("---\naxis: method\n---\n\n# Wrong axis\n")
        check = project_run(self.project, "check")
        self.assertEqual(check.returncode, 1, check.stdout)
        self.assertIn("broken.md", check.stdout)

    def test_domain_skill_resolves_after_scaffold(self):
        scaffold_into(self.project)
        result = project_run(self.project, "explain", "--skill", "orbital_physics")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("standard", result.stdout)

    def test_rust_source_is_untouched(self):
        original = (self.project / "src/main.rs").read_text()
        scaffold_into(self.project)
        self.assertEqual((self.project / "src/main.rs").read_text(), original)


if __name__ == "__main__":
    unittest.main()
