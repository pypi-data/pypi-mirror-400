import unittest

from app.session.budget import TokenBudgetPolicy
from app.session.context import ContextBuilder
from app.session.models import SessionItem
from app.session.tokens import SimpleTokenCounter


class ContextBudgetTestCase(unittest.TestCase):
    def setUp(self):
        self.builder = ContextBuilder(system_prompt="sys", max_memories=10, max_history_items=50)
        self.counter = SimpleTokenCounter()

    def test_policy_validation(self):
        with self.assertRaises(ValueError):
            TokenBudgetPolicy(max_input_tokens=100, reserved_output_tokens=150)
        with self.assertRaises(ValueError):
            TokenBudgetPolicy(max_tokens_memories=-1)

    def test_hard_cap_respected(self):
        session_items = []
        for i in range(5):
            session_items.append(SessionItem(role="user", content=f"u{i}"))
            session_items.append(SessionItem(role="assistant", content=f"a{i}"))
        session_items.append(SessionItem(role="tool", content="x" * 500))
        policy = TokenBudgetPolicy(
            max_input_tokens=120,
            reserved_output_tokens=20,
            max_tokens_recent_history=80,
            max_tokens_tool_items=20,
        )
        messages, report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        total = self.counter.count_messages(messages)
        self.assertLessEqual(total, policy.max_input_tokens - policy.reserved_output_tokens)
        self.assertTrue(report.dropped)

    def test_reserved_output_effective_budget(self):
        policy = TokenBudgetPolicy(max_input_tokens=100, reserved_output_tokens=40, max_tokens_recent_history=60)
        messages, _ = self.builder.build_messages_with_budget(
            session_items=[SessionItem(role="user", content="hello"), SessionItem(role="assistant", content="world")],
            memories=[],
            policy=policy,
            token_counter=self.counter,
        )
        total = self.counter.count_messages(messages)
        self.assertLessEqual(total, policy.max_input_tokens - policy.reserved_output_tokens)

    def test_memories_section_cap(self):
        memories = [f"mem {i}" for i in range(20)]
        policy = TokenBudgetPolicy(max_input_tokens=500, reserved_output_tokens=0, max_tokens_memories=50)
        messages, _ = self.builder.build_messages_with_budget(
            session_items=[], memories=memories, policy=policy, token_counter=self.counter
        )
        mem_blocks = [m for m in messages if m["role"] == "system" and "Long-term memories" in m["content"]]
        self.assertEqual(len(mem_blocks), 1)
        self.assertLessEqual(self.counter.count_message("system", mem_blocks[0]["content"]), policy.max_tokens_memories)

    def test_drop_order_tools_first(self):
        session_items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="tool", content="tool data long" * 20, name="toolname"),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="user", content="u2"),
        ]
        policy = TokenBudgetPolicy(
            max_input_tokens=150,
            reserved_output_tokens=0,
            max_tokens_recent_history=80,
            max_tokens_tool_items=20,
            drop_tool_before_user_assistant=True,
        )
        messages, report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        roles = [m["role"] for m in messages]
        self.assertNotIn("tool", roles)
        self.assertTrue(any(d.section == "history" and d.role == "tool" for d in report.dropped))

    def test_drop_order_tools_first_off(self):
        session_items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="tool", content="tool data long" * 20, name="mytool"),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="user", content="u2"),
        ]
        policy = TokenBudgetPolicy(
            max_input_tokens=150,
            reserved_output_tokens=0,
            max_tokens_recent_history=80,
            max_tokens_tool_items=200,
            drop_tool_before_user_assistant=False,
        )
        messages, report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        # Check drop ordering intention: if a tool is dropped, a non-tool drop should appear before it.
        tool_drop_indices = [i for i, d in enumerate(report.dropped) if d.role == "tool"]
        non_tool_drop_indices = [i for i, d in enumerate(report.dropped) if d.role != "tool"]
        if tool_drop_indices and non_tool_drop_indices:
            self.assertLess(min(non_tool_drop_indices), min(tool_drop_indices))

    def test_tool_name_preserved_when_kept(self):
        session_items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="tool", content="short", name="kept_tool"),
        ]
        policy = TokenBudgetPolicy(
            max_input_tokens=200,
            reserved_output_tokens=0,
            max_tokens_recent_history=200,
            max_tokens_tool_items=200,
            drop_tool_before_user_assistant=False,
        )
        messages, _ = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        tool_msgs = [m for m in messages if m["role"] == "tool"]
        self.assertTrue(tool_msgs)
        self.assertEqual(tool_msgs[0].get("name"), "kept_tool")

    def test_min_history_preserves_most_recent(self):
        session_items = []
        for i in range(3):
            session_items.append(SessionItem(role="user", content=f"u{i}"))
            session_items.append(SessionItem(role="assistant", content=f"a{i}"))
        policy = TokenBudgetPolicy(max_input_tokens=80, reserved_output_tokens=0, max_tokens_recent_history=30, min_history_messages=2)
        messages, _ = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        history = [m for m in messages if m["role"] in {"user", "assistant", "tool"}]
        self.assertEqual([h["content"] for h in history[-2:]], ["u2", "a2"])

    def test_pinned_not_dropped(self):
        session_items = [
            SessionItem(role="user", content="u1", metadata={"pinned": True}),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="tool", content="tool data" * 20),
        ]
        policy = TokenBudgetPolicy(
            max_input_tokens=80,
            reserved_output_tokens=0,
            max_tokens_recent_history=30,
            max_tokens_tool_items=10,
            min_history_messages=1,
        )
        messages, report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        contents = [m["content"] for m in messages]
        self.assertIn("u1", contents)
        self.assertTrue(all(d.preview != "u1" for d in report.dropped))

    def test_summary_dropped_before_history_when_needed(self):
        summary_items = [
            SessionItem(role="system", content="Summary prompt", synthetic=True, kind="history_summary_prompt"),
            SessionItem(role="assistant", content="Summary content", synthetic=True, kind="history_summary"),
        ]
        history_items = [SessionItem(role="user", content="u1"), SessionItem(role="assistant", content="a1")]
        policy = TokenBudgetPolicy(max_input_tokens=40, reserved_output_tokens=0, max_tokens_summary=10, max_tokens_recent_history=40)
        _, report = self.builder.build_messages_with_budget(
            session_items=summary_items + history_items,
            memories=[],
            policy=policy,
            token_counter=self.counter,
        )
        self.assertTrue(any(d.section == "summary" and "Summary prompt" in d.preview for d in report.dropped))

    def test_deterministic_across_runs(self):
        session_items = [
            SessionItem(role="user", content="u1"),
            SessionItem(role="assistant", content="a1"),
            SessionItem(role="tool", content="tool" * 20),
        ]
        policy = TokenBudgetPolicy(max_input_tokens=120, reserved_output_tokens=0, max_tokens_recent_history=60, max_tokens_tool_items=10)
        first_msgs, first_report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=["mem1", "mem2"], policy=policy, token_counter=self.counter
        )
        second_msgs, second_report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=["mem1", "mem2"], policy=policy, token_counter=self.counter
        )
        self.assertEqual(first_msgs, second_msgs)
        self.assertEqual(
            [(d.section, d.reason, d.role, d.preview) for d in first_report.dropped],
            [(d.section, d.reason, d.role, d.preview) for d in second_report.dropped],
        )

    def test_last_resort_truncation(self):
        session_items = [SessionItem(role="user", content="u1" * 50)]
        policy = TokenBudgetPolicy(max_input_tokens=20, reserved_output_tokens=0, max_tokens_recent_history=5)
        messages, report = self.builder.build_messages_with_budget(
            session_items=session_items, memories=[], policy=policy, token_counter=self.counter
        )
        total = self.counter.count_messages(messages)
        self.assertLessEqual(total, policy.max_input_tokens - policy.reserved_output_tokens)
        self.assertTrue(any(d.reason == "truncated" for d in report.dropped))


if __name__ == "__main__":
    unittest.main()
