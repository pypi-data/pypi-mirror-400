"""Compile structured filter definitions into normalized payloads."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple

from .filter_utils import normalize_op, require_str

CompiledFilter = Mapping[str, Any]
CompiledFilters = Tuple[CompiledFilter, ...]


def compile_filters(filter_definitions: Sequence[Mapping[str, Any]]) -> CompiledFilters:
    """Normalize user-provided filter rules into an immutable tuple."""

    if filter_definitions is None:
        return tuple()
    if not isinstance(filter_definitions, Sequence) or isinstance(filter_definitions, (str, bytes)):
        raise TypeError("Filter definitions must be a sequence of mappings.")

    compiled: list[CompiledFilter] = []
    for idx, rule in enumerate(filter_definitions):
        if not isinstance(rule, Mapping):
            raise TypeError(f"Filter rule at index {idx} must be a mapping.")
        rule_type = str(rule.get("type") or "").strip().lower()
        if not rule_type:
            raise ValueError(f"Filter rule at index {idx} is missing the 'type' field.")
        if rule_type == "mapping":
            compiled.append(_compile_mapping(rule, idx))
        elif rule_type == "comparison":
            compiled.append(_compile_comparison(rule, idx))
        elif rule_type == "group":
            compiled.append(_compile_group(rule, idx))
        else:
            raise ValueError(f"Unsupported filter type '{rule_type}' at index {idx}.")

    return tuple(compiled)


def _compile_mapping(rule: Mapping[str, Any], idx: int) -> CompiledFilter:
    column = require_str(rule, "column", idx)
    if "[" in column or "]" in column:
        raise ValueError(f"Mapping rule {idx} uses nested/path syntax; only direct columns are supported.")
    action = require_str(rule, "action", idx).lower()
    if action not in {"drop", "rename"}:
        raise ValueError(f"Mapping rule {idx} has invalid action '{action}'.")

    new_name = None
    if action == "rename":
        new_name = require_str(rule, "new_name", idx)

    compiled: dict[str, Any] = {"type": "mapping", "column": column, "action": action}
    if new_name:
        compiled["new_name"] = new_name
    if rule.get("description"):
        compiled["description"] = str(rule["description"])
    return compiled


def _compile_comparison(rule: Mapping[str, Any], idx: int) -> CompiledFilter:
    column = require_str(rule, "column", idx)
    op = normalize_op(rule.get("op"), idx)

    value_is_column = False
    value = rule.get("value")
    if "value_column" in rule:
        value = require_str(rule, "value_column", idx)
        value_is_column = True
    elif isinstance(value, Mapping) and "column" in value:
        value = require_str(value, "column", idx)
        value_is_column = True
    elif rule.get("value_is_column"):
        value = require_str(rule, "value", idx)
        value_is_column = True

    if value_is_column and op in {"in", "nin", "between"}:
        raise ValueError(f"Comparison rule {idx} uses op '{op}' which is incompatible with column-to-column comparisons.")

    if op in {"in", "nin"}:
        if isinstance(value, str) or not isinstance(value, Sequence):
            raise ValueError(f"Comparison rule {idx} with op '{op}' expects a list/tuple value.")
        value = list(value)
    elif op == "between":
        if isinstance(value, str) or not isinstance(value, Sequence) or len(value) != 2:
            raise ValueError("Between comparisons require a two-element sequence for 'value'.")
        value = [value[0], value[1]]

    compiled: dict[str, Any] = {
        "type": "comparison",
        "column": column,
        "op": op,
        "value": value,
        "keep_nulls": bool(rule.get("keep_nulls", False)),
    }
    if value_is_column:
        compiled["value_is_column"] = True
    if rule.get("description"):
        compiled["description"] = str(rule["description"])
    return compiled


def _compile_group(rule: Mapping[str, Any], idx: int) -> CompiledFilter:
    logic = require_str(rule, "logic", idx).lower()
    if logic not in {"and", "or"}:
        raise ValueError(f"Group rule {idx} has invalid logic '{logic}'.")

    raw_children = rule.get("rules")
    if not isinstance(raw_children, Sequence) or isinstance(raw_children, (str, bytes)):
        raise TypeError(f"Group rule {idx} must include a sequence of rules.")
    children: list[CompiledFilter] = []
    for child in raw_children:
        if not isinstance(child, Mapping):
            raise TypeError(f"Group rule {idx} contains a non-mapping child.")
        child_type = str(child.get("type") or "").strip().lower()
        if child_type == "mapping":
            raise ValueError("Mapping rules are not allowed inside groups.")
        if child_type == "comparison":
            children.append(_compile_comparison(child, idx))
        elif child_type == "group":
            children.append(_compile_group(child, idx))
        else:
            raise ValueError(f"Group rule {idx} contains unsupported child type '{child_type}'.")

    compiled: dict[str, Any] = {
        "type": "group",
        "logic": logic,
        "rules": tuple(children),
        "keep_nulls": bool(rule.get("keep_nulls", False)),
    }
    if rule.get("description"):
        compiled["description"] = str(rule["description"])
    return compiled


__all__ = ["CompiledFilter", "CompiledFilters", "compile_filters"]
