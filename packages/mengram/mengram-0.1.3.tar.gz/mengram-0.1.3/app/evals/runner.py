from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, List, Optional

from app.evals.assertions import build_check_text, eval_expected
from app.evals.dataset import TranscriptSpec, load_transcript_json
from app.chat import ChatMemory
from app.evals.judge import JudgeConfig, JudgeRunner, JudgeResult


@dataclass
class EvalRunConfig:
    schema_version: str = "v1"
    capture_drops: bool = True
    capture_messages_preview: bool = True
    max_preview_chars: int = 500
    fail_fast: bool = False
    judge_config: Optional[JudgeConfig] = None


@dataclass
class TurnEvalResult:
    turn_index: int
    user: str
    tools_injected: int
    prompt_tokens: Optional[int]
    constraint_hits: int
    constraints_matched: List[str]
    expectations_passed: bool
    fail_reasons: List[str]
    dropped: List[dict]
    summary_inserted: bool
    prompt_preview: Optional[str]
    judge: Optional[dict] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class TranscriptEvalResult:
    schema_version: str
    transcript_name: str
    transcript_path: Optional[str]
    preset: str
    policy_snapshot: dict
    passed: bool
    turns: List[TurnEvalResult]
    totals: dict
    judge_scores: Optional[dict] = None
    judge_failures: int = 0

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "transcript_name": self.transcript_name,
            "transcript_path": self.transcript_path,
            "preset": self.preset,
            "policy_snapshot": self.policy_snapshot,
            "passed": self.passed,
            "turns": [t.to_dict() for t in self.turns],
            "totals": self.totals,
            "judge_scores": self.judge_scores,
            "judge_failures": self.judge_failures,
        }


def run_transcript_json(path, chat: ChatMemory, *, config: Optional[EvalRunConfig] = None, llm_fn: Optional[Callable[[List[dict]], str]] = None, judge_llm_fn: Optional[Callable[[str], str]] = None) -> TranscriptEvalResult:
    spec = load_transcript_json(path)
    return run_transcript_spec(spec, chat=chat, config=config, llm_fn=llm_fn, transcript_path=str(path), judge_llm_fn=judge_llm_fn)


def run_transcript_spec(
    spec: TranscriptSpec,
    chat: ChatMemory,
    *,
    config: Optional[EvalRunConfig] = None,
    llm_fn: Optional[Callable[[List[dict]], str]] = None,
    transcript_path: Optional[str] = None,
    judge_llm_fn: Optional[Callable[[str], str]] = None,
) -> TranscriptEvalResult:
    cfg = config or EvalRunConfig()
    if cfg.schema_version != "v1":
        raise ValueError(f"Unsupported eval schema_version {cfg.schema_version}")
    if llm_fn is None:
        llm_fn = lambda msgs: "OK"
    if spec.schema_version != "v1":
        raise ValueError(f"Unsupported transcript schema_version {spec.schema_version}")
    if getattr(chat.config, "return_reports", True) is False:
        raise ValueError("ChatMemory.config.return_reports must be True for eval runner.")
    if getattr(chat, "extractor", None) is not None:
        raise ValueError("Eval runner should use ChatMemory with ingestion disabled (extractor=None).")
    preset_name = getattr(chat.config, "preset_name", "") or getattr(chat.config, "preset", "")
    judge_cfg = cfg.judge_config or JudgeConfig(enabled=False)
    judge_runner = JudgeRunner(judge_llm_fn, judge_cfg) if judge_cfg.enabled and judge_llm_fn else None

    turn_results: List[TurnEvalResult] = []
    total_drops = 0
    total_tokens = 0
    judge_scores = []
    judge_failures = 0

    for idx, turn in enumerate(spec.turns):
        # add user turn
        chat.start_turn(turn.user)
        tools_injected = 0
        for tool in turn.tools:
            chat.add_tool_output(name=tool.name, content=tool.content, kind=tool.kind, pinned=tool.pinned)
            tools_injected += 1
        # build prompt now (after tool injection)
        built = chat.rebuild()
        messages = built.messages
        report = built.report
        prompt_tokens = getattr(report, "tokens_total", None) if report else None
        dropped_list = []
        if report and cfg.capture_drops:
            dropped_list = [
                {
                    "section": d.section,
                    "reason": d.reason,
                    "role": d.role,
                    "preview": d.preview,
                }
                for d in report.dropped
            ]
            total_drops += len(dropped_list)
        check_text = build_check_text(messages)
        passed, reasons, constraint_hits, constraints_matched = eval_expected(
            check_text, turn.expected, spec.golden_constraints, built.recalled_memories
        )
        judge_result = None
        if judge_runner:
            judge = judge_runner.run(
                check_text,
                spec.golden_constraints,
                constraints_matched,
                dropped_list,
                built.summary_inserted,
            )
            judge_result = judge.to_dict()
            if judge.score is not None:
                judge_scores.append(judge.score)
            if judge.passed is False:
                judge_failures += 1
                if judge_cfg.fail_mode == "threshold_hard":
                    passed = False
                    reasons.append("judge_below_threshold")
        total_tokens += prompt_tokens or 0
        prompt_preview = None
        if cfg.capture_messages_preview:
            prompt_preview = check_text[: cfg.max_preview_chars]

        turn_results.append(
            TurnEvalResult(
                turn_index=idx,
                user=turn.user,
                tools_injected=tools_injected,
                prompt_tokens=prompt_tokens,
                constraint_hits=constraint_hits,
                constraints_matched=constraints_matched,
                expectations_passed=passed,
                fail_reasons=reasons,
                dropped=dropped_list,
                summary_inserted=built.summary_inserted,
                prompt_preview=prompt_preview,
                judge=judge_result,
            )
        )
        # commit assistant deterministically to advance session
        chat.commit_assistant(llm_fn(messages), recalled_memories=built.recalled_memories)
        if cfg.fail_fast and not passed:
            break

    policy = chat.config.policy
    snapshot = {
        "max_input_tokens": policy.max_input_tokens,
        "reserved_output_tokens": policy.reserved_output_tokens,
        "max_tokens_memories": policy.max_tokens_memories,
        "max_tokens_summary": policy.max_tokens_summary,
        "max_tokens_recent_history": policy.max_tokens_recent_history,
        "max_tokens_tool_items": policy.max_tokens_tool_items,
        "min_history_messages": policy.min_history_messages,
    }
    passed_all = all(tr.expectations_passed for tr in turn_results)
    judge_scores_summary = None
    if judge_scores:
        judge_scores_summary = {
            "avg": sum(judge_scores) / len(judge_scores),
            "min": min(judge_scores),
            "max": max(judge_scores),
            "count": len(judge_scores),
        }
    return TranscriptEvalResult(
        schema_version=cfg.schema_version,
        transcript_name=spec.name,
        transcript_path=transcript_path,
        preset=preset_name,
        policy_snapshot=snapshot,
        passed=passed_all,
        turns=turn_results,
        totals={"turns": len(turn_results), "failures": sum(not t.expectations_passed for t in turn_results), "drops": total_drops, "tokens": total_tokens},
        judge_scores=judge_scores_summary,
        judge_failures=judge_failures,
    )
