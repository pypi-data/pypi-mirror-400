from __future__ import annotations

from collections import deque
from typing import Iterable, List, Optional

from .models import (
    SUMMARY_ASSISTANT_PREFIX,
    SUMMARY_USER_PROMPT,
    SessionItem,
    SummaryBlock,
    Summarizer,
)


def turn_start_indices(items: List[SessionItem]) -> List[int]:
    """Return indices for the start of each real user turn (synthetic excluded)."""
    return [idx for idx, it in enumerate(items) if it.role == "user" and not it.synthetic]


def trim_to_last_n_turns(items: List[SessionItem], n: int) -> List[SessionItem]:
    """Keep items belonging to the last n user turns (synthetic excluded)."""
    if n <= 0:
        return []
    starts = turn_start_indices(items)
    if len(starts) <= n:
        return items
    boundary = starts[-n]
    return items[boundary:]


def _normalize_content(text: str) -> str:
    return " ".join(text.split())


class SummarizingSession:
    """
    Short-term session buffer with turn-aware trimming and optional summarization.

    Summarization replaces the older prefix with synthetic summary items while
    keeping the most recent turns verbatim. Tool outputs are trimmed defensively
    to avoid prompt blow-ups.
    """

    def __init__(
        self,
        context_limit_turns: int = 8,
        keep_last_n_turns: int = 4,
        tool_max_chars: int = 1200,
        summarizer: Optional[Summarizer] = None,
    ):
        if keep_last_n_turns > context_limit_turns:
            raise ValueError("keep_last_n_turns must be <= context_limit_turns")
        self.context_limit_turns = context_limit_turns
        self.keep_last_n_turns = keep_last_n_turns
        self.tool_max_chars = tool_max_chars
        self.summarizer = summarizer
        self._items: deque[SessionItem] = deque()
        self._current_turn_id = 0
        self._last_ingested_turn_id = 0
        self._last_ingested_index = 0
        self._last_summary_turn_id: Optional[int] = None

    # Public API -----------------------------------------------------
    def add(self, item: SessionItem) -> None:
        self.add_many([item])

    def add_many(self, items: Iterable[SessionItem]) -> None:
        for item in items:
            self._append_item(self._maybe_trim_tool(item))
        self._maybe_summarize()

    def get_items(self) -> List[SessionItem]:
        return list(self._items)

    def get_recent_items(self, max_items: Optional[int] = None) -> List[SessionItem]:
        if max_items is None:
            return list(self._items)
        if max_items <= 0:
            return []
        return list(self._items)[-max_items:]

    def window_for_ingest(self, max_turns: Optional[int] = None) -> List[SessionItem]:
        """
        Return non-synthetic items belonging to turns after the last ingestion checkpoint.
        If max_turns is provided, limit to that many new turns.
        """
        new_items = [
            it
            for it in self._items
            if not it.synthetic and (it.turn_id or 0) > self._last_ingested_turn_id
        ]
        if max_turns is None:
            return new_items

        seen_turns: set[int] = set()
        limited: List[SessionItem] = []
        for it in new_items:
            tid = it.turn_id or 0
            if tid not in seen_turns and len(seen_turns) >= max_turns:
                break
            seen_turns.add(tid)
            limited.append(it)
        return limited

    def mark_ingested(self) -> None:
        """Advance the ingestion checkpoint to the latest turn in the buffer."""
        self._last_ingested_turn_id = self._current_turn_id
        self._last_ingested_index = len(self._items)

    # Internal helpers -----------------------------------------------
    def _append_item(self, item: SessionItem) -> None:
        # Assign turn ids: only real user messages advance the turn counter.
        if item.turn_id is None:
            if item.role == "user" and not item.synthetic:
                self._current_turn_id += 1
                item.turn_id = self._current_turn_id
            else:
                item.turn_id = self._current_turn_id
        self._items.append(item)

    def _maybe_trim_tool(self, item: SessionItem) -> SessionItem:
        if (
            item.role == "tool"
            and not item.synthetic
            and self.tool_max_chars
            and len(item.content) > self.tool_max_chars
        ):
            original_len = len(item.content)
            item.content = item.content[: self.tool_max_chars] + "…"
            item.metadata = dict(item.metadata)
            item.metadata.update({"trimmed": True, "original_len": original_len})
            if not item.kind:
                item.kind = "tool_trimmed"
        return item

    def _maybe_summarize(self) -> None:
        starts = turn_start_indices(list(self._items))
        if len(starts) <= self.context_limit_turns:
            return

        # Do not resummarize if we already summarized at this turn boundary.
        last_turn_start_idx = starts[-self.keep_last_n_turns] if len(starts) >= self.keep_last_n_turns else 0
        boundary_turn_id = list(self._items)[last_turn_start_idx].turn_id
        if self._last_summary_turn_id and boundary_turn_id and boundary_turn_id <= self._last_summary_turn_id:
            return

        prefix = list(self._items)[:last_turn_start_idx]
        suffix = list(self._items)[last_turn_start_idx:]

        summary_block = self._run_summarizer(prefix)
        synthetic_user = SessionItem(
            role="system",
            content=summary_block.shadow_user_prompt or SUMMARY_USER_PROMPT,
            synthetic=True,
            kind="history_summary_prompt",
            metadata={
                "covers_until": last_turn_start_idx - 1,
                "summary_version": summary_block.summary_version,
                **(summary_block.metadata or {}),
            },
            turn_id=self._current_turn_id,
        )
        synthetic_assistant = SessionItem(
            role="assistant",
            content=f"{SUMMARY_ASSISTANT_PREFIX} {summary_block.assistant_summary}",
            synthetic=True,
            kind="history_summary",
            metadata={
                "covers_until": last_turn_start_idx - 1,
                "summary_version": summary_block.summary_version,
                **(summary_block.metadata or {}),
            },
            turn_id=self._current_turn_id,
        )

        self._items = deque([synthetic_user, synthetic_assistant] + suffix)
        self._last_summary_turn_id = boundary_turn_id

    def _run_summarizer(self, items: List[SessionItem]) -> SummaryBlock:
        if self.summarizer:
            return self.summarizer(items)

        # Fallback summarizer: join user/assistant content succinctly.
        snippets: List[str] = []
        for it in items:
            if it.role in {"user", "assistant"} and not it.synthetic:
                snippets.append(f"{it.role}: {_normalize_content(it.content)}")
        assistant_summary = "; ".join(snippets) if snippets else "(no summary)"
        return SummaryBlock(assistant_summary=assistant_summary, shadow_user_prompt=SUMMARY_USER_PROMPT)
