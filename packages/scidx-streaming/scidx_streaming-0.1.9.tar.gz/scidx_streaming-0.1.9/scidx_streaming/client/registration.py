"""Resource registration helpers attached to ``StreamingClient``."""

from __future__ import annotations

from typing import Mapping

from ..connectors.ckan import CKANActionError
from ..resources import (
    deactivate_resource as _deactivate_resource,
    delete_resource as _delete_resource,
    delete_resource_by_name as _delete_resource_by_name,
    register_resource as _register_resource,
    update_resource as _update_resource,
)


def register_resource(
    self: "StreamingClient",
    dataset_id: str,
    resource_payload: Mapping[str, object],
    *,
    server: str | None = None,
):
    """Register a single resource definition on an existing dataset.

    Parameters
    ----------
    dataset_id : str (required)
        CKAN dataset identifier.
    resource_payload : Mapping[str, object] (required)
        Normalized payload (type/name/description + specific config by type).
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        CKAN resource entry (authoritative after CKAN re-fetch).
    """

    return _register_resource(self.ep_client, dataset_id, resource_payload, server=server)


def update_resource(
    self: "StreamingClient",
    resource_id: str,
    updates: Mapping[str, object],
    *,
    server: str | None = None,
):
    """Apply partial updates to a resource definition.

    Parameters
    ----------
    resource_id : str (required)
        Target resource identifier.
    updates : Mapping[str, object] (required)
        Fields to merge into the stored definition.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        Updated CKAN resource entry.
    """

    return _update_resource(self.ep_client, resource_id, updates, server=server)


def deactivate_resource(
    self: "StreamingClient",
    resource_id: str,
    *,
    reason: str | None = None,
    server: str | None = None,
):
    """Mark a resource as inactive (soft delete) with optional metadata.

    Parameters
    ----------
    resource_id : str (required)
        Target resource identifier.
    reason : str | None (optional, default None)
        Optional deactivation reason stored on the resource.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        Updated CKAN resource entry reflecting inactivity.
    """

    return _deactivate_resource(
        self.ep_client,
        resource_id,
        reason=reason,
        server=server,
    )


def delete_resource(
    self: "StreamingClient",
    resource: str,
    *,
    dataset_id: str | None = None,
    server: str | None = None,
):
    """Delete a resource by id or name, with optional dataset scoping.

    Parameters
    ----------
    resource : str (required)
        Resource identifier (id or name). If treated as a name, duplicate names
        will prompt a conflict summary and no deletion will occur until the
        call is repeated with a dataset_id or explicit id.
    dataset_id : str | None (optional, default None)
        Dataset id/slug to disambiguate duplicate names when deleting by name.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Returns
    -------
    None
        Deletes in place; returns None. On name conflicts, prints guidance.

    Notes
    -----
    - First attempts deletion as an id.
    - If not found, falls back to name-based deletion (with optional dataset scope).
    - When multiple matches exist for a name and no dataset_id is provided, a
      conflict summary is printed and nothing is deleted.
    """

    errors: list[str] = []
    try:
        return _delete_resource(self.ep_client, resource, server=server)
    except CKANActionError as exc:
        errors.append(str(exc))

    try:
        return _delete_resource_by_name(self.ep_client, resource, dataset_id=dataset_id, server=server)
    except CKANActionError as exc:
        errors.append(str(exc))
        raise CKANActionError("; ".join(errors)) from exc
