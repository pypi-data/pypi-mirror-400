import unittest
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.auto import MemoryCandidate
from mengram import ChatMemory, ChatMemoryConfig, MemoryClient, get_preset


def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)


class ChatMemorySimpleTest(unittest.TestCase):
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

    def test_step_and_step_with_llm(self):
        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        res = chat.step("Hello")
        self.assertFalse(res.ingested)
        self.assertIsNone(res.assistant_text)
        self.assertGreater(len(res.messages), 0)

        def fake_llm(msgs):
            return "Hi there"

        res2 = chat.step_with_llm("How are you?", fake_llm)
        self.assertEqual(res2.assistant_text, "Hi there")

    def test_commit_assistant_and_history(self):
        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        res = chat.step("Hello")
        self.assertIsNone(res.assistant_text)
        res_after = chat.commit_assistant("Reply")
        # Next step should include assistant history
        res2 = chat.step("Next")
        contents = [m["content"] for m in res2.messages]
        self.assertTrue(any("Reply" in c for c in contents))

    def test_tool_output_and_ingest(self):
        # fake extractor that returns one candidate per interaction
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

        config = ChatMemoryConfig(auto_ingest_every_n_user_turns=1, extractor=DummyExtractor())
        chat = ChatMemory(self.client, scope="user", entity_id="u1", config=config)
        chat.add_tool_output(name="tool1", content="some very long tool output" * 5)
        res = chat.step("Tell me something")
        ingested, count = chat.maybe_ingest()
        self.assertTrue(ingested)
        self.assertGreaterEqual(count, 1)

    def test_ingest_cadence(self):
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

        config = ChatMemoryConfig(auto_ingest_every_n_user_turns=2, extractor=DummyExtractor())
        chat = ChatMemory(self.client, scope="user", entity_id="u1", config=config)
        ingested_flags = []
        chat.step("turn1")
        ingested_flags.append(chat.maybe_ingest()[0])
        chat.commit_assistant("a1")
        chat.step("turn2")
        ingested_flags.append(chat.maybe_ingest()[0])
        chat.commit_assistant("a2")
        # Should ingest on turn 2 boundary only
        self.assertEqual(ingested_flags, [False, True])

    def test_preset_name_and_overrides(self):
        cfg = ChatMemoryConfig()
        self.assertEqual(cfg.preset_name, "CHAT_DEFAULT")
        cfg2 = get_preset("CHAT_DEFAULT", context_limit_turns=4)
        self.assertEqual(cfg2.preset_name, "CHAT_DEFAULT")
        self.assertEqual(cfg2.context_limit_turns, 4)
        with self.assertRaises(ValueError):
            get_preset("CHAT_DEFAULT", unknown_field=123)


if __name__ == "__main__":
    unittest.main()
