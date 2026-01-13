from __future__ import annotations

from typing import Protocol, Sequence


class TokenCounter(Protocol):
    def count_text(self, text: str) -> int: ...
    def count_message(self, role: str, content: str, name: str | None = None) -> int: ...
    def count_messages(self, messages: Sequence[dict]) -> int: ...


class SimpleTokenCounter:
    """
    Fallback token estimator.
    Assumes ~4 chars per token and a small per-message overhead.
    """

    def __init__(self, chars_per_token: int = 4, message_overhead: int = 3):
        self.chars_per_token = max(1, chars_per_token)
        self.message_overhead = message_overhead

    def count_text(self, text: str) -> int:
        return max(1, len(text) // self.chars_per_token)

    def count_message(self, role: str, content: str, name: str | None = None) -> int:
        extra = self.message_overhead + (1 if name else 0)
        return extra + self.count_text(content)

    def count_messages(self, messages: Sequence[dict]) -> int:
        return sum(self.count_message(m.get("role", ""), str(m.get("content", "")), m.get("name")) for m in messages)
