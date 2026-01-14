from __future__ import annotations

import re
from typing import List, Tuple

from app.evals.dataset import ExpectedSpec


def build_check_text(messages: List[dict]) -> str:
    parts = []
    for m in messages:
        role = m.get("role", "")
        name = m.get("name")
        prefix = f"tool({name})" if role == "tool" and name else role
        parts.append(f"{prefix}: {m.get('content', '')}")
    return "\n".join(parts)


def eval_expected(
    check_text: str,
    expected: ExpectedSpec,
    golden_constraints: Tuple[str, ...],
    recalled_memories: List,
) -> Tuple[bool, List[str], int, List[str]]:
    reasons: List[str] = []
    constraints_matched: List[str] = []
    # must_contain
    for s in expected.must_contain:
        if s not in check_text:
            reasons.append(f"missing must_contain: {s}")
    # must_not_contain
    for s in expected.must_not_contain:
        if s in check_text:
            reasons.append(f"found forbidden text: {s}")
    # must_match_any
    if expected.must_match_any:
        if not any(re.search(p, check_text) for p in expected.must_match_any):
            reasons.append("must_match_any failed")
    # constraints hit
    hit = 0
    for c in golden_constraints:
        if c and c in check_text:
            hit += 1
            constraints_matched.append(c)
    if expected.min_constraint_hits is not None and hit < expected.min_constraint_hits:
        reasons.append(f"min_constraint_hits not met: {hit} < {expected.min_constraint_hits}")
    # should_reference_memories
    if expected.should_reference_memories:
        if recalled_memories:
            mem_texts = [getattr(m, "content", str(m)) for m in recalled_memories]
            if not any(mt in check_text for mt in mem_texts if mt):
                reasons.append("should_reference_memories but none referenced")
    return len(reasons) == 0, reasons, hit, constraints_matched
