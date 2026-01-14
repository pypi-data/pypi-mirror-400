"""Public filter helpers exposed via the StreamingClient."""

from __future__ import annotations

from typing import Any, Mapping

from .filter_compiler import CompiledFilter, CompiledFilters, compile_filters
from .filter_runner import apply_filters


def explain_filter(filter_definition: Mapping[str, Any]) -> str:
    """Return a short human-readable description of a filter rule."""
    compiled = compile_filters([filter_definition])
    if not compiled:
        return ""
    return _describe(compiled[0])


def compile_filters_with_descriptions(filter_definitions: Mapping[str, Any] | Sequence[Mapping[str, Any]]) -> CompiledFilters:
    """Compile filters and auto-fill missing descriptions."""
    compiled = compile_filters(filter_definitions)  # type: ignore[arg-type]
    enriched: list[CompiledFilter] = []
    for rule in compiled:
        if rule.get("description"):
            enriched.append(rule)
            continue
        new_rule = dict(rule)
        new_rule["description"] = _describe(new_rule)
        enriched.append(new_rule)
    return tuple(enriched)


def _describe(rule: CompiledFilter) -> str:
    rule_type = rule.get("type")
    if rule_type == "mapping":
        column = rule["column"]
        target = rule.get("new_name") or column
        if rule.get("action") == "drop":
            return f"Drop column '{column}'"
        path = _format_path(rule.get("path") or ())
        if path:
            return f"Derive '{target}' from {column}{path}"
        return f"Rename '{column}' to '{target}'"
    if rule_type == "comparison":
        value = rule.get("value")
        rhs = f"column:{value}" if rule.get("value_is_column") else value
        return f"{rule.get('column')} {rule.get('op')} {rhs}"
    if rule_type == "group":
        joiner = " AND " if rule.get("logic") == "and" else " OR "
        parts = [f"{_describe(child)}" for child in rule.get("rules") or ()]
        return f"({joiner.join(parts)})"
    return str(rule)


def _format_path(tokens: Any) -> str:
    if not tokens:
        return ""
    segments = []
    for token in tokens:
        if isinstance(token, int):
            segments.append(f"[{token}]")
        else:
            segments.append(f".{token}" if segments else f".{token}")
    return "".join(segments)


__all__ = ["CompiledFilter", "CompiledFilters", "compile_filters", "explain_filter", "apply_filters"]
__all__ += ["compile_filters_with_descriptions"]
