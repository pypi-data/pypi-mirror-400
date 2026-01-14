import unittest

from app.session.context import ContextBuilder
from app.session.models import SessionItem, SummaryBlock
from app.session.session import SummarizingSession, trim_to_last_n_turns


def simple_summarizer(items):
    text = "; ".join([i.content for i in items if i.role in {"user", "assistant"}])
    return SummaryBlock(assistant_summary=text or "(empty)")


class SessionTestCase(unittest.TestCase):
    def test_invalid_config_raises(self):
        with self.assertRaises(ValueError):
            SummarizingSession(context_limit_turns=2, keep_last_n_turns=3)

    def test_trim_preserves_turn_boundaries(self):
        items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="tool", content="t1"),
            SessionItem(role="user", content="u2"),
            SessionItem(role="assistant", content="a2"),
            SessionItem(role="user", content="u3"),
        ]
        trimmed = trim_to_last_n_turns(items, 2)
        self.assertEqual([i.content for i in trimmed], ["u2", "a2", "u3"])

    def test_trim_keeps_turn_payloads(self):
        items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="tool", content="t1"),
            SessionItem(role="user", content="u2"),
            SessionItem(role="assistant", content="a2"),
            SessionItem(role="tool", content="t2"),
        ]
        trimmed = trim_to_last_n_turns(items, 1)
        self.assertEqual([i.content for i in trimmed], ["u2", "a2", "t2"])

    def test_tool_trimming_and_summarization(self):
        session = SummarizingSession(
            context_limit_turns=2,
            keep_last_n_turns=2,
            tool_max_chars=5,
            summarizer=simple_summarizer,
        )
        # turn 1
        session.add(SessionItem(role="user", content="hello"))
        session.add(SessionItem(role="assistant", content="ok"))
        # turn 2 (contains tool)
        session.add(SessionItem(role="user", content="second"))
        session.add(SessionItem(role="tool", content="123456789"))
        session.add(SessionItem(role="assistant", content="ack"))
        # turn 3 triggers summary, keeps last 2 turns (so tool remains)
        session.add(SessionItem(role="user", content="third turn"))
        items = session.get_items()
        synthetic = [it for it in items if it.synthetic]
        self.assertGreaterEqual(len(synthetic), 1)
        # summary shape
        kinds = {it.kind for it in synthetic}
        self.assertIn("history_summary", kinds)
        tool = next(it for it in items if it.role == "tool")
        self.assertTrue(tool.metadata.get("trimmed"))
        self.assertTrue(tool.content.endswith("…"))

    def test_ingest_window_checkpointing(self):
        session = SummarizingSession()
        session.add(SessionItem(role="user", content="u1"))
        session.add(SessionItem(role="assistant", content="a1"))
        session.add(SessionItem(role="user", content="u2"))
        first = session.window_for_ingest()
        self.assertEqual([i.content for i in first], ["u1", "a1", "u2"])
        session.mark_ingested()
        session.add(SessionItem(role="assistant", content="a2"))
        session.add(SessionItem(role="user", content="u3"))
        second = session.window_for_ingest()
        self.assertEqual([i.content for i in second], ["u3"])
        limited = session.window_for_ingest(max_turns=1)
        self.assertEqual([i.content for i in limited], ["u3"])

    def test_checkpoint_after_summary(self):
        session = SummarizingSession(context_limit_turns=2, keep_last_n_turns=1, summarizer=simple_summarizer)
        session.add(SessionItem(role="user", content="u1"))
        session.add(SessionItem(role="assistant", content="a1"))
        session.add(SessionItem(role="user", content="u2"))  # triggers summary
        session.mark_ingested()
        session.add(SessionItem(role="assistant", content="a2"))
        session.add(SessionItem(role="user", content="u3"))
        window = session.window_for_ingest()
        self.assertEqual([i.content for i in window], ["u3"])

    def test_context_builder_includes_sections(self):
        session = SummarizingSession()
        session.add(SessionItem(role="system", content="Summary text", synthetic=True, kind="history_summary"))
        session.add(SessionItem(role="user", content="Hi"))
        session.add(SessionItem(role="assistant", content="Hello"))
        builder = ContextBuilder(system_prompt="sys", max_memories=1, max_history_items=3)
        messages = builder.build_messages(session_items=session.get_items(), memories=["fact"])
        self.assertEqual(messages[0]["content"], "sys")
        self.assertTrue(any("Long-term memories" in m["content"] for m in messages))
        history_roles = [m["role"] for m in messages if m["role"] not in {"system"}]
        self.assertEqual(history_roles[-2:], ["user", "assistant"])

    def test_context_builder_caps_and_order(self):
        session = SummarizingSession()
        session.add(SessionItem(role="system", content="Summary text", synthetic=True, kind="history_summary"))
        for i in range(5):
            session.add(SessionItem(role="user", content=f"u{i}"))
        builder = ContextBuilder(system_prompt="sys", max_memories=2, max_history_items=3)
        messages = builder.build_messages(session_items=session.get_items(), memories=["m1", "m2", "m3"])
        mem_blocks = [m for m in messages if m["role"] == "system" and m["content"].startswith("Long-term memories")]
        self.assertEqual(len(mem_blocks), 1)
        self.assertIn("m1", mem_blocks[0]["content"])
        self.assertIn("m2", mem_blocks[0]["content"])
        self.assertNotIn("m3", mem_blocks[0]["content"])
        history = [m for m in messages if m["role"] in {"user", "assistant", "tool", "system"} and not m["content"].startswith("Long-term memories") and m["content"] != "sys"]
        self.assertEqual([h["content"] for h in history[-3:]], ["u2", "u3", "u4"])


if __name__ == "__main__":
    unittest.main()
