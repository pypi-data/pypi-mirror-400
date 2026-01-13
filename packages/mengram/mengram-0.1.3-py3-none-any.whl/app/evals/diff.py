from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DiffItem:
    transcript_name: str
    before_passed: bool
    after_passed: bool
    before_first_failure: Optional[dict]
    after_first_failure: Optional[dict]

    def to_dict(self):
        return {
            "transcript_name": self.transcript_name,
            "before_passed": self.before_passed,
            "after_passed": self.after_passed,
            "before_first_failure": self.before_first_failure,
            "after_first_failure": self.after_first_failure,
        }


@dataclass
class DiffResult:
    schema_version: str
    before_run_id: Optional[str]
    after_run_id: Optional[str]
    regressions_count: int
    fixes_count: int
    regressions: List[DiffItem]
    fixes: List[DiffItem]
    still_failing: List[DiffItem]
    still_passing: List[DiffItem]
    metric_deltas: dict
    summary: str

    def to_dict(self):
        return {
            "schema_version": self.schema_version,
            "before_run_id": self.before_run_id,
            "after_run_id": self.after_run_id,
            "regressions_count": self.regressions_count,
            "fixes_count": self.fixes_count,
            "regressions": [r.to_dict() for r in self.regressions],
            "fixes": [f.to_dict() for f in self.fixes],
            "still_failing": [s.to_dict() for s in self.still_failing],
            "still_passing": [s.to_dict() for s in self.still_passing],
            "metric_deltas": self.metric_deltas,
            "summary": self.summary,
        }


def _first_failure(turns):
    for t in turns:
        if not t.get("expectations_passed", True):
            reason = t.get("fail_reasons") or []
            return {"turn_index": t.get("turn_index"), "reasons": reason}
    return None


def diff_eval_results(before: dict, after: dict) -> DiffResult:
    def normalize_suite(suite: dict) -> dict:
        clean = dict(suite)
        for k in ["started_at", "finished_at"]:
            clean.pop(k, None)
        return clean

    before_norm = normalize_suite(before)
    after_norm = normalize_suite(after)

    regressions: List[DiffItem] = []
    fixes: List[DiffItem] = []
    still_failing: List[DiffItem] = []
    still_passing: List[DiffItem] = []

    before_map = {t["transcript_name"]: t for t in before_norm.get("transcripts", [])}
    after_map = {t["transcript_name"]: t for t in after_norm.get("transcripts", [])}
    all_names = set(before_map.keys()) | set(after_map.keys())

    for name in sorted(all_names):
        b = before_map.get(name)
        a = after_map.get(name)
        b_pass = b.get("passed") if b else False
        a_pass = a.get("passed") if a else False
        item = DiffItem(
            transcript_name=name,
            before_passed=b_pass,
            after_passed=a_pass,
            before_first_failure=_first_failure(b["turns"]) if b else None,
            after_first_failure=_first_failure(a["turns"]) if a else None,
        )
        if b_pass and not a_pass:
            regressions.append(item)
        elif not b_pass and a_pass:
            fixes.append(item)
        elif not b_pass and not a_pass:
            still_failing.append(item)
        else:
            still_passing.append(item)

    def _metric(suite, key):
        return suite.get("totals", {}).get(key, 0)

    metric_deltas = {
        "drops": _metric(after_norm, "drops") - _metric(before_norm, "drops"),
        "tokens": _metric(after_norm, "tokens") - _metric(before_norm, "tokens"),
        "failed": _metric(after_norm, "failed") - _metric(before_norm, "failed"),
        "passed": _metric(after_norm, "passed") - _metric(before_norm, "passed"),
        "judge_failures": _metric(after_norm, "judge_failures") - _metric(before_norm, "judge_failures"),
    }
    summary = f"regressions={len(regressions)}, fixes={len(fixes)}, failed_delta={metric_deltas['failed']}"
    return DiffResult(
        schema_version="diff.v1",
        before_run_id=before.get("run_id"),
        after_run_id=after.get("run_id"),
        regressions_count=len(regressions),
        fixes_count=len(fixes),
        regressions=regressions,
        fixes=fixes,
        still_failing=still_failing,
        still_passing=still_passing,
        metric_deltas=metric_deltas,
        summary=summary,
    )


def diff_eval_result_json(before_path: str, after_path: str, reader=None) -> DiffResult:
    if reader is None:
        from app.evals.io import read_json

        reader = read_json
    before = reader(before_path)
    after = reader(after_path)
    return diff_eval_results(before, after)
