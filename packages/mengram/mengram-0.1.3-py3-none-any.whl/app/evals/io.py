from __future__ import annotations

import json
import os
from importlib import metadata
from pathlib import Path


def read_json(path: str | Path):
    p = Path(path)
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON at {p}: {e.msg} (line {e.lineno} col {e.colno})") from e


def write_json_atomic(data, path: str | Path):
    p = Path(path)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, p)


def get_mengram_version() -> str:
    try:
        return metadata.version("mengram")
    except metadata.PackageNotFoundError:
        return "unknown"
