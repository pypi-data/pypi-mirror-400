from __future__ import annotations

import glob
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

from app.evals.runner import run_transcript_json, EvalRunConfig, TranscriptEvalResult
from app.evals.io import get_mengram_version
from app.evals.dataset import load_transcript_json


@dataclass
class SuiteEvalResult:
    schema_version: str
    run_id: str
    started_at: str
    finished_at: str
    mengram_version: str
    preset: str
    config_snapshot: dict
    transcripts: List[TranscriptEvalResult]
    passed: bool
    totals: dict

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mengram_version": self.mengram_version,
            "preset": self.preset,
            "config_snapshot": self.config_snapshot,
            "transcripts": [t.to_dict() for t in self.transcripts],
            "passed": self.passed,
            "totals": self.totals,
        }


def _snapshot_config(cfg: EvalRunConfig) -> dict:
    return {
        "schema_version": cfg.schema_version,
        "capture_drops": cfg.capture_drops,
        "capture_messages_preview": cfg.capture_messages_preview,
        "max_preview_chars": cfg.max_preview_chars,
        "fail_fast": cfg.fail_fast,
    }


def run_eval_suite(paths: List[str | Path], chat_factory: Callable[[], object], *, config: Optional[EvalRunConfig] = None, strict: bool = False, judge_llm_fn=None) -> SuiteEvalResult:
    cfg = config or EvalRunConfig()
    started = datetime.utcnow().isoformat()
    results: List[TranscriptEvalResult] = []
    errors = 0
    preset_name = None
    for p in paths:
        try:
            chat = chat_factory()
            res = run_transcript_json(p, chat, config=cfg, judge_llm_fn=judge_llm_fn)
            if preset_name is None:
                preset_name = res.preset or ""
            elif res.preset and preset_name != res.preset:
                preset_name = "mixed"
            results.append(res)
        except Exception:
            errors += 1
            if strict:
                raise
            continue
    finished = datetime.utcnow().isoformat()
    passed = all(r.passed for r in results) and errors == 0
    judge_scores = [r.judge_scores.get("avg") for r in results if r.judge_scores]
    totals = {
        "transcripts": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "turns": sum(len(r.turns) for r in results),
        "drops": sum(r.totals.get("drops", 0) for r in results),
        "tokens": sum(r.totals.get("tokens", 0) for r in results),
        "errors": errors,
        "judge_failures": sum(r.judge_failures for r in results),
        "judge_avg": (sum(judge_scores) / len(judge_scores)) if judge_scores else None,
    }
    return SuiteEvalResult(
        schema_version="suite.v1",
        run_id=uuid.uuid4().hex,
        started_at=started,
        finished_at=finished,
        mengram_version=get_mengram_version(),
        preset=preset_name or "",
        config_snapshot=_snapshot_config(cfg),
        transcripts=results,
        passed=passed,
        totals=totals,
    )


def run_eval_suite_dir(
    dir_path: str | Path,
    chat_factory: Callable[[], object],
    *,
    pattern: str = "*.json",
    recursive: bool = True,
    config: Optional[EvalRunConfig] = None,
    strict: bool = False,
    judge_llm_fn=None,
) -> SuiteEvalResult:
    base = Path(dir_path)
    if base.is_file():
        paths = [base]
    else:
        glob_pattern = "**/" + pattern if recursive else pattern
        paths = [Path(p) for p in glob.glob(str(base / glob_pattern), recursive=recursive)]
    return run_eval_suite(paths, chat_factory, config=config, strict=strict, judge_llm_fn=judge_llm_fn)
