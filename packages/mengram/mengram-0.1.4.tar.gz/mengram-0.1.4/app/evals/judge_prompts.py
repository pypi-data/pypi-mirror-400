from __future__ import annotations

DEFAULT_JUDGE_TEMPLATE = "context_quality.v1"

JUDGE_TEMPLATES = {
    "context_quality.v1": """You are an evaluator of prompt/context quality.
Return STRICT JSON only with the schema:
{"score": 0.0-1.0, "verdict": "pass|fail|unknown", "reasons": ["..."], "flags": ["..."]}

Rubric:
- Constraint retention: are key constraints preserved?
- Contradictions: are there conflicts or losses?
- Tool output handling: avoid parroting raw tool blobs.
- Next action readiness: does the context contain what is needed?
""",
}


def get_judge_prompt(template_name: str) -> str:
    if template_name not in JUDGE_TEMPLATES:
        available = ", ".join(sorted(JUDGE_TEMPLATES.keys()))
        raise ValueError(f"Unknown judge template: {template_name}. Available: {available}")
    return JUDGE_TEMPLATES[template_name]
