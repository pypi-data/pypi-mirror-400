from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


SUPPORTED_SCHEMA_VERSIONS = {"v1"}


def _err(where: str, msg: str) -> ValueError:
    return ValueError(f"Invalid transcript{f' at {where}' if where else ''}: {msg}")


def _validate_list_of_str(val, where: str):
    if val is None:
        return ()
    if not isinstance(val, list):
        raise _err(where, f"expected list[str], got {type(val).__name__}")
    for idx, v in enumerate(val):
        if not isinstance(v, str):
            raise _err(f"{where}[{idx}]", f"expected string, got {type(v).__name__}")
    return tuple(val)


@dataclass(frozen=True)
class ToolSpec:
    name: str
    content: str
    pinned: bool = False
    kind: str = "tool_output"

    @classmethod
    def from_dict(cls, d: dict, *, where: str = "") -> "ToolSpec":
        if not isinstance(d, dict):
            raise _err(where, f"expected object, got {type(d).__name__}")
        name = d.get("name")
        content = d.get("content")
        if not isinstance(name, str) or not name:
            raise _err(f"{where}.name", f"must be a non-empty string (got {type(name).__name__})")
        if not isinstance(content, str) or not content:
            raise _err(f"{where}.content", f"must be a non-empty string (got {type(content).__name__})")
        pinned = d.get("pinned", False)
        if not isinstance(pinned, bool):
            raise _err(f"{where}.pinned", f"must be a bool (got {type(pinned).__name__})")
        kind = d.get("kind", "tool_output")
        if not isinstance(kind, str):
            raise _err(f"{where}.kind", f"must be a string (got {type(kind).__name__})")
        return cls(name=name, content=content, pinned=pinned, kind=kind)


@dataclass(frozen=True)
class ExpectedSpec:
    must_contain: tuple[str, ...]
    must_not_contain: tuple[str, ...]
    must_match_any: tuple[str, ...]
    min_constraint_hits: Optional[int] = None
    should_reference_memories: bool = False

    @classmethod
    def from_dict(cls, d: Optional[dict], *, where: str = "") -> "ExpectedSpec":
        if d is None:
            return cls(must_contain=[], must_not_contain=[], must_match_any=[])
        if not isinstance(d, dict):
            raise _err(where, f"expected object, got {type(d).__name__}")
        must_contain = _validate_list_of_str(d.get("must_contain", []), f"{where}.must_contain")
        must_not_contain = _validate_list_of_str(d.get("must_not_contain", []), f"{where}.must_not_contain")
        must_match_any = _validate_list_of_str(d.get("must_match_any", []), f"{where}.must_match_any")
        min_constraint_hits = d.get("min_constraint_hits", None)
        if min_constraint_hits is not None:
            if not isinstance(min_constraint_hits, int) or min_constraint_hits < 0:
                raise _err(f"{where}.min_constraint_hits", f"must be int >=0 or null (got {min_constraint_hits})")
        should_reference_memories = d.get("should_reference_memories", False)
        if not isinstance(should_reference_memories, bool):
            raise _err(f"{where}.should_reference_memories", f"must be bool (got {type(should_reference_memories).__name__})")
        return cls(
            must_contain=must_contain,
            must_not_contain=must_not_contain,
            must_match_any=must_match_any,
            min_constraint_hits=min_constraint_hits,
            should_reference_memories=should_reference_memories,
        )


@dataclass(frozen=True)
class TurnSpec:
    user: str
    tools: tuple[ToolSpec, ...]
    expected: ExpectedSpec
    notes: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict, *, where: str = "") -> "TurnSpec":
        if not isinstance(d, dict):
            raise _err(where, f"expected object, got {type(d).__name__}")
        user = d.get("user")
        if not isinstance(user, str) or not user:
            raise _err(f"{where}.user", f"must be a non-empty string (got {type(user).__name__})")
        tools_raw = d.get("tools", [])
        if tools_raw is None:
            tools_raw = []
        if not isinstance(tools_raw, list):
            raise _err(f"{where}.tools", f"must be a list (got {type(tools_raw).__name__})")
        tools = tuple(ToolSpec.from_dict(t, where=f"{where}.tools[{idx}]") for idx, t in enumerate(tools_raw))
        expected = ExpectedSpec.from_dict(d.get("expected", None), where=f"{where}.expected")
        notes = d.get("notes")
        if notes is not None and not isinstance(notes, str):
            raise _err(f"{where}.notes", f"must be a string if provided (got {type(notes).__name__})")
        return cls(user=user, tools=tools, expected=expected, notes=notes)


@dataclass(frozen=True)
class TranscriptSpec:
    schema_version: str
    name: str
    description: Optional[str]
    golden_constraints: tuple[str, ...]
    turns: tuple[TurnSpec, ...]

    @classmethod
    def from_dict(cls, d: dict, *, where: str = "") -> "TranscriptSpec":
        if not isinstance(d, dict):
            raise _err(where, f"expected object, got {type(d).__name__}")
        schema_version = d.get("schema_version")
        if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            raise _err(where, f"schema_version must be one of {sorted(SUPPORTED_SCHEMA_VERSIONS)} (got {schema_version})")
        name = d.get("name")
        if not isinstance(name, str) or not name:
            raise _err(f"{where}.name", f"must be a non-empty string (got {type(name).__name__})")
        description = d.get("description")
        if description is not None and not isinstance(description, str):
            raise _err(f"{where}.description", f"must be a string if provided (got {type(description).__name__})")
        golden_constraints = d.get("golden_constraints", [])
        if golden_constraints is None:
            golden_constraints = []
        golden_constraints = _validate_list_of_str(golden_constraints, f"{where}.golden_constraints")
        turns_raw = d.get("turns")
        if not isinstance(turns_raw, list) or not turns_raw:
            raise _err(f"{where}.turns", "must be a non-empty list")
        turns = tuple(TurnSpec.from_dict(t, where=f"{where}.turns[{idx}]") for idx, t in enumerate(turns_raw))
        return cls(
            schema_version=schema_version,
            name=name,
            description=description,
            golden_constraints=golden_constraints,
            turns=turns,
        )


def load_transcript_json(path: str | Path) -> TranscriptSpec:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise _err(str(p), f"invalid JSON: {e.msg} (line {e.lineno} col {e.colno})")
    return TranscriptSpec.from_dict(data, where=str(p))
