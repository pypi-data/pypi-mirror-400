"""Resource registration helpers."""

from __future__ import annotations

from typing import Any, Mapping

from ..connectors.ckan import CKANActionError
from .utils import common, datasets, registry


def register_resource(
    ep_client: Any,
    dataset_id: str,
    resource_payload: Mapping[str, Any],
    *,
    server: str | None = None,
) -> Mapping[str, Any]:
    """Register or upsert a resource on an existing dataset.

    Parameters
    ----------
    ep_client : Any (required)
        ndp_ep API client exposing dataset actions.
    dataset_id : str (required)
        CKAN dataset identifier/slug.
    resource_payload : Mapping[str, Any] (required)
        Raw resource definition; normalized before storage.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        CKAN resource entry returned after patch/re-fetch.

    Raises
    ------
    CKANActionError
        When the dataset does not exist.
    ValueError
        When the payload cannot be normalized.
    """

    definition = registry.normalize_definition(resource_payload)
    dataset, scope = datasets.fetch_dataset(ep_client, dataset_id, preferred_scope=server)
    if dataset is None:
        raise CKANActionError(f"Dataset '{dataset_id}' not found.")

    resources = list(dataset.get("resources") or [])
    resource_id = str(definition.get("id") or common.uuid_name())
    entry = registry.build_dataset_resource_entry(definition, resource_id=resource_id)

    idx = datasets.resource_index(resources, resource_id=resource_id, name=entry.get("name"))
    if idx is None:
        resources.append(entry)
    else:
        resources[idx] = entry

    datasets.patch_resources(ep_client, dataset, resources, scope or server)

    # Re-fetch to return the authoritative CKAN resource entry (captures CKAN-assigned IDs).
    refreshed, _ = datasets.fetch_dataset(ep_client, dataset_id, preferred_scope=scope or server)
    if refreshed:
        refreshed_resources = refreshed.get("resources") or []
        resolved_idx = datasets.resource_index(
            refreshed_resources,
            resource_id=entry.get("id"),
            name=entry.get("name"),
        )
        if resolved_idx is not None:
            return refreshed_resources[resolved_idx]

    return entry


__all__ = ["register_resource"]
