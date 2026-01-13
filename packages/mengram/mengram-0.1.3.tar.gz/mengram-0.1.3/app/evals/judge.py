from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.evals.judge_prompts import DEFAULT_JUDGE_TEMPLATE, get_judge_prompt


@dataclass
class JudgeConfig:
    enabled: bool = False
    template_name: str = DEFAULT_JUDGE_TEMPLATE
    custom_prompt: Optional[str] = None
    min_score: Optional[float] = None
    fail_mode: str = "record_only"  # record_only|threshold_soft|threshold_hard
    max_output_tokens: Optional[int] = None
    record_previews: bool = False
    prompt_preview_chars: int = 2000
    output_preview_chars: int = 500


@dataclass
class JudgeResult:
    schema_version: str
    passed: Optional[bool]
    score: Optional[float]
    verdict: str
    reasons: List[str]
    flags: List[str]
    raw_json: Optional[dict]
    error: Optional[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "passed": self.passed,
            "score": self.score,
            "verdict": self.verdict,
            "reasons": self.reasons,
            "flags": self.flags,
            "raw_json": self.raw_json,
            "error": self.error,
            "metadata": self.metadata,
        }


class JudgeRunner:
    def __init__(self, judge_llm_fn: Callable, config: JudgeConfig):
        self.judge_llm_fn = judge_llm_fn
        self.config = config

    def run(
        self,
        check_text: str,
        golden_constraints: Tuple[str, ...],
        constraints_matched: List[str],
        dropped: List[dict],
        summary_inserted: bool,
    ) -> JudgeResult:
        prompt = self._build_prompt(check_text, golden_constraints, constraints_matched, dropped, summary_inserted)
        hints = {
            "max_output_tokens": self.config.max_output_tokens,
            "template_name": self.config.template_name,
        }
        try:
            output = self.judge_llm_fn(prompt, **{k: v for k, v in hints.items() if v is not None})
        except TypeError:
            output = self.judge_llm_fn(prompt)
        raw, error = self._parse_output(str(output))
        if error:
            return JudgeResult(
                schema_version="v1",
                passed=None,
                score=None,
                verdict="unknown",
                reasons=[],
                flags=[],
                raw_json=None,
                error=error,
                metadata=self._metadata(prompt, output),
            )
        score = raw.get("score")
        verdict = raw.get("verdict", "unknown")
        reasons = raw.get("reasons", [])
        flags = raw.get("flags", [])
        passed = None
        if self.config.fail_mode in {"threshold_soft", "threshold_hard"} and self.config.min_score is not None:
            passed = bool(score is not None and score >= self.config.min_score)
        return JudgeResult(
            schema_version="v1",
            passed=passed,
            score=score,
            verdict=verdict,
            reasons=reasons if isinstance(reasons, list) else [],
            flags=flags if isinstance(flags, list) else [],
            raw_json=raw,
            error=None,
            metadata=self._metadata(prompt, output),
        )

    def _build_prompt(
        self,
        check_text: str,
        golden_constraints: Tuple[str, ...],
        constraints_matched: List[str],
        dropped: List[dict],
        summary_inserted: bool,
    ) -> str:
        if self.config.custom_prompt:
            system = self.config.custom_prompt
        else:
            system = get_judge_prompt(self.config.template_name)
        payload = {
            "golden_constraints": list(golden_constraints),
            "constraints_matched": constraints_matched,
            "dropped": dropped,
            "summary_inserted": summary_inserted,
            "context": check_text,
        }
        return system + "\nINPUT:\n" + json.dumps(payload, ensure_ascii=False)

    def _metadata(self, prompt: str, output: str) -> dict:
        if not self.config.record_previews:
            return {
                "template_name": self.config.template_name,
            }
        return {
            "template_name": self.config.template_name,
            "prompt_preview": prompt[: self.config.prompt_preview_chars],
            "output_preview": str(output)[: self.config.output_preview_chars],
        }

    def _parse_output(self, text: str) -> tuple[Optional[dict], Optional[str]]:
        obj_text = _extract_first_json_object(text)
        if not obj_text:
            return None, "no_json_object_found"
        try:
            raw = json.loads(obj_text)
        except json.JSONDecodeError as e:
            return None, f"invalid_json: {e.msg}"
        for field in ("score", "verdict", "reasons", "flags"):
            if field not in raw:
                return None, f"missing_field:{field}"
        # type validation / coercion
        score = raw.get("score")
        if isinstance(score, str):
            try:
                score = float(score)
                raw["score"] = score
            except ValueError:
                return None, "invalid_score_type"
        if not isinstance(score, (int, float)):
            return None, "invalid_score_type"
        if not isinstance(raw.get("verdict"), str):
            return None, "invalid_verdict_type"
        if not isinstance(raw.get("reasons"), list):
            return None, "invalid_reasons_type"
        if not isinstance(raw.get("flags"), list):
            return None, "invalid_flags_type"
        return raw, None


def _extract_first_json_object(text: str) -> Optional[str]:
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None
