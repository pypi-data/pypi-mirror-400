import unittest
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.evals.suite import run_eval_suite, run_eval_suite_dir, SuiteEvalResult
from app.evals.io import write_json_atomic, read_json
from mengram import ChatMemory, ChatMemoryConfig, MemoryClient


def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)


def chat_factory():
    tmp = tempfile.TemporaryDirectory()
    db_path = Path(tmp.name) / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    client = MemoryClient(session_factory=SessionLocal, embed_fn=fake_embed)
    chat = ChatMemory(client, scope="user", entity_id="u1")
    chat._tmpdir = tmp  # prevent GC
    return chat


class EvalsSuiteTest(unittest.TestCase):
    def test_run_single_transcript_to_suite_result(self):
        res = run_eval_suite([Path("tests/fixtures/evals/transcript_ok_v1.json")], chat_factory)
        self.assertIsInstance(res, SuiteEvalResult)
        self.assertTrue(res.passed)
        self.assertGreater(res.totals["turns"], 0)

    def test_run_dir_discovers_json_files(self):
        res = run_eval_suite_dir("tests/fixtures/evals", chat_factory, pattern="*.json", recursive=False)
        self.assertGreaterEqual(res.totals["transcripts"], 2)

    def test_totals_aggregate(self):
        res = run_eval_suite([Path("tests/fixtures/evals/transcript_ok_v1.json")], chat_factory)
        self.assertEqual(res.totals["transcripts"], 1)
        self.assertEqual(res.totals["passed"], 1)

    def test_strict_mode_raises_on_bad_json(self):
        with self.assertRaises(Exception):
            run_eval_suite([Path("tests/fixtures/evals/transcript_invalid_missing_user.json")], chat_factory, strict=True)

    def test_non_strict_skips_bad_json(self):
        res = run_eval_suite(
            [Path("tests/fixtures/evals/transcript_invalid_missing_user.json"), Path("tests/fixtures/evals/transcript_ok_v1.json")],
            chat_factory,
            strict=False,
        )
        self.assertEqual(res.totals["errors"], 1)
        self.assertGreaterEqual(res.totals["transcripts"], 1)


if __name__ == "__main__":
    unittest.main()
