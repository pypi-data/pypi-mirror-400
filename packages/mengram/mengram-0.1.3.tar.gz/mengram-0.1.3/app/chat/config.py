from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from app.auto import LLMMemoryExtractor
from app.session.budget import TokenBudgetPolicy
from app.session.tokens import TokenCounter, SimpleTokenCounter
from app.session.summarizer import SummarizerConfig


@dataclass
class ChatMemoryConfig:
    # Session
    context_limit_turns: int = 8
    keep_last_n_turns: int = 3
    tool_max_chars: int = 800
    summarizer: Optional[object] = None
    summarizer_config: SummarizerConfig = field(default_factory=SummarizerConfig)
    llm_summarizer_fn: Optional[Callable] = None
    preset_name: str = "CHAT_DEFAULT"

    # Budget
    policy: TokenBudgetPolicy = field(
        default_factory=lambda: TokenBudgetPolicy(
            max_input_tokens=4000,
            reserved_output_tokens=600,
            max_tokens_memories=800,
            max_tokens_summary=800,
            max_tokens_recent_history=2000,
            max_tokens_tool_items=800,
            min_history_messages=2,
            drop_tool_before_user_assistant=True,
        )
    )
    token_counter: TokenCounter = field(default_factory=SimpleTokenCounter)

    # Long-term
    recall_k: int = 5
    max_memories_in_prompt: int = 8
    auto_ingest_every_n_user_turns: int = 3
    auto_ingest_max_turns_window: int = 3
    min_importance: float = 0.2
    extractor: Optional[LLMMemoryExtractor] = None

    # Debug
    print_budget_report: bool = False
    return_reports: bool = True


def get_preset(name: str, **overrides) -> ChatMemoryConfig:
    key = name.upper()
    if key == "CHAT_DEFAULT":
        base = ChatMemoryConfig(preset_name="CHAT_DEFAULT")
    elif key == "TOOL_HEAVY":
        base = ChatMemoryConfig(
            context_limit_turns=10,
            keep_last_n_turns=3,
            tool_max_chars=500,
            policy=TokenBudgetPolicy(
                max_input_tokens=4500,
                reserved_output_tokens=700,
                max_tokens_memories=500,
                max_tokens_summary=600,
                max_tokens_recent_history=2200,
                max_tokens_tool_items=1200,
                min_history_messages=2,
                drop_tool_before_user_assistant=True,
            ),
            recall_k=4,
            auto_ingest_every_n_user_turns=4,
            auto_ingest_max_turns_window=3,
            min_importance=0.25,
            preset_name="TOOL_HEAVY",
        )
    elif key == "RAG_HEAVY":
        base = ChatMemoryConfig(
            context_limit_turns=10,
            keep_last_n_turns=4,
            tool_max_chars=1000,
            policy=TokenBudgetPolicy(
                max_input_tokens=6000,
                reserved_output_tokens=900,
                max_tokens_memories=1800,
                max_tokens_summary=900,
                max_tokens_recent_history=2200,
                max_tokens_tool_items=700,
                min_history_messages=2,
                drop_tool_before_user_assistant=False,
            ),
            recall_k=8,
            auto_ingest_every_n_user_turns=3,
            auto_ingest_max_turns_window=4,
            min_importance=0.15,
            preset_name="RAG_HEAVY",
        )
    else:
        raise ValueError(f"Unknown preset: {name}")

    for attr, val in overrides.items():
        if not hasattr(base, attr):
            raise ValueError(f"Unknown override field: {attr}")
        setattr(base, attr, val)
    _validate_config(base)
    return base


def _validate_config(cfg: ChatMemoryConfig) -> None:
    if cfg.keep_last_n_turns > cfg.context_limit_turns:
        raise ValueError("keep_last_n_turns must be <= context_limit_turns")
