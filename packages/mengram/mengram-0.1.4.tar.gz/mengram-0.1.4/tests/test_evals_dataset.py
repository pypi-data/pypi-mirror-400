import unittest
from pathlib import Path

from app.evals.dataset import (
    TranscriptSpec,
    TurnSpec,
    ToolSpec,
    ExpectedSpec,
    load_transcript_json,
)


FIXTURES = Path("tests/fixtures/evals")


class EvalsDatasetTest(unittest.TestCase):
    def test_loads_valid_transcript(self):
        spec = load_transcript_json(FIXTURES / "transcript_ok_v1.json")
        self.assertEqual(spec.schema_version, "v1")
        self.assertGreater(len(spec.turns), 0)
        tool = spec.turns[1].tools[0]
        self.assertIsInstance(tool, ToolSpec)
        self.assertTrue(tool.pinned)
        self.assertEqual(tool.kind, "tool_output")

    def test_missing_user_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            load_transcript_json(FIXTURES / "transcript_invalid_missing_user.json")
        self.assertIn("turns[0].user", str(ctx.exception))

    def test_invalid_schema_version(self):
        bad = {
            "schema_version": "v2",
            "name": "x",
            "turns": [{"user": "hi"}],
            "golden_constraints": [],
        }
        with self.assertRaises(ValueError) as ctx:
            TranscriptSpec.from_dict(bad)
        self.assertIn("schema_version", str(ctx.exception))

    def test_defaults_behavior(self):
        turn = TurnSpec.from_dict({"user": "hi"})
        self.assertEqual(turn.tools, ())
        self.assertIsInstance(turn.expected, ExpectedSpec)
        self.assertEqual(turn.expected.must_contain, [])

    def test_type_validation(self):
        bad = {
            "schema_version": "v1",
            "name": "x",
            "golden_constraints": "notalist",
            "turns": [{"user": "hi"}],
        }
        with self.assertRaises(ValueError):
            TranscriptSpec.from_dict(bad)

        bad2 = {
            "schema_version": "v1",
            "name": "x",
            "golden_constraints": [],
            "turns": [
                {
                    "user": "hi",
                    "expected": {"min_constraint_hits": -1},
                }
            ],
        }
        with self.assertRaises(ValueError):
            TranscriptSpec.from_dict(bad2)

    def test_tool_defaults(self):
        tool = ToolSpec.from_dict({"name": "t", "content": "c"})
        self.assertFalse(tool.pinned)
        self.assertEqual(tool.kind, "tool_output")

    def test_notes_validation(self):
        bad_turn = {"user": "hi", "notes": 123}
        with self.assertRaises(ValueError):
            TurnSpec.from_dict(bad_turn, where="turns[0]")

    def test_tools_invalid_type(self):
        bad_turn = {"user": "hi", "tools": {}}
        with self.assertRaises(ValueError):
            TurnSpec.from_dict(bad_turn, where="turns[0]")

    def test_expected_invalid_type(self):
        bad_turn = {"user": "hi", "expected": "nope"}
        with self.assertRaises(ValueError):
            TurnSpec.from_dict(bad_turn, where="turns[0]")


if __name__ == "__main__":
    unittest.main()
