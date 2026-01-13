import unittest
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.session.summarizer import SummarizerConfig, LLMSummarizer
from app.auto import MemoryCandidate
from mengram import ChatMemory, ChatMemoryConfig, MemoryClient


def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)


class GoldenPathContextTest(unittest.TestCase):
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

    def test_golden_flow(self):
        # deterministic summarizer
        def summarizer_prompt(prompt: str):
            return "Summary stub"

        summarizer = LLMSummarizer(summarizer_prompt, SummarizerConfig(tool_trim_chars=50))

        # deterministic extractor
        class DummyExtractor:
            def __call__(self, interactions):
                return [
                    MemoryCandidate(
                        content=it.content,
                        type="semantic",
                        importance=0.5,
                        scope=None,
                        entity_id=None,
                        tags=[],
                        metadata={},
                    )
                    for it in interactions
                ]

        config = ChatMemoryConfig(
            context_limit_turns=2,
            keep_last_n_turns=1,
            tool_max_chars=30,
            summarizer=summarizer,
            auto_ingest_every_n_user_turns=2,
            auto_ingest_max_turns_window=2,
            extractor=DummyExtractor(),
        )
        chat = ChatMemory(self.client, scope="user", entity_id="g1", config=config)

        # user turn 1
        res1 = chat.step("u1")
        self.assertFalse(res1.summary_inserted)
        # tool blob to force trimming/drops later
        chat.add_tool_output(name="tool", content="X" * 200)
        chat.commit_assistant("a1")
        # user turn 2 triggers ingest after assistant commit
        res2 = chat.step("u2")
        ingested, count = chat.maybe_ingest()
        self.assertTrue(ingested)
        self.assertGreaterEqual(count, 1)
        chat.commit_assistant("a2")
        # user turn 3 triggers summary insertion (context_limit_turns=2)
        res3 = chat.step("u3")
        self.assertTrue(res3.summary_inserted)
        # check drop ordering: tool likely dropped before user/assistant due to caps
        if res3.report and res3.report.dropped:
            first_drop = res3.report.dropped[0]
            self.assertIn(first_drop.reason, {"section_cap", "over_budget", "tool_cap"})
        self.assertLessEqual(res3.report.tokens_total, config.policy.max_input_tokens - config.policy.reserved_output_tokens)


if __name__ == "__main__":
    unittest.main()
