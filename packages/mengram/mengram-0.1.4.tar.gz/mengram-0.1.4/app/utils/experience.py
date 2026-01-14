from typing import Any, Dict, Optional
import re
from typing import Any, Dict, Optional, List, Set

_whitespace_re = re.compile(r"\s+")

NOISY_ENV_KEYS = {"timestamp", "ts", "request_id", "session_id", "uuid"}


def dict_to_sorted_str(data: Optional[Dict[str, Any]]) -> str:
    if not data:
        return ""
    items = []
    for key in sorted(data.keys()):
        val = data[key]
        items.append(f"{key}:{val}")
    return "; ".join(items)


def summarize_state(env_state: Optional[Dict[str, Any]], internal_state: Optional[Dict[str, Any]]) -> str:
    env_part = dict_to_sorted_str(env_state)
    internal_part = dict_to_sorted_str(internal_state)
    return f"env: {env_part} | internal: {internal_part}"


def flatten_env(env_state: Optional[Dict[str, Any]], ignore_keys: Optional[Set[str]] = None) -> List[str]:
    """
    Deterministic env tokenization: flattens nested dicts into sorted key=value strings.
    """
    tokens: List[str] = []
    ignore = ignore_keys or NOISY_ENV_KEYS

    def _walk(prefix: str, val: Any):
        if isinstance(val, dict):
            for k in sorted(val.keys()):
                _walk(f"{prefix}.{k}" if prefix else k, val[k])
        elif isinstance(val, list):
            for idx, item in enumerate(val):
                _walk(f"{prefix}[{idx}]", item)
        else:
            if prefix in ignore:
                return
            tokens.append(f"{prefix}={val}")

    if env_state:
        _walk("", env_state)
    return tokens


def env_similarity(tokens_a: List[str], tokens_b: List[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    set_a: Set[str] = set(tokens_a)
    set_b: Set[str] = set(tokens_b)
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    if union == 0:
        return 0.0
    return inter / union
