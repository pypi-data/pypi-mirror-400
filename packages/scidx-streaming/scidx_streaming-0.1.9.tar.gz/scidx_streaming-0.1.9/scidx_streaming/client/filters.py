"""Filter helpers for ``StreamingClient``."""

from __future__ import annotations

from typing import Mapping, Sequence

from ..data_cleaning import CompiledFilters, compile_filters as _compile_filters


def compile_filters(self: "StreamingClient", filter_definitions: Sequence[Mapping[str, object]]) -> CompiledFilters:
    """Normalize and validate high-level filter rules before stream creation.

    Parameters
    ----------
    filter_definitions : Sequence[Mapping[str, object]]
        Iterable of filter rules. These can be human-friendly entries (plain
        text/loosely structured dicts) that will be normalized into machine-
        readable rules shaped like ``{"field": ..., "op": ..., "value": ...}``.

    Returns
    -------
    CompiledFilters
        Immutable, validated filter tuple ready to attach to ``create_stream``.

    Notes
    -----
    The current backend raises ``NotImplementedError`` (DSL is being finalized),
    but keeping this call in place ensures downstream code is wired correctly.
    """

    return _compile_filters(filter_definitions)
