import subprocess
import unittest

import _support

ROOT = _support.ROOT


def run_check(cwd):
    return subprocess.run(
        [str(_support.BIN / "project"), "context", "check"],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


class CheckTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp, self.root = _support.temp_repo()

    def tearDown(self):
        self.tmp.cleanup()

    def add_topic(self, topic_id, canonical, marker):
        """Register an enforced topic and plant its marker in the canonical file."""
        canonical_path = self.root / canonical
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_path.write_text(
            canonical_path.read_text() if canonical_path.exists() else "# Canonical\n"
        )
        canonical_path.write_text(canonical_path.read_text() + f"\n{marker}.\n")
        topics = self.root / ".agents/context/TOPICS.toon"
        topics.write_text(
            topics.read_text().replace(
                "topics: []",
                "topics:\n"
                f"  - id: {topic_id}\n"
                f"    canonical: {canonical}\n"
                f"    marker: {marker}\n",
                1,
            )
        )


class TestBaseline(unittest.TestCase):
    def test_template_passes(self):
        result = run_check(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("CONTEXT ROUTER OK", result.stdout)

    def test_known_duplications_are_reported_as_warnings(self):
        result = run_check(ROOT)
        self.assertIn("warning", result.stdout.lower())
        self.assertIn("D1", result.stdout)


class TestTaxonomyValidation(CheckTestCase):
    def test_uncatalogued_skill_fails(self):
        target = self.root / ".agents/skills/workflow/orphan/SKILL.md"
        target.parent.mkdir(parents=True)
        target.write_text("---\nname: orphan\ndescription: Not in the catalog.\n---\n\n# Orphan\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow/orphan/SKILL.md", result.stdout)
        self.assertIn("CATALOG.toon", result.stdout)

    def test_catalog_entry_without_a_file_fails(self):
        catalog = self.root / ".agents/skills/CATALOG.toon"
        catalog.write_text(
            catalog.read_text() + "\n  ghost:\n    path: workflow/ghost/SKILL.md\n    trigger: never\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow/ghost/SKILL.md", result.stdout)

    def test_empty_layer_file_fails(self):
        directory = self.root / ".agents/skills/workflow/review-loop"
        (directory / "core.md").write_text("\n\n")
        skill_file = directory / "SKILL.md"
        skill_file.write_text(
            skill_file.read_text().replace(
                "---\n\n# Review Loop", "layers:\n  core: core.md\n---\n\n# Review Loop", 1
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("empty", result.stdout.lower())

    def test_undeclared_layer_file_on_disk_fails(self):
        (self.root / ".agents/skills/workflow/review-loop/procedure.md").write_text(
            "# Stray procedure layer\n\nNot declared in frontmatter.\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("procedure.md", result.stdout)

    def test_unknown_layer_name_fails(self):
        skill_file = self.root / ".agents/skills/workflow/review-loop/SKILL.md"
        skill_file.write_text(
            skill_file.read_text().replace(
                "---\n\n# Review Loop", "layers:\n  epilogue: epilogue.md\n---\n\n# Review Loop", 1
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("epilogue", result.stdout)

    def test_catalog_entry_without_a_trigger_fails(self):
        catalog = self.root / ".agents/skills/CATALOG.toon"
        catalog.write_text(
            catalog.read_text()
            + "\n  triggerless:\n    path: workflow/review-loop/SKILL.md\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("triggerless", result.stdout)
        self.assertIn("declares no trigger", result.stdout)

    def test_declared_layer_file_missing_fails(self):
        skill_file = self.root / ".agents/skills/workflow/review-loop/SKILL.md"
        skill_file.write_text(
            skill_file.read_text().replace(
                "---\n\n# Review Loop",
                "layers:\n  verification: verification.md\n---\n\n# Review Loop",
                1,
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("workflow/review-loop/SKILL.md", result.stdout)
        self.assertIn("verification.md", result.stdout)


class TestCanonicalSourceUniqueness(CheckTestCase):
    MARKER = "This synthetic sentence has exactly one canonical home"
    CANONICAL = "docs/synthetic-canonical.md"

    def test_a_single_homed_topic_passes(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        result = run_check(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_duplicated_marker_fails_and_names_both_files(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        stray = self.root / "docs/wiki/development.md"
        stray.write_text(stray.read_text() + f"\n\n{self.MARKER}.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)
        self.assertIn("docs/wiki/development.md", result.stdout)

    def test_marker_matching_ignores_case(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        stray = self.root / "docs/wiki/development.md"
        stray.write_text(stray.read_text() + f"\n\n{self.MARKER.lower()}.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)

    def test_marker_absent_from_its_canonical_home_fails(self):
        self.add_topic("synthetic_topic", self.CANONICAL, self.MARKER)
        canonical = self.root / self.CANONICAL
        canonical.write_text("# Canonical\n\nThe marker was removed.\n")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("synthetic_topic", result.stdout)

    def test_short_marker_is_rejected_as_unreliable(self):
        self.add_topic("synthetic_topic", self.CANONICAL, "too short")
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("20 characters", result.stdout)

    def test_canonical_home_under_an_excluded_directory_is_still_found(self):
        # Excluding a directory from the duplicate scan must not make a marker
        # living there report as absent from its own home.
        self.add_topic(
            "excluded_home_topic",
            ".agents/context/RECOVERY.toon",
            "This synthetic marker lives in an excluded configuration directory",
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 0, result.stdout)


class TestRouterConfigValidation(CheckTestCase):
    def test_duplicate_trigger_fails(self):
        catalog = self.root / ".agents/skills/CATALOG.toon"
        catalog.write_text(
            catalog.read_text()
            + "\n  shadow_skill:\n    path: workflow/review-loop/SKILL.md\n"
            "    trigger: before_merge_or_boy_scout_cleanup\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("share trigger", result.stdout)

    def test_declared_defer_layers_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(
            config.read_text().replace(
                "    preload_layers: [summary]",
                "    preload_layers: [summary]\n    defer_layers: [core]",
                1,
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("defer_layers", result.stdout)

    def test_profile_missing_from_the_order_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(config.read_text().replace(
            "order: [lean, standard, guarded]", "order: [lean, standard, guarded, feral]"
        ))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("feral", result.stdout)

    def test_profile_absent_from_order_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(
            config.read_text().replace(
                "\nrisk_floors:",
                "\n  feral:\n    preload_layers: [summary]\n    always_preload: []\n"
                "    independent_review: not_required\n\nrisk_floors:",
                1,
            )
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("feral", result.stdout)
        self.assertIn("absent from order", result.stdout)

    def test_high_risk_floor_below_guarded_fails(self):
        config = self.root / ".agents/context/ROUTER.toon"
        config.write_text(config.read_text().replace("  high: guarded", "  high: lean"))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("guarded", result.stdout)

    def test_override_without_a_reason_fails(self):
        override = self.root / ".agents/context/overrides.local.toon"
        override.write_text(
            "version: 1\noverrides:\n  - match:\n      model: x\n    profile: lean\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("reason", result.stdout)

    def test_override_with_an_unknown_profile_fails(self):
        override = self.root / ".agents/context/overrides.local.toon"
        override.write_text(
            "version: 1\noverrides:\n  - match:\n      model: x\n    profile: turbo\n"
            "    reason: testing\n    expires: 2099-01-01\n"
        )
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("turbo", result.stdout)


class TestFrontmatterValidation(CheckTestCase):
    def test_missing_required_field_fails(self):
        skill_file = self.root / ".agents/skills/workflow/review-loop/SKILL.md"
        skill_file.write_text(skill_file.read_text().replace("name: review-loop\n", "", 1))
        result = run_check(self.root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name", result.stdout)


class TestIntegrationWithProjectCheck(unittest.TestCase):
    def test_project_check_runs_the_router_check(self):
        result = subprocess.run(
            [str(_support.BIN / "project"), "check"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.assertIn("CONTEXT ROUTER", result.stdout)


if __name__ == "__main__":
    unittest.main()
