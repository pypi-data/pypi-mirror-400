import unittest
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.evals.dataset import load_transcript_json, TranscriptSpec, TurnSpec, ExpectedSpec
from app.evals.runner import run_transcript_json, run_transcript_spec, EvalRunConfig
from app.evals.judge import JudgeConfig
from mengram import ChatMemory, ChatMemoryConfig, MemoryClient


def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)


class EvalsRunnerTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        self.client = MemoryClient(session_factory=SessionLocal, embed_fn=fake_embed)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_runner_passes_ok_fixture(self):
        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        result = run_transcript_json("tests/fixtures/evals/transcript_ok_v1.json", chat)
        self.assertTrue(result.passed)
        self.assertGreater(len(result.turns), 0)

    def test_runner_detects_fail(self):
        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        spec = load_transcript_json("tests/fixtures/evals/transcript_ok_v1.json")
        # modify expected to force failure
        turns = list(spec.turns)
        first = turns[0]
        bad_expected = ExpectedSpec(
            must_contain=("missing",),
            must_not_contain=(),
            must_match_any=(),
            min_constraint_hits=None,
            should_reference_memories=False,
        )
        bad_first = TurnSpec(user=first.user, tools=first.tools, expected=bad_expected, notes=first.notes)
        bad_spec = TranscriptSpec(
            schema_version=spec.schema_version,
            name=spec.name,
            description=spec.description,
            golden_constraints=spec.golden_constraints,
            turns=(bad_first,) + spec.turns[1:],
        )
        result = run_transcript_spec(bad_spec, chat)
        self.assertFalse(result.passed)
        self.assertGreater(result.totals["failures"], 0)

    def test_runner_pinned_tool_survives(self):
        small_policy = ChatMemoryConfig()
        chat = ChatMemory(self.client, scope="user", entity_id="u1", config=small_policy)
        spec = load_transcript_json("tests/fixtures/evals/transcript_ok_v1.json")
        res = run_transcript_spec(spec, chat)
        # ensure no pinned drop
        for t in res.turns:
            for d in t.dropped:
                self.assertNotEqual(d.get("reason"), "tool_cap")

    def test_runner_deterministic_across_runs(self):
        # use fresh DBs to avoid carryover
        def fresh_client():
            tmp = tempfile.TemporaryDirectory()
            db_path = Path(tmp.name) / "test.db"
            engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
            Base.metadata.create_all(bind=engine)
            SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
            return MemoryClient(session_factory=SessionLocal, embed_fn=fake_embed), tmp

        client1, tmp1 = fresh_client()
        client2, tmp2 = fresh_client()
        chat = ChatMemory(client1, scope="user", entity_id="u1")
        res1 = run_transcript_json("tests/fixtures/evals/transcript_ok_v1.json", chat)
        chat2 = ChatMemory(client2, scope="user", entity_id="u1")
        res2 = run_transcript_json("tests/fixtures/evals/transcript_ok_v1.json", chat2)
        tmp1.cleanup()
        tmp2.cleanup()
        self.assertEqual(res1.to_dict(), res2.to_dict())

    def test_runner_with_judge_record_only(self):
        def judge_fn(prompt: str, **kwargs):
            return '{"score": 0.6, "verdict": "pass", "reasons": [], "flags": []}'

        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        cfg = EvalRunConfig(judge_config=JudgeConfig(enabled=True, min_score=0.5, fail_mode="record_only"))
        res = run_transcript_json("tests/fixtures/evals/transcript_ok_v1.json", chat, config=cfg, judge_llm_fn=judge_fn)
        self.assertIsNotNone(res.turns[0].judge)
        self.assertTrue(res.passed)

    def test_runner_with_judge_hard_gate(self):
        def judge_fn(prompt: str, **kwargs):
            return '{"score": 0.1, "verdict": "fail", "reasons": ["bad"], "flags": []}'

        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        cfg = EvalRunConfig(judge_config=JudgeConfig(enabled=True, min_score=0.5, fail_mode="threshold_hard"))
        res = run_transcript_json("tests/fixtures/evals/transcript_ok_v1.json", chat, config=cfg, judge_llm_fn=judge_fn)
        self.assertFalse(res.passed)
        self.assertTrue(any("judge_below_threshold" in t.fail_reasons for t in res.turns))

    def test_judge_good_bad_transcripts(self):
        def judge_fn(prompt: str, **kwargs):
            payload = prompt.split("INPUT:\n", 1)[-1]
            try:
                import json
                data = json.loads(payload)
                ctx = data.get("context", "")
            except Exception:
                ctx = ""
            score = 0.9 if "User avoids peanuts" in ctx else 0.1
            verdict = "pass" if score >= 0.5 else "fail"
            return f'{{"score": {score}, "verdict": "{verdict}", "reasons": [], "flags": []}}'

        cfg = EvalRunConfig(judge_config=JudgeConfig(enabled=True, min_score=0.5, fail_mode="threshold_hard"))
        chat_good = ChatMemory(self.client, scope="user", entity_id="u1")
        good = run_transcript_json("tests/fixtures/evals/judge_good_v1.json", chat_good, config=cfg, judge_llm_fn=judge_fn)
        self.assertTrue(good.passed)
        chat_bad = ChatMemory(self.client, scope="user", entity_id="u2")
        bad = run_transcript_json("tests/fixtures/evals/judge_bad_v1.json", chat_bad, config=cfg, judge_llm_fn=judge_fn)
        self.assertFalse(bad.passed)


if __name__ == "__main__":
    unittest.main()
