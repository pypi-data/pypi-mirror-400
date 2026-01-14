import unittest

from app.evals.judge import JudgeConfig, JudgeRunner


class EvalsJudgeTest(unittest.TestCase):
    def test_parses_valid_json(self):
        def judge_fn(prompt: str):
            return '{"score": 0.9, "verdict": "pass", "reasons": ["ok"], "flags": []}'

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True, min_score=0.5, fail_mode="threshold_soft"))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertEqual(res.score, 0.9)
        self.assertEqual(res.verdict, "pass")
        self.assertIn("prompt_hash", res.metadata)

    def test_invalid_json(self):
        def judge_fn(prompt: str):
            return "not json"

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertIsNotNone(res.error)

    def test_kwargs_retry(self):
        called = {"kwargs": False}

        def judge_fn(prompt: str):
            called["kwargs"] = True
            return '{"score": 0.5, "verdict": "unknown", "reasons": [], "flags": []}'

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True, max_output_tokens=10))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertTrue(called["kwargs"])
        self.assertEqual(res.score, 0.5)

    def test_multiple_json_objects_first_one_used(self):
        def judge_fn(prompt: str):
            return '{"score": 0.2, "verdict": "fail", "reasons": [], "flags": []} trailing {"score": 0.9}'

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertEqual(res.score, 0.2)

    def test_score_string_coerced(self):
        def judge_fn(prompt: str):
            return '{"score": "0.8", "verdict": "pass", "reasons": [], "flags": []}'

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertEqual(res.score, 0.8)

    def test_invalid_types(self):
        def judge_fn(prompt: str):
            return '{"score": "bad", "verdict": 5, "reasons": "no", "flags": {}}'

        runner = JudgeRunner(judge_fn, JudgeConfig(enabled=True))
        res = runner.run("ctx", tuple(), [], [], False)
        self.assertIsNotNone(res.error)


if __name__ == "__main__":
    unittest.main()
