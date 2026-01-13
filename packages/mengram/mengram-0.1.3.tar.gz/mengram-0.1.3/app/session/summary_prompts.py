from __future__ import annotations

DEFAULT_SUMMARY_TEMPLATE = "generic.v1"

SUMMARY_TEMPLATES = {
    "generic.v1": """You are summarizing an AI agent conversation.
Rules:
- Do not invent facts. If unsure, mark as UNVERIFIED.
- Prefer exact strings for IDs/codes. Latest update wins; older becomes Superseded.
- Keep the summary under {max_summary_words} words. Be concise.

Produce sections with the following headings (use the headings verbatim):
- User Goal / Current Ask
- Stable Facts & Preferences
- Constraints (hard/soft)
- Key Decisions & Rationale
- Progress / What’s been done
- Open Questions / Blockers
- Tool Calls & Outcomes
- UNVERIFIED / Conflicting
- Next Step
"""
}


def get_summary_prompt(template_name: str) -> str:
    if template_name not in SUMMARY_TEMPLATES:
        available = ", ".join(sorted(SUMMARY_TEMPLATES.keys()))
        raise ValueError(f"Unknown summary template: {template_name}. Available: {available}")
    return SUMMARY_TEMPLATES[template_name]
