"""Filter compilation and application behaviour."""

from __future__ import annotations

from scidx_streaming.data_cleaning import (
    apply_filters,
    compile_filters,
    compile_filters_with_descriptions,
    explain_filter,
)


def test_mapping_with_path_and_station_filtering() -> None:
    filters = [
        {"type": "mapping", "column": "SNCL", "action": "rename", "new_name": "station"},
        {"type": "mapping", "column": "coor", "action": "drop"},
        {"type": "comparison", "column": "station", "op": "in", "value": ["AAA", "BBB"]},
    ]
    compiled = compile_filters(filters)
    records = [
        {"SNCL": "AAA", "coor": [1, 2, 3]},
        {"SNCL": "CCC", "coor": [4, 5, 6]},
        {"SNCL": "BBB", "coor": [7, 8, 9]},
    ]
    df = apply_filters(records, compiled)
    assert list(df["station"]) == ["AAA", "BBB"]
    assert "coor" not in df.columns


def test_column_comparison_and_group_null_passthrough() -> None:
    compiled = compile_filters(
        [
            {"type": "comparison", "column": "a", "op": "gt", "value": {"column": "b"}},
            {
                "type": "group",
                "logic": "and",
                "keep_nulls": True,
                "rules": [{"type": "comparison", "column": "missing", "op": "eq", "value": 1}],
            },
        ]
    )
    rows = [{"a": 2, "b": 1}, {"a": None, "b": 1}, {"a": 1, "b": 2}]
    df = apply_filters(rows, compiled)
    assert list(df["a"]) == [2.0]
    assert "missing" not in df.columns

    null_only = compile_filters(
        [
            {
                "type": "group",
                "logic": "and",
                "keep_nulls": True,
                "rules": [{"type": "comparison", "column": "missing", "op": "eq", "value": 1}],
            }
        ]
    )
    null_df = apply_filters(rows, null_only)
    assert len(null_df) == len(rows)

    description = explain_filter({"type": "comparison", "column": "a", "op": "gte", "value": 0})
    assert "a" in description


def test_auto_description_generation() -> None:
    compiled = compile_filters_with_descriptions(
        [{"type": "comparison", "column": "rate", "op": "gt", "value": 0}]
    )
    assert compiled[0].get("description")
