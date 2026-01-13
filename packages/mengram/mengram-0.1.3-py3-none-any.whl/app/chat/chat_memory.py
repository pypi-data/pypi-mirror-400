from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from app.auto import Interaction, LLMMemoryExtractor
from app.chat.config import ChatMemoryConfig, get_preset
from app.core import MemoryClient
from app.session.context import ContextBuilder
from app.session.models import SessionItem
from app.session.session import SummarizingSession
from app.session.summarizer import LLMSummarizer


@dataclass
class ChatStepResult:
    assistant_text: Optional[str]
    messages: List[dict]
    report: object
    recalled_memories: list
    ingested: bool
    ingest_stored_count: int
    summary_inserted: bool


class ChatMemory:
    def __init__(
        self,
        client: MemoryClient,
        scope: str,
        entity_id: str,
        config: Optional[ChatMemoryConfig] = None,
        preset: str = "CHAT_DEFAULT",
        preset_overrides: Optional[dict] = None,
    ):
        self.client = client
        self.scope = scope
        self.entity_id = entity_id
        self.config = config or get_preset(preset, **(preset_overrides or {}))
        if self.config.keep_last_n_turns > self.config.context_limit_turns:
            raise ValueError("keep_last_n_turns must be <= context_limit_turns")
        self.session = SummarizingSession(
            context_limit_turns=self.config.context_limit_turns,
            keep_last_n_turns=self.config.keep_last_n_turns,
            tool_max_chars=self.config.tool_max_chars,
            summarizer=self.config.summarizer
            or (
                LLMSummarizer(self.config.llm_summarizer_fn, self.config.summarizer_config)
                if self.config.llm_summarizer_fn
                else None
            ),
        )
        self.builder = ContextBuilder(
            system_prompt="You are a helpful assistant.",
            max_memories=self.config.max_memories_in_prompt,
            max_history_items=100,
        )
        self.extractor: Optional[LLMMemoryExtractor] = self.config.extractor
        self.user_turns = 0

    # Public API -------------------------------------------------
    def step(self, user_text: str) -> ChatStepResult:
        self.start_turn(user_text)
        return self._build_result(assistant_text=None)

    def step_with_llm(self, user_text: str, llm_fn: Callable[[List[dict]], str]) -> ChatStepResult:
        self.start_turn(user_text)
        memories = self._recall(user_text)
        messages, _ = self.builder.build_messages_with_budget(
            session_items=self.session.get_items(),
            memories=memories,
            policy=self.config.policy,
            token_counter=self.config.token_counter,
        )
        assistant_text = llm_fn(messages)
        return self.commit_assistant(assistant_text, recalled_memories=memories)

    def start_turn(self, user_text: str) -> None:
        self._add_user(user_text)

    def rebuild(self) -> ChatStepResult:
        """Build prompt/report from current session state without adding a new turn."""
        user_query = self._latest_user_text()
        memories = self._recall(query=user_query)
        messages, report = self.builder.build_messages_with_budget(
            session_items=self.session.get_items(),
            memories=memories,
            policy=self.config.policy,
            token_counter=self.config.token_counter,
        )
        return ChatStepResult(
            assistant_text=None,
            messages=messages,
            report=report if self.config.return_reports else None,
            recalled_memories=memories,
            ingested=False,
            ingest_stored_count=0,
            summary_inserted=self._has_summary(),
        )

    def add_tool_output(self, name: str, content: str, kind: str = "tool_output", pinned: bool = False):
        metadata = {"pinned": True} if pinned else {}
        self.session.add(SessionItem(role="tool", name=name, content=content, kind=kind, metadata=metadata))

    def commit_assistant(self, text: str, recalled_memories: Optional[list] = None) -> ChatStepResult:
        self.session.add(SessionItem(role="assistant", content=text))
        ingested, stored = self.maybe_ingest()
        memories = recalled_memories if recalled_memories is not None else []
        messages, report = self.builder.build_messages_with_budget(
            session_items=self.session.get_items(),
            memories=memories,
            policy=self.config.policy,
            token_counter=self.config.token_counter,
        )
        if self.config.print_budget_report and report:
            print(report)
        return ChatStepResult(
            assistant_text=text,
            messages=messages,
            report=report if self.config.return_reports else None,
            recalled_memories=memories,
            ingested=ingested,
            ingest_stored_count=stored,
            summary_inserted=self._has_summary(),
        )

    def build_prompt(self, user_text: str) -> ChatStepResult:
        return self.step(user_text)

    def maybe_ingest(self) -> tuple[bool, int]:
        if not self.extractor:
            return False, 0
        if self.user_turns % max(1, self.config.auto_ingest_every_n_user_turns) != 0:
            return False, 0
        window = self.session.window_for_ingest(max_turns=self.config.auto_ingest_max_turns_window)
        interactions: List[Interaction] = [
            Interaction(role=it.role, content=it.content, metadata=it.metadata) for it in window if not it.synthetic
        ]
        if not interactions:
            return False, 0
        stored = self.client.auto_ingest(
            interactions=interactions,
            extractor=self.extractor,
            scope=self.scope,
            entity_id=self.entity_id,
            min_importance=self.config.min_importance,
        )
        self.session.mark_ingested()
        return True, len(stored)

    def debug_session(self) -> List[SessionItem]:
        return self.session.get_items()

    def describe(self) -> dict:
        return {
            "preset_name": getattr(self.config, "preset_name", ""),
            "policy": {
                "max_input_tokens": self.config.policy.max_input_tokens,
                "reserved_output_tokens": self.config.policy.reserved_output_tokens,
                "max_tokens_memories": self.config.policy.max_tokens_memories,
                "max_tokens_summary": self.config.policy.max_tokens_summary,
                "max_tokens_recent_history": self.config.policy.max_tokens_recent_history,
                "max_tokens_tool_items": self.config.policy.max_tokens_tool_items,
                "min_history_messages": self.config.policy.min_history_messages,
            },
            "summarizer_template": getattr(self.config.summarizer_config, "template_name", ""),
            "ingest_every_n_user_turns": self.config.auto_ingest_every_n_user_turns,
        }

    # Internal ---------------------------------------------------
    def _add_user(self, text: str):
        self.user_turns += 1
        self.session.add(SessionItem(role="user", content=text))

    def _recall(self, query: str):
        return self.client.recall(
            query=query,
            k=self.config.recall_k,
            scope=self.scope,
            entity_id=self.entity_id,
        )

    def _build_result(self, assistant_text: Optional[str]) -> ChatStepResult:
        user_query = self._latest_user_text()
        memories = self._recall(query=user_query)
        messages, report = self.builder.build_messages_with_budget(
            session_items=self.session.get_items(),
            memories=memories,
            policy=self.config.policy,
            token_counter=self.config.token_counter,
        )
        if self.config.print_budget_report and report:
            print(report)
        return ChatStepResult(
            assistant_text=assistant_text,
            messages=messages,
            report=report if self.config.return_reports else None,
            recalled_memories=memories,
            ingested=False,
            ingest_stored_count=0,
            summary_inserted=self._has_summary(),
        )

    def _has_summary(self) -> bool:
        return any(it.synthetic and (it.kind or "").startswith("history_summary") for it in self.session.get_items())

    def _latest_user_text(self) -> str:
        items = self.session.get_items()
        for it in reversed(items):
            if it.role == "user" and not it.synthetic:
                return it.content
        return ""
