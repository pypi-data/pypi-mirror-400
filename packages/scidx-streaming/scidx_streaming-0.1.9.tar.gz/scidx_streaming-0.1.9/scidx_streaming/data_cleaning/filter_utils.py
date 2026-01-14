"""Helper utilities shared across filter modules."""

from __future__ import annotations

from typing import Any, Mapping

CANONICAL_OPS = {"eq", "neq", "gt", "gte", "lt", "lte", "in", "nin", "between"}
OP_ALIASES = {
    "==": "eq",
    "=": "eq",
    "eq": "eq",
    "!=": "neq",
    "<>": "neq",
    "ne": "neq",
    "neq": "neq",
    ">": "gt",
    "gt": "gt",
    ">=": "gte",
    "ge": "gte",
    "gte": "gte",
    "<": "lt",
    "lt": "lt",
    "<=": "lte",
    "le": "lte",
    "lte": "lte",
    "in": "in",
    "nin": "nin",
    "not in": "nin",
    "between": "between",
}


def normalize_op(op: Any, idx: int) -> str:
    normalized = str(op or "").strip().lower()
    canonical = OP_ALIASES.get(normalized)
    if canonical not in CANONICAL_OPS:
        raise ValueError(f"Comparison rule {idx} has invalid operator '{op}'.")
    return canonical


def require_str(rule: Mapping[str, Any], key: str, idx: int) -> str:
    value = rule.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Filter rule {idx} must include a non-empty string field '{key}'.")
    return value


def tokenize_path(expr: str) -> list[Any]:
    tokens: list[Any] = []
    current = ""
    i = 0
    while i < len(expr):
        char = expr[i]
        if char == ".":
            if current:
                tokens.append(current)
                current = ""
            i += 1
            continue
        if char == "[":
            if current:
                tokens.append(current)
                current = ""
            end = expr.find("]", i)
            if end == -1:
                break
            raw = expr[i + 1 : end]
            token = int(raw) if raw.isdigit() else raw
            tokens.append(token)
            i = end + 1
            continue
        current += char
        i += 1
    if current:
        tokens.append(current)
    return tokens


__all__ = ["CANONICAL_OPS", "OP_ALIASES", "normalize_op", "require_str", "tokenize_path"]
