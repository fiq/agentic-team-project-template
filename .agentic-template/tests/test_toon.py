import unittest

import _support  # noqa: F401  (import for the sys.path side effect)
import toon


class TestToonScalars(unittest.TestCase):
    def test_reads_scalar_types(self):
        text = "name: router\ncount: 3\nenabled: true\nmissing: null\n"
        self.assertEqual(
            toon.loads(text),
            {"name": "router", "count": 3, "enabled": True, "missing": None},
        )

    def test_reads_quoted_string_verbatim(self):
        self.assertEqual(toon.loads('marker: "a: b"\n'), {"marker": "a: b"})


class TestToonCollections(unittest.TestCase):
    def test_reads_nested_map(self):
        text = "profiles:\n  lean:\n    review: none\n"
        self.assertEqual(toon.loads(text), {"profiles": {"lean": {"review": "none"}}})

    def test_reads_inline_and_empty_lists(self):
        text = "order: [lean, standard, guarded]\nnone: []\nblank: {}\n"
        self.assertEqual(
            toon.loads(text),
            {"order": ["lean", "standard", "guarded"], "none": [], "blank": {}},
        )

    def test_reads_list_of_maps_with_nested_children(self):
        text = (
            "overrides:\n"
            "  - match:\n"
            "      model: claude-fable-5\n"
            "    profile: lean\n"
            "    reason: fixture run\n"
            "  - match:\n"
            "      model: other\n"
            "    profile: guarded\n"
            "    reason: unverified\n"
        )
        self.assertEqual(
            toon.loads(text),
            {
                "overrides": [
                    {
                        "match": {"model": "claude-fable-5"},
                        "profile": "lean",
                        "reason": "fixture run",
                    },
                    {
                        "match": {"model": "other"},
                        "profile": "guarded",
                        "reason": "unverified",
                    },
                ]
            },
        )

    def test_list_item_with_colon_in_prose_stays_a_string(self):
        text = "tests_run:\n  - 2026-07-26 project check: pass\n"
        self.assertEqual(
            toon.loads(text), {"tests_run": ["2026-07-26 project check: pass"]}
        )

    def test_url_list_item_stays_a_string(self):
        text = "refs:\n  - https://example.com/a\n"
        self.assertEqual(toon.loads(text), {"refs": ["https://example.com/a"]})


class TestToonErrors(unittest.TestCase):
    def test_odd_indent_is_rejected_with_line_number(self):
        with self.assertRaises(toon.ToonError) as caught:
            toon.loads("a:\n   b: 1\n")
        self.assertIn("line 2", str(caught.exception))


class TestToonRoundTrip(unittest.TestCase):
    def test_dumps_then_loads_is_identity(self):
        value = {
            "version": 1,
            "order": ["lean", "standard"],
            "profiles": {"lean": {"preload_layers": ["summary"]}},
            "runs": [{"date": "2026-07-26", "outcome": "success"}],
        }
        self.assertEqual(toon.loads(toon.dumps(value)), value)


if __name__ == "__main__":
    unittest.main()
