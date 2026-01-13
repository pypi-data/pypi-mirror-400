from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from mengram import ChatMemory


@dataclass
class ReplayConfig:
    preset: str = "CHAT_DEFAULT"
    scope: str = "session"
    entity_id: str = "replay"
    capture_reports: bool = True


@dataclass
class TurnResult:
    role: str
    content: str
    tokens: int
    dropped: List[dict] = field(default_factory=list)
    summary_inserted: bool = False


@dataclass
class ReplayResult:
    schema_version: str
    preset: str
    policy_snapshot: Dict[str, int]
    turns: List[TurnResult]
    totals: Dict[str, int]


class TranscriptReplayer:
    """
    Deterministically replays a transcript through ChatMemory to capture reports/metrics.
    Transcript items: dicts with role/content/name/metadata.
    """

    def __init__(self, chat_memory: ChatMemory, token_counter: Optional[Callable[[List[dict]], int]] = None, preset: str = "CHAT_DEFAULT"):
        self.chat = chat_memory
        self.token_counter = token_counter
        self.preset = preset

    def run(self, transcript: List[dict]) -> ReplayResult:
        turns: List[TurnResult] = []
        total_tokens = 0
        total_drops = 0
        for item in transcript:
            role = item.get("role")
            content = item.get("content", "")
            if role == "user":
                step = self.chat.step(content)
                tokens = self._count(step.messages)
                total_tokens += tokens
                dr = [{"section": d.section, "reason": d.reason} for d in (step.report.dropped if step.report else [])]
                total_drops += len(dr)
                turns.append(
                    TurnResult(
                        role="user",
                        content=content,
                        tokens=tokens,
                        dropped=dr,
                        summary_inserted=step.summary_inserted,
                    )
                )
            elif role == "assistant":
                step = self.chat.commit_assistant(content)
                tokens = self._count(step.messages)
                total_tokens += tokens
                dr = [{"section": d.section, "reason": d.reason} for d in (step.report.dropped if step.report else [])]
                total_drops += len(dr)
                turns.append(
                    TurnResult(
                        role="assistant",
                        content=content,
                        tokens=tokens,
                        dropped=dr,
                        summary_inserted=step.summary_inserted,
                    )
                )
            elif role == "tool":
                self.chat.add_tool_output(name=item.get("name") or "tool", content=content)
                turns.append(TurnResult(role="tool", content=content, tokens=0, dropped=[], summary_inserted=False))
            else:
                continue
        policy = self.chat.config.policy
        snapshot = {
            "max_input_tokens": policy.max_input_tokens,
            "reserved_output_tokens": policy.reserved_output_tokens,
            "max_tokens_memories": policy.max_tokens_memories,
            "max_tokens_summary": policy.max_tokens_summary,
            "max_tokens_recent_history": policy.max_tokens_recent_history,
            "max_tokens_tool_items": policy.max_tokens_tool_items,
            "min_history_messages": policy.min_history_messages,
        }
        return ReplayResult(
            schema_version="v1",
            preset=self.preset,
            policy_snapshot=snapshot,
            turns=turns,
            totals={"tokens": total_tokens, "drops": total_drops},
        )

    def _count(self, messages: List[dict]) -> int:
        if self.token_counter:
            return self.token_counter(messages)
        return 0
