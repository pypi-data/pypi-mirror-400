"""Dataset lookup helpers used by the resource actions."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any

from ...connectors.ckan import CKANActionError, call_action
from . import common

_RESOURCE_HINTS: dict[str, dict[str, str | None]] = {}


def fetch_dataset(
    ep_client: Any,
    dataset_ref: str,
    *,
    preferred_scope: str | None,
) -> tuple[Mapping[str, Any] | None, str | None]:
    """Fetch a dataset by id/slug across scopes, returning (dataset, scope)."""
    for entry, scope in _iter_datasets(ep_client, dataset_names=[dataset_ref], preferred_scope=preferred_scope):
        if entry.get("name") == dataset_ref or entry.get("id") == dataset_ref:
            return entry, scope
    return None, None


def locate_resource(
    ep_client: Any,
    resource_id: str,
    *,
    preferred_scope: str | None,
) -> tuple[Mapping[str, Any] | None, str | None, int | None]:
    """Locate a resource by id across datasets/scopes; return (dataset, scope, index)."""

    # Fast path: ask CKAN for the resource and jump straight to its dataset.
    dataset, scope, idx = _fetch_resource(ep_client, resource_id, preferred_scope)
    if dataset is not None and idx is not None:
        return dataset, scope, idx

    hint = resource_hint(resource_id)
    if hint:
        for dataset_ref in (hint.get("dataset_id"), hint.get("dataset_name")):
            if not dataset_ref:
                continue
            dataset, scope = fetch_dataset(ep_client, dataset_ref, preferred_scope=preferred_scope)
            if dataset:
                resources = dataset.get("resources") or []
                idx = resource_index(resources, resource_id=resource_id)
                if idx is not None:
                    return dataset, scope, idx

    for dataset, scope in _iter_datasets(ep_client, preferred_scope=preferred_scope):
        resources = dataset.get("resources") or []
        idx = resource_index(resources, resource_id=resource_id)
        if idx is not None:
            return dataset, scope, idx
    return None, None, None


def find_resources_by_name(
    ep_client: Any,
    resource_name: str,
    *,
    dataset_names: Iterable[str] | None = None,
    preferred_scope: str | None = None,
) -> list[tuple[Mapping[str, Any], str | None, int]]:
    """Return all dataset/resource matches for the provided resource name."""

    target = common.clean_text(resource_name)
    matches: list[tuple[Mapping[str, Any], str | None, int]] = []
    if not target:
        return matches

    for dataset, scope in _iter_datasets(ep_client, dataset_names=dataset_names, preferred_scope=preferred_scope):
        resources = dataset.get("resources") or []
        idx = resource_index(resources, name=target)
        if idx is not None:
            matches.append((dataset, scope, idx))
    return matches


def patch_resources(
    ep_client: Any,
    dataset: Mapping[str, Any],
    resources: Sequence[Mapping[str, Any]],
    scope: str | None,
) -> None:
    """Patch the resources list on a dataset via ndp_ep.patch_general_dataset."""
    patcher = getattr(ep_client, "patch_general_dataset", None)
    if not callable(patcher):
        raise CKANActionError("ndp_ep client does not support patch_general_dataset.")

    dataset_identifier = dataset.get("id") or dataset.get("name")
    if not dataset_identifier:
        raise CKANActionError("Dataset identifier is unavailable; cannot update resources.")

    patcher(dataset_identifier, {"resources": list(resources)}, server=scope)


def resource_index(
    resources: Sequence[Mapping[str, Any]],
    *,
    resource_id: str | None = None,
    name: str | None = None,
) -> int | None:
    """Return the index of a resource matching id or name inside a resources list."""
    resource_id_text = common.clean_text(resource_id) if resource_id else None
    name_text = common.clean_text(name) if name else None
    for idx, resource in enumerate(resources):
        if resource_id_text and common.clean_text(resource.get("id")) == resource_id_text:
            return idx
        if name_text and common.clean_text(resource.get("name")) == name_text:
            return idx
    return None


def _iter_datasets(
    ep_client: Any,
    *,
    dataset_names: Iterable[str] | None = None,
    preferred_scope: str | None,
) -> Iterator[tuple[Mapping[str, Any], str | None]]:
    """Yield (dataset, scope) across preferred/local/global scopes, filtered by names."""
    searcher = getattr(ep_client, "search_datasets", None)
    if not callable(searcher):
        return iter(())

    scopes: list[str] = []
    if preferred_scope:
        scopes.append(preferred_scope)
    for scope in ("local", "global"):
        if scope not in scopes:
            scopes.append(scope)

    targets = {str(name) for name in dataset_names} if dataset_names else None
    queries = list(targets or [])
    if not queries:
        queries = ["", "*"]

    seen_ids: set[str] = set()
    for scope in scopes or [None]:
        for query in queries:
            try:
                results = searcher([query], server=scope)
            except Exception:
                continue
            for entry in results or []:
                name = str(entry.get("name") or "")
                identifier = str(entry.get("id") or name)
                if targets and identifier not in targets and name not in targets:
                    continue
                if identifier in seen_ids:
                    continue
                seen_ids.add(identifier)
                _remember_dataset(entry)
                yield entry, scope


def remember_resource_hint(resource: Mapping[str, Any], dataset: Mapping[str, Any]) -> None:
    """Store dataset/name hints for a resource ID."""

    resource_id = common.clean_text(resource.get("id"))
    if not resource_id:
        return
    _RESOURCE_HINTS[resource_id] = {
        "dataset_name": common.clean_text(dataset.get("name")) or None,
        "dataset_id": common.clean_text(dataset.get("id")) or None,
        "resource_name": common.clean_text(resource.get("name")) or None,
    }


def resource_hint(resource_id: str) -> dict[str, str | None] | None:
    """Return cached dataset/name info for a resource ID."""

    return _RESOURCE_HINTS.get(common.clean_text(resource_id))


def forget_resource_hint(resource_id: str) -> None:
    """Remove cached metadata for a resource ID."""

    _RESOURCE_HINTS.pop(common.clean_text(resource_id), None)


def _remember_dataset(dataset: Mapping[str, Any]) -> None:
    """Cache hints for all resources in a dataset."""
    for resource in dataset.get("resources") or []:
        remember_resource_hint(resource, dataset)


def _fetch_resource(
    ep_client: Any,
    resource_id: str,
    preferred_scope: str | None,
) -> tuple[Mapping[str, Any] | None, str | None, int | None]:
    """Use CKAN resource_show via ndp_ep to resolve dataset/id quickly."""
    try:
        result = call_action(ep_client, "resource_show", {"id": resource_id}, server=preferred_scope)
    except Exception:
        return None, None, None

    dataset_ref = result.get("package_id") or result.get("dataset_id") or result.get("package_name")
    if not dataset_ref:
        return None, None, None

    dataset, scope = fetch_dataset(ep_client, dataset_ref, preferred_scope=preferred_scope)
    if not dataset:
        return None, None, None

    resources = dataset.get("resources") or []
    idx = resource_index(resources, resource_id=resource_id)
    if idx is None:
        return None, None, None
    return dataset, scope, idx


__all__ = [
    "fetch_dataset",
    "find_resources_by_name",
    "forget_resource_hint",
    "locate_resource",
    "patch_resources",
    "remember_resource_hint",
    "resource_hint",
    "resource_index",
]
