"""Resource deletion helpers."""

from __future__ import annotations

from typing import Any, Mapping

from ..connectors.ckan import CKANActionError
from .utils import common, datasets, registry
from .utils.dataset_recreate import recreate_dataset_without_resource
from .utils.datasets import forget_resource_hint, resource_hint


def delete_resource(
    ep_client: Any,
    resource_id: str,
    *,
    server: str | None = None,
) -> None:
    """Remove a resource by recreating the dataset without it.

    Parameters
    ----------
    ep_client : Any (required)
        ndp_ep API client.
    resource_id : str (required)
        CKAN resource identifier.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Raises
    ------
    CKANActionError
        If the resource cannot be found or the dataset cannot be modified.
    """

    dataset, scope, idx = datasets.locate_resource(ep_client, resource_id, preferred_scope=server)
    if dataset is None or idx is None:
        hint = resource_hint(resource_id)
        if hint and hint.get("resource_name"):
            dataset_refs = [value for value in (hint.get("dataset_name"), hint.get("dataset_id")) if value]
            matches = datasets.find_resources_by_name(
                ep_client,
                hint["resource_name"] or "",
                dataset_names=dataset_refs or None,
                preferred_scope=server,
            )
            if matches:
                dataset, scope, idx = matches[0]
    if dataset is None or idx is None:
        raise CKANActionError(f"Resource '{resource_id}' not found.")

    resources = dataset.get("resources") or []
    resource_meta = resources[idx] if idx < len(resources) else {}
    resource_identifier = common.clean_text(resource_meta.get("id") or resource_id)
    recreate_dataset_without_resource(ep_client, dataset, scope or server, idx)
    if resource_identifier:
        forget_resource_hint(resource_identifier)


def delete_resource_by_name(
    ep_client: Any,
    resource_name: str,
    *,
    dataset_id: str | None = None,
    server: str | None = None,
) -> None:
    """Remove a resource by its name, optionally scoped to a dataset.

    Parameters
    ----------
    ep_client : Any (required)
        ndp_ep API client.
    resource_name : str (required)
        Resource name to delete.
    dataset_id : str | None (optional, default None)
        Optional dataset slug/id to disambiguate duplicate names.
    server : str | None (optional, default None)
        Optional ndp_ep scope override.

    Raises
    ------
    CKANActionError
        If no matching resource is found.
    Notes
    -----
    When multiple matches exist and ``dataset_id`` is not provided, a conflict
    summary is printed and no deletion occurs.
    """

    dataset_refs = [dataset_id] if dataset_id else None
    matches = datasets.find_resources_by_name(
        ep_client,
        resource_name,
        dataset_names=dataset_refs,
        preferred_scope=server,
    )
    if not matches:
        target = f"{resource_name} on dataset {dataset_id}" if dataset_id else resource_name
        raise CKANActionError(f"Resource '{target}' not found.")

    if len(matches) > 1 and not dataset_id:
        print(_format_name_conflict(resource_name, matches), flush=True)
        return

    dataset, scope, idx = matches[0]
    resources = dataset.get("resources") or []
    resource_meta = resources[idx] if idx < len(resources) else {}
    resource_identifier = common.clean_text(resource_meta.get("id") or resource_name)
    recreate_dataset_without_resource(ep_client, dataset, scope or server, idx)
    if resource_identifier:
        forget_resource_hint(resource_identifier)
    forget_resource_hint(matches[0][0].get("id") if isinstance(matches[0][0], Mapping) else None)


def _format_name_conflict(
    resource_name: str,
    matches: list[tuple[Mapping[str, Any], str | None, int]],
) -> str:
    """Return a human-readable conflict message for duplicate resource names."""

    lines = [f"Multiple resources named '{resource_name}' were found:"]
    for dataset, _scope, idx in matches:
        resources = dataset.get("resources") or []
        resource = resources[idx]
        definition = registry.load_definition_from_resource(resource)
        description = definition.get("description") or resource.get("description") or "unspecified"
        identifier = resource.get("id") or resource.get("name")
        dataset_name = dataset.get("name") or dataset.get("id")
        lines.append(f"- dataset={dataset_name} id={identifier} description={description}")
    lines.append("Re-run the delete call using the dataset_id to disambiguate.")
    return "\n".join(lines)


__all__ = ["delete_resource", "delete_resource_by_name"]
