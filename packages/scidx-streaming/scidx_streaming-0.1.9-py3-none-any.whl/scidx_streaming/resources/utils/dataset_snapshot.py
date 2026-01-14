"""Helpers for cloning dataset metadata/resources when recreating entries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ...connectors.ckan import CKANActionError
from . import common, registry

DATASET_FIELDS = ("name", "title", "notes", "owner_org", "private", "license_id", "version")


def clone_dataset(dataset: Mapping[str, Any], *, skip_resource_index: int | None = None) -> dict[str, Any]:
    """Return dataset metadata + resources, optionally skipping one resource.

    Parameters
    ----------
    dataset : Mapping[str, Any]
        Source CKAN dataset entry.
    skip_resource_index : int | None
        Optional index to exclude from the cloned resources list.

    Returns
    -------
    dict[str, Any]
        Cloned dataset payload safe for re-registration.

    Raises
    ------
    CKANActionError
        If required fields (name/title/owner_org) are missing.
    """

    metadata: dict[str, Any] = {}
    for field in DATASET_FIELDS:
        value = dataset.get(field)
        if value is not None:
            metadata[field] = value

    tags = _compact_named_entries(dataset.get("tags"))
    if tags:
        metadata["tags"] = tags

    groups = _compact_named_entries(dataset.get("groups"))
    if groups:
        metadata["groups"] = groups

    extras = _normalize_extras(dataset.get("extras"))
    if extras:
        metadata["extras"] = extras

    if not common.clean_text(metadata.get("name")):
        raise CKANActionError("Dataset name unavailable; cannot rebuild dataset.")
    if not common.clean_text(metadata.get("title")):
        raise CKANActionError("Dataset title unavailable; cannot rebuild dataset.")
    if not common.clean_text(metadata.get("owner_org")):
        raise CKANActionError("Dataset owner_org unavailable; cannot rebuild dataset.")

    metadata["resources"] = _clone_resources(dataset.get("resources") or [], skip_resource_index)
    return metadata


def _compact_named_entries(raw: Any) -> list[str]:
    """Normalize various tag/group structures into a list of names."""
    entries: list[str] = []
    if isinstance(raw, Mapping):
        for key in raw.keys():
            name = common.clean_text(key)
            if name:
                entries.append(name)
        return entries
    if isinstance(raw, (str, bytes)):
        name = common.clean_text(raw)
        if name:
            entries.append(name)
        return entries
    if isinstance(raw, Sequence):
        for value in raw:
            if isinstance(value, Mapping):
                name = common.clean_text(value.get("name") or value.get("display_name"))
            else:
                name = common.clean_text(value)
            if name:
                entries.append(name)
    return entries


def _normalize_extras(raw: Any) -> dict[str, Any]:
    """Normalize CKAN extras (mapping or list-of-maps) into a dict."""
    extras: dict[str, Any] = {}
    if isinstance(raw, Mapping):
        for key, value in raw.items():
            name = common.clean_text(key)
            if name:
                extras[name] = value
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
        for entry in raw:
            if not isinstance(entry, Mapping):
                continue
            key = common.clean_text(entry.get("key"))
            if key:
                extras[key] = entry.get("value")
    return extras


def _clone_resources(resources: Sequence[Mapping[str, Any]], skip_index: int | None) -> list[dict[str, Any]]:
    """Clone resources, optionally skipping one entry."""
    cloned: list[dict[str, Any]] = []
    for idx, resource in enumerate(resources):
        if skip_index is not None and idx == skip_index:
            continue
        try:
            definition = registry.load_definition_from_resource(resource)
            entry = registry.build_dataset_resource_entry(definition, resource_id=resource.get("id"))
        except Exception:
            entry = _sanitize_resource_entry(resource)
        cloned.append(entry)
    return cloned


def _sanitize_resource_entry(resource: Mapping[str, Any]) -> dict[str, Any]:
    """Strip unsupported fields from a raw CKAN resource entry."""
    disallowed = {
        "package_id",
        "revision_id",
        "package_name",
        "position",
        "tracking_summary",
        "created",
        "metadata_modified",
        "last_modified",
    }
    entry = {}
    for key, value in resource.items():
        if key in disallowed:
            continue
        if value is not None:
            entry[key] = value
    return entry


__all__ = ["clone_dataset"]
