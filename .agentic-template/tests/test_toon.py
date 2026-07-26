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

    def test_tab_indent_is_rejected_with_line_number(self):
        with self.assertRaises(toon.ToonError) as caught:
            toon.loads("key:\n\tvalue: 1\n")
        self.assertIn("line 2", str(caught.exception))
        self.assertIn("tab", str(caught.exception).lower())


class TestToonRoundTrip(unittest.TestCase):
    def test_dumps_then_loads_is_identity(self):
        value = {
            "version": 1,
            "order": ["lean", "standard"],
            "profiles": {"lean": {"preload_layers": ["summary"]}},
            "runs": [{"date": "2026-07-26", "outcome": "success"}],
        }
        self.assertEqual(toon.loads(toon.dumps(value)), value)

    def test_all_digit_string_survives_the_round_trip(self):
        value = {"sha": "0123456789012345"}
        self.assertEqual(toon.loads(toon.dumps(value)), value)

    def test_boolean_and_null_lookalike_strings_stay_strings(self):
        value = {"a": "true", "b": "false", "c": "null", "d": "-12"}
        self.assertEqual(toon.loads(toon.dumps(value)), value)

    def test_bracket_leading_string_stays_a_string(self):
        value = {"symptom": "[degraded]", "note": "{pending}"}
        self.assertEqual(toon.loads(toon.dumps(value)), value)


class TestToonLenience(unittest.TestCase):
    def test_duplicate_keys_resolve_last_wins(self):
        text = "a: 1\na: 2\n"
        self.assertEqual(toon.loads(text), {"a": 2})

    def test_unterminated_quote_is_treated_as_literal(self):
        text = 'marker: "a: b\n'
        self.assertEqual(toon.loads(text), {"marker": '"a: b'})


if __name__ == "__main__":
    unittest.main()
