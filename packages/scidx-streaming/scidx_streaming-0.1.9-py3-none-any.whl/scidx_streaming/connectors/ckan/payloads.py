"""Serialization helpers for CKAN payloads."""

from __future__ import annotations

import json
from typing import Any, Dict, Mapping


def normalize_payload(base: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a JSON-serializable payload without mutating ``base``.

    Parameters
    ----------
    base : Mapping[str, Any]
        Potentially nested payload to sanitize.

    Returns
    -------
    Dict[str, Any]
        JSON-safe copy (nested mappings normalized, other values serialized when possible).

    Raises
    ------
    ValueError
        When a value cannot be serialized.
    """

    normalized: Dict[str, Any] = {}
    for key, value in base.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            normalized[key] = value
        elif isinstance(value, Mapping):
            normalized[key] = normalize_payload(value)
        else:
            try:
                normalized[key] = json.loads(json.dumps(value))
            except Exception as exc:  # pragma: no cover - defensive fallback
                raise ValueError(f"Unsupported value for key '{key}': {value!r}") from exc
    return normalized


__all__ = ["normalize_payload"]
