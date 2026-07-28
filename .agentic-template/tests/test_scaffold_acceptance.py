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


if __name__ == "__main__":
    unittest.main()
