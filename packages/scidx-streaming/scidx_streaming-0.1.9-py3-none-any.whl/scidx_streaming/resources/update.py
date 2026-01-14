"""Resource update helpers."""

from __future__ import annotations

from typing import Any, Mapping

from ..connectors.ckan import CKANActionError
from .utils import datasets, registry


def update_resource(
    ep_client: Any,
    resource_id: str,
    updates: Mapping[str, Any],
    *,
    server: str | None = None,
) -> Mapping[str, Any]:
    """Apply partial updates to a resource definition.

    Parameters
    ----------
    ep_client : Any (required)
        ndp_ep API client exposing dataset search/patch.
    resource_id : str (required)
        CKAN resource identifier.
    updates : Mapping[str, Any] (required)
        Fields to merge into the stored definition; ``None`` values are ignored.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        Updated CKAN resource entry.

    Raises
    ------
    CKANActionError
        If the resource cannot be located.
    ValueError
        If the updates are invalid.
    """

    dataset, scope, idx = datasets.locate_resource(ep_client, resource_id, preferred_scope=server)
    if dataset is None or idx is None:
        raise CKANActionError(f"Resource '{resource_id}' not found.")

    resources = list(dataset.get("resources") or [])
    stored = registry.load_definition_from_resource(resources[idx])
    merged = registry.merge_definitions(stored, updates)
    entry = registry.build_dataset_resource_entry(merged, resource_id=resource_id)
    resources[idx] = entry
    datasets.patch_resources(ep_client, dataset, resources, scope or server)
    return entry


def deactivate_resource(
    ep_client: Any,
    resource_id: str,
    *,
    reason: str | None = None,
    server: str | None = None,
) -> Mapping[str, Any]:
    """Soft-delete a resource by marking it inactive and preserving the record.

    Parameters
    ----------
    ep_client : Any (required)
        ndp_ep API client.
    resource_id : str (required)
        CKAN resource identifier.
    reason : str | None (optional, default None)
        Optional deactivation reason stored in metadata.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        Updated CKAN resource entry reflecting inactive state.
    """

    updates: dict[str, Any] = {"inactive": True, "preserve_record": True}
    if reason:
        updates["deactivation_reason"] = reason
    return update_resource(ep_client, resource_id, updates, server=server)


__all__ = ["deactivate_resource", "update_resource"]
