"""Tests for the static-analysis skill, CI pipeline shape, and runtime skills."""
import subprocess
import tempfile
import unittest
from pathlib import Path

import _support  # noqa: F401

ROOT = _support.ROOT
BIN = _support.BIN

SPECIALISE = ROOT / ".agents/skills/specialise"

# Every runtime skill must carry these sections. The set is derived from the
# fullest existing skills (runtime-rust, runtime-go) and is what
# `init/SKILL.md` step 10 instructs an agent to write for a new runtime.
# Discovering the runtimes from disk rather than listing them here means a
# newly added runtime skill is held to the same bar automatically.
REQUIRED_RUNTIME_SECTIONS = (
    "## Build and tooling",
    "## Static analysis",
    "## Language smells",
    "## Testing",
    "## Ecosystem openness",
)


def discovered_runtime_skills():
    """Every specialise/runtime-* skill present on disk, by directory name."""
    return sorted(
        path.name
        for path in SPECIALISE.iterdir()
        if path.is_dir() and path.name.startswith("runtime-") and (path / "SKILL.md").exists()
    )


class TestEveryRuntimeSkillIsComplete(unittest.TestCase):
    """Hold every runtime skill to the pattern, including ones added later.

    The template ships runtime skills as examples of a self-extending pattern.
    If some carry only a smells list while others carry the full pattern, an
    agent told to "follow the existing runtime skills" for a new language gets
    two contradictory templates and may silently drop static analysis.
    """

    def test_at_least_the_known_runtimes_are_present(self):
        found = discovered_runtime_skills()
        self.assertGreaterEqual(len(found), 11, f"expected the shipped runtimes, found {found}")

    def test_every_runtime_skill_has_valid_frontmatter(self):
        for runtime in discovered_runtime_skills():
            with self.subTest(runtime=runtime):
                text = (SPECIALISE / runtime / "SKILL.md").read_text()
                self.assertTrue(text.startswith("---\n"), "missing frontmatter")
                end = text.find("\n---", 4)
                self.assertGreater(end, 0, "unterminated frontmatter")
                frontmatter = text[4:end]
                self.assertIn("name:", frontmatter)
                self.assertIn("description:", frontmatter)

    def test_every_runtime_skill_has_the_required_sections(self):
        for runtime in discovered_runtime_skills():
            text = (SPECIALISE / runtime / "SKILL.md").read_text()
            for section in REQUIRED_RUNTIME_SECTIONS:
                with self.subTest(runtime=runtime, section=section):
                    self.assertIn(
                        section,
                        text,
                        f"{runtime} is missing '{section}'; see init/SKILL.md step 10",
                    )

    def test_every_runtime_skill_acknowledges_unknown_tools(self):
        for runtime in discovered_runtime_skills():
            with self.subTest(runtime=runtime):
                text = (SPECIALISE / runtime / "SKILL.md").read_text().lower()
                self.assertIn(
                    "not a closed list",
                    text,
                    f"{runtime} must state its tool list is not closed",
                )

    def test_every_runtime_skill_is_catalogued(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        for runtime in discovered_runtime_skills():
            with self.subTest(runtime=runtime):
                self.assertIn(f"specialise/{runtime}/SKILL.md", catalog)

    def test_every_runtime_skill_is_required_by_the_repo_contract(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        for runtime in discovered_runtime_skills():
            with self.subTest(runtime=runtime):
                self.assertIn(f"specialise/{runtime}", text)


class TestInitSkillRuntimeGuidance(unittest.TestCase):
    """init/SKILL.md must not carry a hand-maintained runtime list that rots."""

    def test_step_ten_points_at_the_catalog_not_a_hardcoded_list(self):
        text = (ROOT / ".agents/skills/init/SKILL.md").read_text()
        self.assertIn("CATALOG.toon", text)

    def test_step_ten_does_not_claim_java_as_a_runtime_skill(self):
        # The skill was renamed runtime-java -> runtime-jvm; a stale "Java"
        # in the example list sends an agent looking for a skill that is gone.
        text = (ROOT / ".agents/skills/init/SKILL.md").read_text()
        self.assertNotIn("runtime-java/", text)

    def test_step_ten_names_the_required_sections(self):
        text = (ROOT / ".agents/skills/init/SKILL.md").read_text().lower()
        for phrase in ("static-analysis", "language smells", "ecosystem openness"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


class TestRuntimeRustSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/runtime-rust/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/runtime-rust/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_skill_mentions_cargo(self):
        path = ROOT / ".agents/skills/specialise/runtime-rust/SKILL.md"
        text = path.read_text()
        self.assertIn("cargo", text.lower())

    def test_skill_mentions_clippy(self):
        path = ROOT / ".agents/skills/specialise/runtime-rust/SKILL.md"
        text = path.read_text()
        self.assertIn("clippy", text.lower())

    def test_skill_acknowledges_unknown_tools(self):
        path = ROOT / ".agents/skills/specialise/runtime-rust/SKILL.md"
        text = path.read_text()
        self.assertIn("not a closed list", text.lower())

    def test_skill_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/runtime-rust/SKILL.md", catalog)

    def test_skill_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/runtime-rust", text)

    def test_static_analysis_table_has_rust(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertIn("Rust", text)
        self.assertIn("clippy", text.lower())

    def test_static_analysis_table_has_go(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertIn("Go", text)
        self.assertIn("golangci-lint", text.lower())

    def test_static_analysis_table_has_csharp(self):
        path = ROOT / ".agents/skills/specialise/static-analysis/SKILL.md"
        text = path.read_text()
        self.assertIn("C#/.NET", text)
        self.assertIn("dotnet format", text.lower())


class TestRuntimeGoSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/runtime-go/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/runtime-go/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_skill_mentions_go_modules(self):
        path = ROOT / ".agents/skills/specialise/runtime-go/SKILL.md"
        text = path.read_text()
        self.assertIn("go.mod", text)
        self.assertIn("go test", text)

    def test_skill_acknowledges_unknown_tools(self):
        path = ROOT / ".agents/skills/specialise/runtime-go/SKILL.md"
        text = path.read_text()
        self.assertIn("not a closed list", text.lower())

    def test_skill_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/runtime-go/SKILL.md", catalog)

    def test_skill_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/runtime-go", text)


class TestRuntimeCSharpSkill(unittest.TestCase):
    def test_skill_file_exists(self):
        path = ROOT / ".agents/skills/specialise/runtime-csharp/SKILL.md"
        self.assertTrue(path.exists(), f"missing skill: {path}")

    def test_skill_has_valid_frontmatter(self):
        path = ROOT / ".agents/skills/specialise/runtime-csharp/SKILL.md"
        text = path.read_text()
        self.assertTrue(text.startswith("---\n"), "missing frontmatter")
        end = text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")
        frontmatter = text[4:end]
        self.assertIn("name:", frontmatter)
        self.assertIn("description:", frontmatter)

    def test_skill_mentions_dotnet(self):
        path = ROOT / ".agents/skills/specialise/runtime-csharp/SKILL.md"
        text = path.read_text()
        self.assertIn("dotnet", text.lower())
        self.assertIn("csproj", text.lower())

    def test_skill_acknowledges_unknown_tools(self):
        path = ROOT / ".agents/skills/specialise/runtime-csharp/SKILL.md"
        text = path.read_text()
        self.assertIn("not a closed list", text.lower())

    def test_skill_in_catalog(self):
        catalog = (ROOT / ".agents/skills/CATALOG.toon").read_text()
        self.assertIn("specialise/runtime-csharp/SKILL.md", catalog)

    def test_skill_in_required_skills(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("specialise/runtime-csharp", text)


class TestCheckSecrets(unittest.TestCase):
    def test_clean_repo_passes(self):
        result = subprocess.run(
            [str(BIN / "check-secrets")],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("SECRETS CHECK OK", result.stdout)

    def test_planted_secret_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text("api key: sk-abcdefghijklmnopqrstuvwxyz1234567890\n")
            result = subprocess.run(
                [str(BIN / "check-secrets")],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("SECRETS CHECK FAILED", result.stdout)
            self.assertIn("leak.txt", result.stdout)

    def test_private_key_block_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "key.pem").write_text(
                "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n-----END RSA PRIVATE KEY-----\n"
            )
            result = subprocess.run(
                [str(BIN / "check-secrets")],
                cwd=root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("private key", result.stdout.lower())

    def test_check_secrets_is_in_project_check(self):
        text = (ROOT / ".agentic-template/bin/project").read_text()
        self.assertIn("check-secrets", text)

    def test_check_secrets_is_in_repo_contract(self):
        text = (ROOT / ".agentic-template/bin/check-repo-contract").read_text()
        self.assertIn("check-secrets", text)

    def test_anthropic_key_is_detected(self):
        # The plain sk- pattern cannot match this: the hyphen after `sk-`
        # falls outside its character class.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(
                "ANTHROPIC_API_KEY=sk-ant-api03-"
                "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ABCDEFGHIJ\n"
            )
            result = subprocess.run(
                [str(BIN / "check-secrets")],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("Anthropic", result.stdout)

    def test_openai_project_key_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "leak.txt").write_text(
                "OPENAI_API_KEY=sk-proj-"
                "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789ABCDEFGHIJ\n"
            )
            result = subprocess.run(
                [str(BIN / "check-secrets")],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("project-scoped", result.stdout)


def git_available():
    try:
        return subprocess.run(
            ["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode == 0
    except OSError:
        return False


@unittest.skipUnless(git_available(), "git is not available")
class TestCheckSecretsIsGitAware(unittest.TestCase):
    """Scope is what git would let you commit, not everything on disk.

    Scanning ignored paths flags credentials that cannot reach the remote
    (a real `.env`, `node_modules/`), which is noise — and contradicts the
    tool's own advice to move secrets into an untracked `.env`.
    """

    AWS_KEY = "AKIAABCDEFGHIJKLMNOP"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self):
        return subprocess.run(
            [str(BIN / "check-secrets")],
            cwd=self.repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )

    def test_gitignored_file_is_out_of_scope(self):
        (self.repo / ".gitignore").write_text(".env\n")
        (self.repo / ".env").write_text(f"AWS_ACCESS_KEY_ID={self.AWS_KEY}\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("SECRETS CHECK OK", result.stdout)

    def test_untracked_but_committable_file_is_in_scope(self):
        # Not yet `git add`ed, but nothing stops someone adding it next.
        (self.repo / "config.txt").write_text(f"AWS_ACCESS_KEY_ID={self.AWS_KEY}\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("config.txt", result.stdout)

    def test_staged_file_is_in_scope(self):
        (self.repo / "config.txt").write_text(f"AWS_ACCESS_KEY_ID={self.AWS_KEY}\n")
        subprocess.run(["git", "add", "config.txt"], cwd=self.repo, check=True)
        result = self.run_check()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("config.txt", result.stdout)

    def test_ignored_directory_is_not_walked(self):
        (self.repo / ".gitignore").write_text("vendor/\n")
        vendor = self.repo / "vendor"
        vendor.mkdir()
        (vendor / "leak.txt").write_text(f"AWS_ACCESS_KEY_ID={self.AWS_KEY}\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_non_git_directory_falls_back_to_walking_the_tree(self):
        with tempfile.TemporaryDirectory() as plain:
            root = Path(plain)
            (root / "leak.txt").write_text(f"AWS_ACCESS_KEY_ID={self.AWS_KEY}\n")
            result = subprocess.run(
                [str(BIN / "check-secrets")],
                cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("leak.txt", result.stdout)

    def test_docstring_documents_the_history_limitation(self):
        text = (BIN / "check-secrets").read_text()
        self.assertIn("does not scan git history", text.lower())


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
