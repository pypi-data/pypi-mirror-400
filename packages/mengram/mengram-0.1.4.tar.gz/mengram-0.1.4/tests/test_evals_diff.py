import unittest

from app.evals.diff import diff_eval_results


class EvalsDiffTest(unittest.TestCase):
    def test_diff_detects_regressions_and_fixes(self):
        before = {
            "run_id": "a",
            "transcripts": [
                {"transcript_name": "t1", "passed": True, "turns": []},
                {"transcript_name": "t2", "passed": False, "turns": [{"turn_index": 0, "expectations_passed": False, "fail_reasons": ["missing"]}]},
            ],
            "totals": {"drops": 10, "tokens": 100, "failed": 1, "passed": 1},
        }
        after = {
            "run_id": "b",
            "transcripts": [
                {"transcript_name": "t1", "passed": False, "turns": [{"turn_index": 0, "expectations_passed": False, "fail_reasons": ["new"]}]},
                {"transcript_name": "t2", "passed": True, "turns": []},
            ],
            "totals": {"drops": 15, "tokens": 120, "failed": 1, "passed": 1},
        }
        diff = diff_eval_results(before, after)
        self.assertEqual(diff.before_run_id, "a")
        self.assertEqual(diff.after_run_id, "b")
        self.assertEqual(len(diff.regressions), 1)
        self.assertEqual(len(diff.fixes), 1)
        self.assertIn("failed", diff.metric_deltas)
        self.assertTrue(diff.summary)


if __name__ == "__main__":
    unittest.main()
