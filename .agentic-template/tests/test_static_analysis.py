"""Tests for the static-analysis skill and CI pipeline shape."""
import unittest

import _support  # noqa: F401

ROOT = _support.ROOT


class TestStaticAnalysisSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter, "frontmatter missing name")
        self.assertIn("description:", frontmatter, "frontmatter missing description")

    def test_skill_mentions_required_categories(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        for category in ("lint", "type_check", "sast", "dependency_scan", "complexity", "dast"):
            with self.subTest(category=category):
                self.assertIn(category, text, f"skill missing category: {category}")

    def test_skill_mentions_pre_commit_hook(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertIn("pre-commit", text.lower(), "skill missing pre-commit hook guidance")

    def test_skill_mentions_deprecation_revisit(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertIn("revisit_trigger", text, "skill missing revisit_trigger guidance")
        self.assertIn("deprecat", text.lower(), "skill missing deprecation guidance")


class TestCatalogEntry(unittest.TestCase):
    def test_static_analysis_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/static-analysis/SKILL.md", catalog)


class TestCheckRepoContract(unittest.TestCase):
    def test_static_analysis_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/static-analysis", text)

    def test_lint_in_project_commands(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("lint", text)


class TestProjectDispatch(unittest.TestCase):
    def test_lint_in_unspecialised_set(self):
        text = (ROOT / ".agentic-template/bin/project").read_text()
        self.assertIn('"lint"', text)


class TestCISkill(unittest.TestCase):
    def test_ci_skill_mentions_lint(self):
        path = ROOT / ".agents/skills/specialise/ci/SKILL.md"
        text = path.read_text()
        self.assertIn("project lint", text, "CI skill does not mention project lint")

    def test_ci_skill_mentions_parallel(self):
        path = ROOT / ".agents/skills/specialise/ci/SKILL.md"
        text = path.read_text()
        self.assertIn("parallel", text.lower(), "CI skill does not mention parallel execution")

    def test_ci_skill_references_static_analysis(self):
        path = ROOT / ".agents/skills/specialise/ci/SKILL.md"
        text = path.read_text()
        self.assertIn("static-analysis", text, "CI skill does not reference static-analysis skill")


class TestCustomizeContract(unittest.TestCase):
    def test_static_analysis_block_exists(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        self.assertIn("static_analysis:", text)

    def test_static_analysis_categories_present(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        for category in ("lint:", "type_check:", "sast:", "dependency_scan:", "complexity:", "dast:"):
            with self.subTest(category=category):
                self.assertIn(category, text)


class TestProjectProfile(unittest.TestCase):
    def test_static_analysis_decision_exists(self):
        text = (ROOT / "PROJECT_PROFILE.toon").read_text()
        self.assertIn("static_analysis_from_specialise", text)


class TestAgentsMd(unittest.TestCase):
    def test_agents_md_mentions_static_analysis(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("static analysis", text.lower())

    def test_agents_md_mentions_lint_command(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("project lint", text)

    def test_agents_md_mentions_acceptance_orthogonal(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("orthogonal", text.lower())

    def test_agents_md_mentions_right_framework(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("right framework", text.lower())


class TestAgentsTemplate(unittest.TestCase):
    def test_template_mentions_static_analysis(self):
        text = (ROOT / ".agentic-template/templates/AGENTS_TEMPLATE.md").read_text()
        self.assertIn("Static analysis", text)


class TestBuildPipelineSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/build-pipeline/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/build-pipeline/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter, "frontmatter missing name")
        self.assertIn("description:", frontmatter, "frontmatter missing description")

    def test_skill_mentions_nix_first(self):
        path = ROOT / ".agents/skills/specialise/build-pipeline/SKILL.md"
        text = path.read_text()
        self.assertIn("nix", text.lower())
        self.assertIn("reproducib", text.lower())

    def test_skill_mentions_evolvable_targets(self):
        path = ROOT / ".agents/skills/specialise/build-pipeline/SKILL.md"
        text = path.read_text()
        self.assertIn("evolvable", text.lower())
        self.assertIn("revisit_trigger", text)


class TestBuildPipelineWiring(unittest.TestCase):
    def test_build_pipeline_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/build-pipeline/SKILL.md", catalog)

    def test_build_pipeline_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/build-pipeline", text)

    def test_build_in_project_commands(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("build", text)

    def test_build_in_unspecialised_set(self):
        text = (ROOT / ".agentic-template/bin/project").read_text()
        self.assertIn('"build"', text)

    def test_ci_skill_mentions_build(self):
        path = ROOT / ".agents/skills/specialise/ci/SKILL.md"
        text = path.read_text()
        self.assertIn("project build", text)

    def test_container_build_references_build_pipeline(self):
        path = ROOT / ".agents/skills/specialise/container-build/SKILL.md"
        text = path.read_text()
        self.assertIn("build-pipeline", text)

    def test_customize_has_build_command(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        self.assertIn("build: specialise", text)

    def test_profile_has_build_decision(self):
        text = (ROOT / "PROJECT_PROFILE.toon").read_text()
        self.assertIn("nix_first_build_pipeline", text)

    def test_agents_md_mentions_build(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("project build", text)


class TestDeploymentPipelineSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/deployment-pipeline/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/deployment-pipeline/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_skill_mentions_evolvable_targets(self):
        path = ROOT / ".agents/skills/specialise/deployment-pipeline/SKILL.md"
        text = path.read_text()
        self.assertIn("evolvable", text.lower())
        self.assertIn("revisit_trigger", text)

    def test_skill_mentions_promotion(self):
        path = ROOT / ".agents/skills/specialise/deployment-pipeline/SKILL.md"
        text = path.read_text()
        self.assertIn("promotion", text.lower())


class TestDeploymentPipelineWiring(unittest.TestCase):
    def test_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/deployment-pipeline/SKILL.md", catalog)

    def test_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/deployment-pipeline", text)

    def test_customize_has_deployment_block(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        self.assertIn("deployment:", text)

    def test_profile_has_deployment_decision(self):
        text = (ROOT / "PROJECT_PROFILE.toon").read_text()
        self.assertIn("deployment_pipeline_from_specialise", text)

    def test_infra_decision_references_deployment(self):
        text = (ROOT / ".agents/skills/specialise/infra-decision/SKILL.md").read_text()
        self.assertIn("deployment-pipeline", text)


class TestObservabilitySkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/observability/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/observability/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_skill_mentions_otel(self):
        path = ROOT / ".agents/skills/specialise/observability/SKILL.md"
        text = path.read_text()
        self.assertIn("otel", text.lower())

    def test_skill_mentions_local_instrumentation(self):
        path = ROOT / ".agents/skills/specialise/observability/SKILL.md"
        text = path.read_text()
        self.assertIn("local", text.lower())


class TestObservabilityWiring(unittest.TestCase):
    def test_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/observability/SKILL.md", catalog)

    def test_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/observability", text)

    def test_customize_has_observability_block(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        self.assertIn("observability:", text)

    def test_profile_has_observability_decision(self):
        text = (ROOT / "PROJECT_PROFILE.toon").read_text()
        self.assertIn("observability_from_specialise", text)

    def test_operations_md_mentions_observability(self):
        text = (ROOT / "docs/wiki/product/operations.md").read_text()
        self.assertIn("Observability", text)


class TestBudgetAndShiftLeft(unittest.TestCase):
    def test_customize_has_budget_block(self):
        text = (ROOT / "CUSTOMIZE_THIS_PROJECT.toon").read_text()
        self.assertIn("budget:", text)
        self.assertIn("appetite:", text)

    def test_profile_has_budget_block(self):
        text = (ROOT / "PROJECT_PROFILE.toon").read_text()
        self.assertIn("budget:", text)
        self.assertIn("appetite:", text)

    def test_agents_md_has_shift_left_section(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("Shift-left engineering", text)

    def test_agents_md_mentions_budget_appetite(self):
        text = (ROOT / "AGENTS.md").read_text()
        self.assertIn("constrained", text)
        self.assertIn("generous", text)

    def test_glossary_has_budget_term(self):
        text = (ROOT / "docs/wiki/method/glossary.md").read_text()
        self.assertIn("Budget appetite", text)

    def test_glossary_has_observability_term(self):
        text = (ROOT / "docs/wiki/method/glossary.md").read_text()
        self.assertIn("Observability 2.0", text)

    def test_glossary_has_deployment_pipeline_term(self):
        text = (ROOT / "docs/wiki/method/glossary.md").read_text()
        self.assertIn("Deployment pipeline", text)


class TestWikiPages(unittest.TestCase):
    def test_testing_md_mentions_static_analysis(self):
        text = (ROOT / "docs/wiki/method/testing.md").read_text()
        self.assertIn("Static analysis", text)
        self.assertIn("shift-left", text.lower())

    def test_testing_md_mentions_orthogonal(self):
        text = (ROOT / "docs/wiki/method/testing.md").read_text()
        self.assertIn("orthogonal", text.lower())

    def test_development_md_mentions_lint(self):
        text = (ROOT / "docs/wiki/method/development.md").read_text()
        self.assertIn("project lint", text)

    def test_glossary_has_new_terms(self):
        text = (ROOT / "docs/wiki/method/glossary.md").read_text()
        for term in ("Static analysis", "Shift-left", "Lint gate", "Complexity budget"):
            with self.subTest(term=term):
                self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
