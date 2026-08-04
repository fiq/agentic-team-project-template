"""Tests for the AAA / FIRST / fixture testing-structure default.

An implementation repo built from this template shipped tests with no
fixtures, no Arrange-Act-Assert structure and no regard for the FIRST
properties. The contract and skill did not say to do otherwise. These tests
hold the fix in place so the guidance cannot silently drop out again.
"""
import unittest

import _support

ROOT = _support.ROOT


def _section(text, heading, next_prefix="## "):
    start = text.find(heading)
    assert start >= 0, f"heading {heading!r} not found"
    end = text.find(f"\n{next_prefix}", start + len(heading))
    return text[start:] if end < 0 else text[start:end]


class TestAgentsMdTestingExpectations(unittest.TestCase):
    def setUp(self):
        self.section = _section(
            (ROOT / "AGENTS.md").read_text(), "## Testing expectations"
        )

    def test_mentions_arrange_act_assert(self):
        self.assertIn("Arrange-Act-Assert", self.section)

    def test_mentions_first_principles(self):
        for word in ("Fast", "Independent", "Repeatable", "Self-validating", "Timely"):
            with self.subTest(word=word):
                self.assertIn(word, self.section)

    def test_mentions_fixtures_and_shared_state(self):
        self.assertIn("fixture", self.section.lower())
        self.assertIn("shared", self.section.lower())

    def test_points_at_the_test_first_skill(self):
        self.assertIn("workflow/test-first", self.section)


class TestTestFirstSkill(unittest.TestCase):
    def setUp(self):
        path = ROOT / ".agents/skills/workflow/test-first/SKILL.md"
        self.text = path.read_text()

    def test_skill_has_valid_frontmatter(self):
        self.assertTrue(self.text.startswith("---\n"), "missing frontmatter")
        end = self.text.find("\n---", 4)
        self.assertGreater(end, 0, "unterminated frontmatter")

    def test_breaks_down_arrange_act_assert(self):
        for word in ("Arrange", "Act", "Assert"):
            with self.subTest(word=word):
                self.assertIn(word, self.text)

    def test_breaks_down_first_principles(self):
        for word in ("Fast", "Independent", "Repeatable", "Self-validating", "Timely"):
            with self.subTest(word=word):
                self.assertIn(word, self.text)

    def test_requires_a_real_fixture_not_shared_state(self):
        self.assertIn("fixture", self.text.lower())
        self.assertIn("shared", self.text.lower())


if __name__ == "__main__":
    unittest.main()
