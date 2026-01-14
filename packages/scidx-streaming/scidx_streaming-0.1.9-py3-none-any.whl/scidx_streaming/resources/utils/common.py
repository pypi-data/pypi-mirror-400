"""Shared helpers for normalizing resource definitions."""

from __future__ import annotations

import json
from typing import Any, Mapping
from uuid import uuid4


def clean_text(value: Any) -> str:
    """Return a stripped string representation of ``value`` (empty when falsy)."""
    return str(value or "").strip()


def require_text(value: Any, field: str) -> str:
    """Return cleaned text or raise ``ValueError`` if missing."""
    text = clean_text(value)
    if not text:
        raise ValueError(f"{field} is required.")
    return text


def normalize_port(value: Any) -> int:
    """Coerce a port value to a positive int, raising ``ValueError`` on failure."""
    if isinstance(value, int):
        if value <= 0:
            raise ValueError("port must be a positive integer.")
        return value
    text = clean_text(value)
    if not text:
        raise ValueError("port is required.")
    if not text.isdigit():
        raise ValueError("port must be an integer.")
    port = int(text)
    if port <= 0:
        raise ValueError("port must be a positive integer.")
    return port


def as_mapping(value: Any) -> Mapping[str, Any]:
    """Return ``value`` if it is a mapping, otherwise an empty dict."""
    if isinstance(value, Mapping):
        return value
    return {}


def uuid_name() -> str:
    """Return a random UUID hex string for naming resources."""
    return uuid4().hex


def clean_payload(values: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a resource payload: drop ``None``, stringify keys, hoist config."""
    cleaned: dict[str, Any] = {}
    for key, value in values.items():
        if value is None:
            continue
        if isinstance(key, str):
            cleaned[key] = value
        else:
            cleaned[str(key)] = value
    config = as_mapping(cleaned.pop("config", None))
    for field, raw in config.items():
        cleaned.setdefault(str(field), raw)
    return cleaned


def encode_definition(definition: Mapping[str, Any]) -> str:
    """Serialize a resource definition dict to a stable JSON string."""
    return json.dumps(definition, sort_keys=True)


def decode_definition(raw: Any) -> dict[str, Any]:
    """Deserialize a JSON string or mapping into a definition dict (or empty)."""
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if isinstance(parsed, Mapping):
            return dict(parsed)
        return {}
    if isinstance(raw, Mapping):
        return dict(raw)
    return {}


def load_definition_from_resource(resource: Mapping[str, Any]) -> dict[str, Any]:
    """Extract the normalized definition from a CKAN resource entry."""
    definition = decode_definition(resource.get("description"))
    if not definition:
        legacy = decode_definition(resource.get("method_definition"))
        if legacy:
            definition = legacy
    if not definition.get("type"):
        definition["type"] = clean_text(resource.get("format")).lower() or None
    if not definition.get("name") and resource.get("name"):
        definition["name"] = clean_text(resource.get("name"))
    if not definition.get("description") and isinstance(resource.get("description"), str):
        definition["description"] = resource["description"]
    return {key: value for key, value in definition.items() if value is not None}


def resource_state(definition: Mapping[str, Any]) -> str:
    """Return 'inactive' when definition has inactive flag, else 'active'."""
    return "inactive" if definition.get("inactive") else "active"


__all__ = [
    "as_mapping",
    "clean_payload",
    "clean_text",
    "decode_definition",
    "encode_definition",
    "load_definition_from_resource",
    "normalize_port",
    "require_text",
    "resource_state",
    "uuid_name",
]
