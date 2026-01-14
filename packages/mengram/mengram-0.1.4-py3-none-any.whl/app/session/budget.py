from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TokenBudgetPolicy:
    max_input_tokens: int = 8000
    reserved_output_tokens: int = 1000
    max_tokens_system: Optional[int] = None
    max_tokens_memories: int = 800
    max_tokens_summary: int = 1200
    max_tokens_recent_history: int = 4000
    max_tokens_tool_items: int = 1200
    min_history_messages: int = 2
    drop_tool_before_user_assistant: bool = True
    memory_line_prefix: str = "- "

    def __post_init__(self):
        if self.max_input_tokens <= self.reserved_output_tokens:
            raise ValueError("max_input_tokens must be greater than reserved_output_tokens")
        for name, val in [
            ("max_tokens_memories", self.max_tokens_memories),
            ("max_tokens_summary", self.max_tokens_summary),
            ("max_tokens_recent_history", self.max_tokens_recent_history),
            ("max_tokens_tool_items", self.max_tokens_tool_items),
            ("min_history_messages", self.min_history_messages),
        ]:
            if val < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass
class DropEvent:
    section: str
    reason: str
    role: Optional[str]
    kind: Optional[str]
    preview: str
    tokens: int


@dataclass
class ContextBuildReport:
    max_input_tokens: int
    reserved_output_tokens: int
    effective_budget: int
    tokens_total: int
    tokens_by_section: Dict[str, int] = field(default_factory=dict)
    dropped: List[DropEvent] = field(default_factory=list)
