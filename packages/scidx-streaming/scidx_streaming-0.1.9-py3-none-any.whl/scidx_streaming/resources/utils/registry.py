"""Helpers for storing simplified resource definitions inside CKAN resources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from . import common
from .types import api_stream, kafka, rss, static_file

NormalizerFn = Callable[[Mapping[str, Any], str], dict[str, Any]]
UrlBuilderFn = Callable[[Mapping[str, Any]], str | None]
ExtrasFn = Callable[[Mapping[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ResourceHandler:
    normalize: NormalizerFn
    build_url: UrlBuilderFn
    extras: ExtrasFn


def _normalize_static(payload: Mapping[str, Any], resource_type: str) -> dict[str, Any]:
    """Adapter that forwards to static_file.normalize with resource type."""
    return static_file.normalize(payload, resource_type=resource_type)


def _normalize_single(module_normalize: Callable[[Mapping[str, Any]], dict[str, Any]]) -> NormalizerFn:
    """Wrap a single-argument normalize function to match NormalizerFn signature."""
    def wrapped(payload: Mapping[str, Any], resource_type: str) -> dict[str, Any]:
        return module_normalize(payload)

    return wrapped


HANDLERS: dict[str, ResourceHandler] = {
    kafka.RESOURCE_TYPE: ResourceHandler(
        normalize=_normalize_single(kafka.normalize),
        build_url=kafka.build_url,
        extras=kafka.resource_extras,
    ),
    api_stream.RESOURCE_TYPE: ResourceHandler(
        normalize=_normalize_single(api_stream.normalize),
        build_url=api_stream.build_url,
        extras=api_stream.resource_extras,
    ),
    rss.RESOURCE_TYPE: ResourceHandler(
        normalize=_normalize_single(rss.normalize),
        build_url=rss.build_url,
        extras=rss.resource_extras,
    ),
}

for static_type in static_file.STATIC_FILE_TYPES:
    HANDLERS[static_type] = ResourceHandler(
        normalize=_normalize_static,
        build_url=static_file.build_url,
        extras=static_file.resource_extras,
    )

SUPPORTED_RESOURCE_TYPES: tuple[str, ...] = tuple(sorted(HANDLERS.keys()))
URL_BACKED_RESOURCE_TYPES: tuple[str, ...] = tuple(
    resource_type for resource_type in SUPPORTED_RESOURCE_TYPES if resource_type != kafka.RESOURCE_TYPE
)


def normalize_definition(raw_definition: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and normalize an input resource payload for CKAN storage."""
    if not isinstance(raw_definition, Mapping):
        raise ValueError("resource payload must be provided as a mapping.")

    payload = common.clean_payload(raw_definition)

    resource_type = common.require_text(payload.get("type"), "type").lower()
    handler = HANDLERS.get(resource_type)
    if handler is None:
        raise ValueError(f"Unsupported resource type '{resource_type}'.")

    description = common.require_text(payload.get("description"), "description")
    name = common.clean_text(payload.get("name")) or common.uuid_name()

    normalized: dict[str, Any] = {
        "type": resource_type,
        "description": description,
        "name": name,
    }

    if "inactive" in payload:
        normalized["inactive"] = bool(payload["inactive"])

    normalized.update(handler.normalize(payload, resource_type))

    for key, value in payload.items():
        if key in normalized:
            continue
        if key in {"type", "description", "name", "inactive"}:
            continue
        if key in {"mapping", "processing"}:
            continue
        normalized[key] = value

    return normalized


def merge_definitions(stored: Mapping[str, Any] | None, updates: Mapping[str, Any]) -> dict[str, Any]:
    """Merge stored definition with updates, then normalize."""
    base: dict[str, Any] = {}
    if isinstance(stored, Mapping):
        base.update(stored)
    if not isinstance(updates, Mapping):
        raise ValueError("updates must be a mapping.")
    base.update({k: v for k, v in updates.items() if v is not None})
    return normalize_definition(base)


def build_resource_payload(
    dataset_id: str,
    definition: Mapping[str, Any],
    *,
    existing_id: str | None = None,
) -> dict[str, Any]:
    """Construct a CKAN resource payload for dataset registration."""
    dataset_text = common.clean_text(dataset_id)
    if not dataset_text:
        raise ValueError("dataset_id is required.")

    handler = HANDLERS.get(str(definition.get("type") or "").lower())
    if handler is None:
        raise ValueError("Unknown resource type for payload construction.")

    encoded_definition = common.encode_definition(definition)

    payload = {
        "package_id": dataset_text,
        "name": common.require_text(definition.get("name"), "name"),
        "format": common.require_text(definition.get("type"), "type"),
        "description": encoded_definition,
        "method_definition": encoded_definition,
        "state": common.resource_state(definition),
    }

    url_value = handler.build_url(definition)
    if url_value:
        payload["url"] = url_value
    payload.update(handler.extras(definition))
    if existing_id:
        payload["id"] = existing_id
    return payload


load_definition_from_resource = common.load_definition_from_resource


def build_dataset_resource_entry(definition: Mapping[str, Any], *, resource_id: str | None = None) -> dict[str, Any]:
    """Construct a dataset 'resources' list entry from a normalized definition."""
    handler = HANDLERS.get(str(definition.get("type") or "").lower())
    if handler is None:
        raise ValueError("Unknown resource type for dataset resource entry.")

    encoded_definition = common.encode_definition(definition)
    entry = {
        "name": common.require_text(definition.get("name"), "name"),
        "format": common.require_text(definition.get("type"), "type"),
        "description": encoded_definition,
        "method_definition": encoded_definition,
        "state": common.resource_state(definition),
    }
    if resource_id:
        entry["id"] = resource_id
    url_value = handler.build_url(definition)
    if url_value:
        entry["url"] = url_value
    entry.update(handler.extras(definition))
    return entry


__all__ = [
    "SUPPORTED_RESOURCE_TYPES",
    "URL_BACKED_RESOURCE_TYPES",
    "build_dataset_resource_entry",
    "build_resource_payload",
    "load_definition_from_resource",
    "merge_definitions",
    "normalize_definition",
]
