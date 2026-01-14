"""Apply compiled filters to records or DataFrames."""

from __future__ import annotations

from typing import Any, Mapping, Sequence, Tuple
import json

from .filter_compiler import CompiledFilter, CompiledFilters
from .filter_evaluator import evaluate_rule


def apply_filters(data: Any, compiled: CompiledFilters) -> Any:
    """Apply compiled filters to data and return a filtered pandas DataFrame."""
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:
        raise RuntimeError("pandas is required to apply filters") from exc

    df = _to_dataframe(data, pd)
    if df.empty or not compiled:
        return df

    mask = pd.Series(True, index=df.index)
    for rule in compiled:
        rule_type = rule.get("type")
        if rule_type == "mapping":
            df = _apply_mapping(df, rule, pd)
        elif rule_type in {"comparison", "group"}:
            rule_mask, _nulls = evaluate_rule(df, rule, pd)
            mask = mask & rule_mask
        else:
            raise ValueError(f"Unsupported compiled filter type '{rule_type}'.")

    return df.loc[mask].reset_index(drop=True)


def _to_dataframe(data: Any, pd: Any) -> Any:
    if hasattr(data, "columns"):
        return data.copy()
    if isinstance(data, Mapping):
        data = [data]
    if isinstance(data, Sequence) and not isinstance(data, (str, bytes)):
        if not data:
            return pd.DataFrame()
        # Use DataFrame directly to preserve list/tuple cells (json_normalize flattens lists).
        return pd.DataFrame(list(data))
    raise TypeError("apply_filters expects a pandas DataFrame or a sequence of mappings.")


def _apply_mapping(df: Any, rule: CompiledFilter, pd: Any) -> Any:
    column = rule["column"]
    action = rule["action"]
    if action == "drop":
        if column in df.columns:
            return df.drop(columns=[column])
        return df
    if action == "rename":
        target = rule.get("new_name") or column
        if column in df.columns:
            df[target] = df[column]
            if target != column:
                df = df.drop(columns=[column])
        else:
            df[target] = pd.Series([None] * len(df), index=df.index)
        return df
    raise ValueError(f"Unknown mapping action '{action}'.")


__all__ = ["apply_filters"]
