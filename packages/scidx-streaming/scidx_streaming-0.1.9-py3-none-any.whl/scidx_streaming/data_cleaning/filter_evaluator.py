"""Boolean evaluation for compiled filter rules."""

from __future__ import annotations

from typing import Any, Tuple

from .filter_compiler import CompiledFilter


def evaluate_rule(df: Any, rule: CompiledFilter, pd: Any) -> Tuple[Any, Any]:
    rule_type = rule["type"]
    if rule_type == "comparison":
        return _evaluate_comparison(df, rule, pd)
    if rule_type == "group":
        return _evaluate_group(df, rule, pd)
    raise ValueError(f"Unsupported rule type '{rule_type}' in evaluator.")


def _evaluate_comparison(df: Any, rule: CompiledFilter, pd: Any) -> Tuple[Any, Any]:
    column = rule["column"]
    series = df[column] if column in df.columns else pd.Series([None] * len(df), index=df.index)
    rhs_value = rule.get("value")
    rhs_series = None
    if rule.get("value_is_column"):
        rhs_series = df[rhs_value] if rhs_value in df.columns else pd.Series([None] * len(df), index=df.index)
        rhs_value = rhs_series

    op = rule["op"]
    if op == "eq":
        mask = series.eq(rhs_value)
    elif op == "neq":
        mask = series.ne(rhs_value)
    elif op == "gt":
        mask = series.gt(rhs_value)
    elif op == "gte":
        mask = series.ge(rhs_value)
    elif op == "lt":
        mask = series.lt(rhs_value)
    elif op == "lte":
        mask = series.le(rhs_value)
    elif op == "in":
        mask = series.isin(rhs_value)
    elif op == "nin":
        mask = ~series.isin(rhs_value)
    elif op == "between":
        low, high = rhs_value
        mask = series.ge(low) & series.le(high)
    else:
        raise ValueError(f"Unsupported comparison operator '{op}'.")

    null_mask = series.isna()
    if rhs_series is not None:
        null_mask = null_mask | rhs_series.isna()

    keep_nulls = bool(rule.get("keep_nulls", False))
    if keep_nulls:
        mask = mask | null_mask
    else:
        mask = mask & ~null_mask

    return mask.fillna(False), null_mask


def _evaluate_group(df: Any, rule: CompiledFilter, pd: Any) -> Tuple[Any, Any]:
    children = rule.get("rules") or tuple()
    if not children:
        empty = pd.Series(True, index=df.index)
        return empty, pd.Series(False, index=df.index)

    masks = []
    nulls = []
    for child in children:
        child_mask, child_nulls = evaluate_rule(df, child, pd)
        masks.append(child_mask)
        nulls.append(child_nulls)

    combined = masks[0]
    if rule.get("logic") == "and":
        for other in masks[1:]:
            combined = combined & other
    else:
        for other in masks[1:]:
            combined = combined | other

    all_nulls = nulls[0]
    for other in nulls[1:]:
        all_nulls = all_nulls & other

    if rule.get("keep_nulls"):
        combined = combined | all_nulls

    return combined.fillna(False), all_nulls


__all__ = ["evaluate_rule"]
