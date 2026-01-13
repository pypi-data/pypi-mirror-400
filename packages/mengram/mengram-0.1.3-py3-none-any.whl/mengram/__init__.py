"""
Primary public package surface for mengram.

Exports:
- MemoryClient: programmatic API for memories/rules/events/experiences
- init_memory_os_schema: creates required tables (idempotent)
- Interaction / MemoryCandidate: data models for auto-ingest
- LLMMemoryExtractor: reference LLM-based extractor
- RuleCondition / NotifyAction / InjectMemoryAction: prospective rules
- ExperienceIn / ExperienceOut: procedural memory traces
"""

from app.auto import Interaction, MemoryCandidate, LLMMemoryExtractor, interactions_from_dicts
from app.core import MemoryClient
from app.db.init_db import init_memory_os_schema
from app.rules.models import RuleCondition, NotifyAction, InjectMemoryAction, RuleEvaluationResult, RuleOut
from app.session.context import ContextBuilder
from app.session.models import SessionItem, Summarizer
from app.session.budget import TokenBudgetPolicy, ContextBuildReport, DropEvent
from app.session.tokens import TokenCounter
from app.session.session import SummarizingSession
from app.session.summarizer import SummarizerConfig, LLMSummarizer
from app.session.summary_prompts import DEFAULT_SUMMARY_TEMPLATE, get_summary_prompt
from app.chat import ChatMemory, ChatStepResult, ChatMemoryConfig, get_preset
from app.evals.dataset import TranscriptSpec, TurnSpec, ToolSpec, ExpectedSpec, load_transcript_json
from app.evals.runner import run_transcript_json, run_transcript_spec, EvalRunConfig, TranscriptEvalResult, TurnEvalResult
from app.evals.suite import SuiteEvalResult, run_eval_suite, run_eval_suite_dir
from app.evals.diff import DiffResult, DiffItem, diff_eval_results, diff_eval_result_json
from app.evals.io import write_json_atomic as write_eval_result_json, read_json as read_eval_result_json
from app.evals.judge import JudgeConfig, JudgeResult, JudgeRunner
from app.evals.judge_prompts import DEFAULT_JUDGE_TEMPLATE, get_judge_prompt
from app.schemas.experience import ExperienceIn, ExperienceOut

__all__ = [
    "MemoryClient",
    "init_memory_os_schema",
    "Interaction",
    "MemoryCandidate",
    "LLMMemoryExtractor",
    "interactions_from_dicts",
    "RuleCondition",
    "NotifyAction",
    "InjectMemoryAction",
    "RuleEvaluationResult",
    "RuleOut",
    "ExperienceIn",
    "ExperienceOut",
    "SessionItem",
    "SummarizingSession",
    "ContextBuilder",
    "Summarizer",
    "TokenBudgetPolicy",
    "ContextBuildReport",
    "DropEvent",
    "TokenCounter",
    "SummarizerConfig",
    "LLMSummarizer",
    "DEFAULT_SUMMARY_TEMPLATE",
    "get_summary_prompt",
    "ChatMemory",
    "ChatStepResult",
    "ChatMemoryConfig",
    "get_preset",
    "TranscriptSpec",
    "TurnSpec",
    "ToolSpec",
    "ExpectedSpec",
    "load_transcript_json",
    "run_transcript_json",
    "run_transcript_spec",
    "EvalRunConfig",
    "TranscriptEvalResult",
    "TurnEvalResult",
    "SuiteEvalResult",
    "run_eval_suite",
    "run_eval_suite_dir",
    "DiffResult",
    "DiffItem",
    "diff_eval_results",
    "diff_eval_result_json",
    "write_eval_result_json",
    "read_eval_result_json",
    "JudgeConfig",
    "JudgeResult",
    "JudgeRunner",
    "DEFAULT_JUDGE_TEMPLATE",
    "get_judge_prompt",
]
