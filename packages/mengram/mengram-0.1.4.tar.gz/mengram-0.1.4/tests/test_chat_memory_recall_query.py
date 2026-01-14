import unittest
import tempfile
from pathlib import Path

import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from mengram import ChatMemory, MemoryClient


def fake_embed(_: str):
    return np.ones(384, dtype=np.float32)


class RecordingClient(MemoryClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_query = None

    def recall(self, query: str, k: int = 8, scope=None, entity_id=None, as_of=None):
        self.last_query = query
        return super().recall(query=query, k=k, scope=scope, entity_id=entity_id, as_of=as_of)


class ChatMemoryRecallQueryTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tmpdir.name) / "test.db"
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        self.client = RecordingClient(session_factory=SessionLocal, embed_fn=fake_embed)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_rebuild_uses_latest_user_not_tool(self):
        chat = ChatMemory(self.client, scope="user", entity_id="u1")
        chat.start_turn("USER_QUERY")
        chat.add_tool_output(name="tool", content="TOOL_BLOB")
        chat.rebuild()
        self.assertEqual(self.client.last_query, "USER_QUERY")


if __name__ == "__main__":
    unittest.main()
