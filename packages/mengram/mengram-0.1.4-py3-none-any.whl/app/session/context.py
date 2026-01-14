from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

from .budget import ContextBuildReport, DropEvent, TokenBudgetPolicy
from .models import SessionItem
from .tokens import SimpleTokenCounter, TokenCounter


def _memory_to_text(mem: object) -> str:
    if hasattr(mem, "content"):
        return str(getattr(mem, "content"))
    return str(mem)


class ContextBuilder:
    """
    Construct model-ready context from long-term memories and a session buffer.

    Output is a list of message dicts compatible with common chat model clients.
    """

    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant.",
        max_memories: int = 8,
        max_history_items: int = 20,
    ):
        self.system_prompt = system_prompt
        self.max_memories = max_memories
        self.max_history_items = max_history_items

    def build_messages(
        self,
        session_items: Sequence[SessionItem],
        memories: Optional[Iterable[object]] = None,
        include_summary: bool = True,
    ) -> List[dict]:
        # Backward-compatible builder without budget: set very large policy.
        huge = TokenBudgetPolicy(
            max_input_tokens=1_000_000,
            reserved_output_tokens=0,
            max_tokens_memories=1_000_000,
            max_tokens_summary=1_000_000,
            max_tokens_recent_history=1_000_000,
            max_tokens_tool_items=1_000_000,
            min_history_messages=0,
        )
        messages, _ = self.build_messages_with_budget(
            session_items=session_items,
            memories=memories,
            include_summary=include_summary,
            policy=huge,
            token_counter=SimpleTokenCounter(),
        )
        return messages

    def build_messages_with_budget(
        self,
        session_items: Sequence[SessionItem],
        memories: Optional[Iterable[object]] = None,
        include_summary: bool = True,
        policy: Optional[TokenBudgetPolicy] = None,
        token_counter: Optional[TokenCounter] = None,
    ) -> Tuple[List[dict], ContextBuildReport]:
        policy = policy or TokenBudgetPolicy()
        counter = token_counter or SimpleTokenCounter()

        msgs: List[dict] = [{"role": "system", "content": self.system_prompt}]
        tokens_by_section = {"system": counter.count_message("system", self.system_prompt)}
        dropped: List[DropEvent] = []

        # Memories block
        mem_list = list(memories or [])
        mem_lines = [f"{policy.memory_line_prefix}{_memory_to_text(m)}" for m in mem_list[: self.max_memories]]
        mem_block = None
        mem_tokens = 0
        if mem_lines:
            mem_text = "Long-term memories:\n" + "\n".join(mem_lines)
            mem_block = {"role": "system", "content": mem_text}
            mem_tokens = counter.count_message("system", mem_text)
            if mem_tokens > policy.max_tokens_memories:
                kept_lines = []
                kept_tokens = counter.count_message("system", "Long-term memories:\n")
                for line in mem_lines:
                    line_tokens = counter.count_text(line)
                    if kept_tokens + line_tokens > policy.max_tokens_memories:
                        dropped.append(
                            DropEvent("memories", "section_cap", "system", None, line[:80], line_tokens)
                        )
                        continue
                    kept_lines.append(line)
                    kept_tokens += line_tokens
                mem_text = "Long-term memories:\n" + "\n".join(kept_lines)
                mem_block = {"role": "system", "content": mem_text}
                mem_tokens = counter.count_message("system", mem_text)
        if mem_block:
            msgs.append(mem_block)
        tokens_by_section["memories"] = mem_tokens

        # Summaries
        summary_kinds = {"history_summary_prompt", "history_summary"}
        summary_items = (
            [it for it in session_items if it.synthetic and it.kind in summary_kinds] if include_summary else []
        )
        # ensure prompt comes before summary for deterministic drop order
        summary_items = sorted(summary_items, key=lambda it: (it.kind != "history_summary_prompt", it.kind or ""))
        summary_msgs: List[dict] = []
        summary_tokens = 0
        for it in summary_items:
            msg = {
                "role": it.role,
                "content": it.content,
                **({"name": it.name} if it.name else {}),
            }
            t = counter.count_message(it.role, it.content, it.name)
            summary_tokens += t
            summary_msgs.append(msg)
        if summary_tokens > policy.max_tokens_summary and summary_msgs:
            # drop oldest summary messages first
            while summary_tokens > policy.max_tokens_summary and summary_msgs:
                drop = summary_msgs.pop(0)
                dt = counter.count_message(drop["role"], drop["content"], drop.get("name"))
                summary_tokens -= dt
                dropped.append(
                    DropEvent(
                        "summary",
                        "section_cap",
                        drop.get("role"),
                        None,
                        str(drop.get("content", ""))[:80],
                        dt,
                    )
                )
        msgs.extend(summary_msgs)
        tokens_by_section["summary"] = summary_tokens

        # Recent history (non-summary synthetic filtered)
        history_raw = list(session_items)[-self.max_history_items :]
        history_items = [it for it in history_raw if not (it.synthetic and it.kind in summary_kinds)]

        def to_msg(it: SessionItem) -> dict:
            return {
                "role": it.role,
                "content": it.content,
                **({"name": it.name} if it.name else {}),
                "_kind": it.kind,
                "_pinned": bool(it.metadata.get("pinned")) if it.metadata else False,
            }

        history_msgs = [to_msg(it) for it in history_items]
        history_tokens = sum(counter.count_message(m["role"], m["content"], m.get("name")) for m in history_msgs)

        # Section cap for recent history
        def drop_oldest_history(msgs_list: List[dict], prefer_drop_tool: bool, min_keep: int) -> Optional[dict]:
            if not msgs_list:
                return None
            if len(msgs_list) <= min_keep:
                return None
            # skip pinned items
            def eligible_indices(predicate=None):
                for idx, m in enumerate(msgs_list):
                    if m.get("_pinned"):
                        continue
                    if predicate is None or predicate(m):
                        yield idx, m

            if prefer_drop_tool:
                for idx, m in eligible_indices(lambda m: m["role"] == "tool"):
                    if len(msgs_list) - 1 < min_keep:
                        break
                    return msgs_list.pop(idx)
            # drop oldest non-pinned
            for idx, m in eligible_indices():
                if len(msgs_list) - 1 < min_keep:
                    break
                return msgs_list.pop(idx)
            return None

        while history_tokens > policy.max_tokens_recent_history and history_msgs:
            dropped_msg = drop_oldest_history(history_msgs, policy.drop_tool_before_user_assistant, policy.min_history_messages)
            if not dropped_msg:
                break
            dt = counter.count_message(dropped_msg["role"], dropped_msg["content"], dropped_msg.get("name"))
            history_tokens -= dt
            dropped.append(
                DropEvent(
                    "history",
                    "section_cap",
                    dropped_msg.get("role"),
                    dropped_msg.get("_kind"),
                    str(dropped_msg.get("content", ""))[:80],
                    dt,
                )
            )

        # Tool cap inside history
        def tool_tokens(msgs_list: List[dict]) -> int:
            return sum(
                counter.count_message(m["role"], m["content"], m.get("name"))
                for m in msgs_list
                if m["role"] == "tool"
            )

        while history_msgs and tool_tokens(history_msgs) > policy.max_tokens_tool_items:
            drop = drop_oldest_history(history_msgs, prefer_drop_tool=True, min_keep=policy.min_history_messages)
            if not drop:
                break
            dt = counter.count_message(drop["role"], drop["content"], drop.get("name"))
            history_tokens -= dt
            dropped.append(
                DropEvent(
                    "history",
                    "tool_cap",
                    drop.get("role"),
                    drop.get("_kind"),
                    str(drop.get("content", ""))[:80],
                    dt,
                )
            )

        # Global budget enforcement
        effective_budget = policy.max_input_tokens - policy.reserved_output_tokens
        msgs_final = list(msgs)
        msgs_final.extend(history_msgs)
        total_tokens = counter.count_messages(msgs_final)

        def try_drop_history():
            nonlocal total_tokens
            if not history_msgs:
                return False
            drop = drop_oldest_history(history_msgs, policy.drop_tool_before_user_assistant, policy.min_history_messages)
            if not drop:
                return False
            dt = counter.count_message(drop["role"], drop["content"], drop.get("name"))
            total_tokens -= dt
            dropped.append(
                DropEvent(
                    "history",
                    "over_budget",
                    drop.get("role"),
                    drop.get("_kind"),
                    str(drop.get("content", ""))[:80],
                    dt,
                )
            )
            return True

        def try_drop_memories():
            nonlocal mem_block, mem_tokens, total_tokens
            if not mem_block:
                return False
            dt = mem_tokens
            mem_block = None
            mem_tokens = 0
            total_tokens -= dt
            dropped.append(DropEvent("memories", "over_budget", "system", None, "(memories block)", dt))
            return True

        def try_drop_summary():
            nonlocal summary_msgs, summary_tokens, total_tokens
            if not summary_msgs:
                return False
            # skip pinned summary
            idx = None
            for i, m in enumerate(summary_msgs):
                if not m.get("_pinned"):
                    idx = i
                    break
            if idx is None:
                return False
            drop = summary_msgs.pop(idx)
            dt = counter.count_message(drop["role"], drop["content"], drop.get("name"))
            summary_tokens -= dt
            total_tokens -= dt
            dropped.append(
                DropEvent(
                    "summary",
                    "over_budget",
                    drop.get("role"),
                    None,
                    str(drop.get("content", ""))[:80],
                    dt,
                )
            )
            return True

        # enforce global budget by dropping in order
        while total_tokens > effective_budget:
            if try_drop_history():
                continue
            if try_drop_memories():
                msgs_final = [m for m in msgs_final if m.get("content") != "(memories block)"]
                continue
            if try_drop_summary():
                continue
            # last resort: truncate last message
            if msgs_final:
                last = msgs_final[-1]
                needed = total_tokens - effective_budget
                text = str(last["content"])
                truncated = text[: max(0, len(text) - needed * 4)]
                dt = counter.count_message(last["role"], last["content"], last.get("name"))
                total_tokens -= dt
                last["content"] = truncated
                dt_new = counter.count_message(last["role"], last["content"], last.get("name"))
                total_tokens += dt_new
                dropped.append(
                    DropEvent(
                        "history",
                        "truncated",
                        last.get("role"),
                        last.get("_kind"),
                        text[:80],
                        dt - dt_new,
                    )
                )
            break

        # rebuild final messages to ensure order and content
        msgs_final = [{"role": "system", "content": self.system_prompt}]
        if mem_block:
            msgs_final.append(mem_block)
        msgs_final.extend(summary_msgs)
        msgs_final.extend([{k: v for k, v in m.items() if k != "_kind"} for m in history_msgs])

        tokens_by_section["history"] = sum(counter.count_message(m["role"], m["content"], m.get("name")) for m in history_msgs)
        tokens_total = counter.count_messages(msgs_final)
        report = ContextBuildReport(
            max_input_tokens=policy.max_input_tokens,
            reserved_output_tokens=policy.reserved_output_tokens,
            effective_budget=effective_budget,
            tokens_total=tokens_total,
            tokens_by_section=tokens_by_section,
            dropped=dropped,
        )
        return msgs_final, report
