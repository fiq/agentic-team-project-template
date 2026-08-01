import unittest

import _support  # noqa: F401
import skills

ROOT = _support.ROOT


class TestFrontmatter(unittest.TestCase):
    def test_parses_metadata_and_returns_the_body(self):
        text = (
            "---\n"
            "name: review-loop\n"
            'description: "Cyclic clean-up: boy-scout and smells."\n'
            "id: SKILL-review-loop\n"
            "triggers: [before_merge, boy_scout_cleanup]\n"
            "default_task_risk: normal\n"
            "layers:\n"
            "  core: core.md\n"
            "---\n"
            "\n"
            "# Review Loop\n"
        )
        meta, body = skills.parse_frontmatter(text)
        self.assertEqual(meta["id"], "SKILL-review-loop")
        self.assertEqual(meta["description"], "Cyclic clean-up: boy-scout and smells.")
        self.assertEqual(meta["triggers"], ["before_merge", "boy_scout_cleanup"])
        self.assertEqual(meta["layers"], {"core": "core.md"})
        self.assertTrue(body.lstrip().startswith("# Review Loop"))

    def test_missing_frontmatter_is_an_error(self):
        with self.assertRaises(skills.SkillError):
            skills.parse_frontmatter("# No frontmatter\n")

    def test_colon_in_a_value_is_kept_as_text(self):
        meta, _ = skills.parse_frontmatter(
            "---\nname: a\ndescription: Route work: fast and cheap.\n---\n"
        )
        self.assertEqual(meta["description"], "Route work: fast and cheap.")

    def test_malformed_frontmatter_reports_how_to_fix_it(self):
        with self.assertRaises(skills.SkillError) as caught:
            skills.parse_frontmatter("---\nname: a\n   description: b\n---\n")
        message = str(caught.exception)
        self.assertIn("not parseable", message)
        self.assertIn("two-space", message)

    def test_bracket_leading_value_is_read_as_a_list_not_text(self):
        meta, _ = skills.parse_frontmatter(
            "---\nname: a\ndescription: [not, prose]\n---\n"
        )
        self.assertEqual(meta["description"], ["not", "prose"])


class TestCatalogResolution(unittest.TestCase):
    def test_every_skill_on_disk_is_in_the_catalog(self):
        catalogued = {entry["path"] for entry in skills.load_catalog(ROOT).values()}
        on_disk = {
            str(skill.path.relative_to(ROOT / ".agents/skills")) for skill in skills.all_skills(ROOT)
        }
        self.assertEqual(on_disk - catalogued, set(), "skills missing from CATALOG.toon")

    def test_every_catalog_path_exists(self):
        for skill_id, entry in skills.load_catalog(ROOT).items():
            with self.subTest(skill=skill_id):
                self.assertTrue((ROOT / ".agents/skills" / entry["path"]).exists())

    def test_resolves_by_id(self):
        found = skills.resolve(ROOT, skill_id="review_loop")
        self.assertTrue(str(found.path).endswith("workflow/review-loop/SKILL.md"))

    def test_resolves_by_trigger(self):
        found = skills.resolve(ROOT, trigger="before_merge_or_boy_scout_cleanup")
        self.assertEqual(found.id, "review_loop")

    def test_unknown_id_names_the_catalog_in_the_error(self):
        with self.assertRaises(skills.SkillError) as caught:
            skills.resolve(ROOT, skill_id="not-a-skill")
        self.assertIn("CATALOG.toon", str(caught.exception))


class TestLayerDiscovery(unittest.TestCase):
    def test_summary_layer_is_always_the_skill_file(self):
        found = skills.resolve(ROOT, skill_id="review_loop")
        self.assertTrue(found.layers["summary"].endswith("SKILL.md"))

    def test_only_existing_layer_files_are_reported(self):
        for skill in skills.all_skills(ROOT):
            for layer, relative in skill.layers.items():
                with self.subTest(skill=skill.id, layer=layer):
                    self.assertTrue((ROOT / relative).exists())

    def test_layer_names_stay_inside_the_taxonomy(self):
        for skill in skills.all_skills(ROOT):
            for layer in skill.layers:
                with self.subTest(skill=skill.id, layer=layer):
                    self.assertIn(layer, skills.LAYERS)


if __name__ == "__main__":
    unittest.main()
