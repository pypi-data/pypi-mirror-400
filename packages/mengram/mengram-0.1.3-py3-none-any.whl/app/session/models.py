from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

SessionRole = str  # expected: "user", "assistant", "tool", "system"


@dataclass
class SessionItem:
    role: SessionRole
    content: str
    name: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    synthetic: bool = False
    kind: Optional[str] = None
    turn_id: Optional[int] = None


def items_from_dicts(records: List[Dict[str, Any]]) -> List[SessionItem]:
    return [SessionItem(**rec) for rec in records]


class Summarizer(Protocol):
    def __call__(self, items: List[SessionItem]) -> "SummaryBlock":
        ...


@dataclass
class SummaryBlock:
    assistant_summary: str
    shadow_user_prompt: Optional[str] = None
    covers_until_index: Optional[int] = None
    summary_version: str = "v0"
    metadata: Dict[str, Any] = field(default_factory=dict)


# Defaults for summary synthetic items
SUMMARY_USER_PROMPT = "Conversation so far (compressed):"
SUMMARY_ASSISTANT_PREFIX = "Summary:"
