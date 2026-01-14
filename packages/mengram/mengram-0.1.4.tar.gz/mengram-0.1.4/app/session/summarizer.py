from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional

from .models import SessionItem, SummaryBlock
from .summary_prompts import DEFAULT_SUMMARY_TEMPLATE, get_summary_prompt


@dataclass
class SummarizerConfig:
    template_name: str = DEFAULT_SUMMARY_TEMPLATE
    max_summary_words: int = 200
    tool_trim_chars: int = 600
    style: str = "chat_default"
    model_name: Optional[str] = None
    include_tool_performance: bool = True
    custom_prompt: Optional[str] = None
    record_previews: bool = False
    prompt_preview_chars: int = 2000
    output_preview_chars: int = 500
    max_output_tokens: Optional[int] = None  # optional hint for providers


class LLMSummarizer:
    """
    Default LLM-backed summarizer.

    Accepts a user-supplied llm_fn(prompt: str) -> str (or messages-aware callable).
    Produces a SummaryBlock with a concise assistant_summary and an optional shadow prompt.
    """

    def __init__(self, llm_fn: Callable, config: Optional[SummarizerConfig] = None):
        self.llm_fn = llm_fn
        self.config = config or SummarizerConfig()

    def __call__(self, items: List[SessionItem]) -> SummaryBlock:
        prompt, meta = self._build_prompt(items)
        hints = {
            "max_output_tokens": self.config.max_output_tokens,
            "model_name": self.config.model_name,
            "style": self.config.style,
            "template_name": self.config.template_name,
        }
        # best-effort: pass hints if callable supports kwargs
        try:
            llm_out = self.llm_fn(prompt, **{k: v for k, v in hints.items() if v is not None})
        except TypeError:
            llm_out = self.llm_fn(prompt)
        # Basic safety: strip fences and whitespace
        if isinstance(llm_out, str):
            text = llm_out.strip().strip("`")
        else:
            text = str(llm_out)
        words = text.split()
        truncated = False
        original_word_count = len(words)
        kept_word_count = original_word_count
        if self.config.max_summary_words and len(words) > self.config.max_summary_words:
            text = " ".join(words[: self.config.max_summary_words]) + "…"
            truncated = True
            kept_word_count = self.config.max_summary_words
        return SummaryBlock(
            assistant_summary=text or "(empty)",
            shadow_user_prompt="Conversation so far (compressed):",
            metadata={
                **(
                    {
                        "prompt_preview": prompt[: self.config.prompt_preview_chars],
                        "output_preview": text[: self.config.output_preview_chars],
                    }
                    if self.config.record_previews
                    else {}
                ),
                "tool_trimmed": meta.get("tool_trimmed", 0),
                "tool_trimmed_names": meta.get("tool_trimmed_names", []),
                "trimmed_tools": meta.get("trimmed_tools", []),
                "model_name": self.config.model_name,
                "style": self.config.style,
                "template_name": self.config.template_name,
                "max_summary_words": self.config.max_summary_words,
                "tool_trim_chars": self.config.tool_trim_chars,
                "truncated_summary": truncated,
                "original_word_count": original_word_count,
                "kept_word_count": kept_word_count,
            },
        )

    def _build_prompt(self, items: Iterable[SessionItem]) -> tuple[str, dict]:
        lines: List[str] = []
        tool_trimmed = 0
        tool_names_trimmed: List[str] = []
        trimmed_tools_info: List[dict] = []
        for idx, it in enumerate(items, start=1):
            role = it.role.upper()
            name = f"({it.name})" if it.name else ""
            content = it.content
            if it.role == "tool" and len(content) > self.config.tool_trim_chars:
                original_len = len(content)
                content = content[: self.config.tool_trim_chars] + "…"
                tool_trimmed += 1
                if it.name:
                    tool_names_trimmed.append(it.name)
                trimmed_tools_info.append(
                    {
                        "name": it.name or "",
                        "original_len": original_len,
                        "kept_len": len(content),
                    }
                )
            lines.append(f"{idx}. {role}{name}: {content}")
        if self.config.custom_prompt:
            system_prompt = self.config.custom_prompt
        else:
            template = get_summary_prompt(self.config.template_name)
            system_prompt = template.format(max_summary_words=self.config.max_summary_words)
        if not self.config.include_tool_performance:
            system_prompt = system_prompt.replace("- Tool Calls & Outcomes\n", "")
        prompt = system_prompt + "\nConversation:\n" + "\n".join(lines)
        return prompt, {
            "tool_trimmed": tool_trimmed,
            "tool_trimmed_names": tool_names_trimmed,
            "trimmed_tools": trimmed_tools_info,
        }
