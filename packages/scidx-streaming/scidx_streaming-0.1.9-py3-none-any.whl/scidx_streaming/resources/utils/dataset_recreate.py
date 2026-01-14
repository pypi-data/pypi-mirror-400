"""Helpers that delete + recreate datasets to remove resources cleanly."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from ...connectors.ckan import CKANActionError
from . import common
from .dataset_snapshot import clone_dataset

logger = logging.getLogger(__name__)


def recreate_dataset_without_resource(
    ep_client: Any,
    dataset: Mapping[str, Any],
    scope: str | None,
    skip_index: int,
) -> None:
    """Delete a dataset and re-register it without the specified resource entry.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client exposing dataset delete/register helpers.
    dataset : Mapping[str, Any]
        Dataset payload including resources.
    scope : str | None
        Optional ndp_ep scope override.
    skip_index : int
        Index of the resource to remove from the dataset.
    """
    dataset_name = common.clean_text(dataset.get("name"))
    dataset_identifier = dataset.get("id") or dataset_name
    if not dataset_name or not dataset_identifier:
        raise CKANActionError("Dataset metadata is incomplete; cannot delete resource.")

    payload = clone_dataset(dataset, skip_resource_index=skip_index)
    remaining = len(payload.get("resources") or [])

    logger.info("Deleting dataset %s to remove resource index %s", dataset_name, skip_index)
    _delete_dataset(ep_client, dataset_identifier, dataset_name, scope)
    logger.info("Re-registering dataset %s with %s remaining resources.", dataset_name, remaining)
    _register_dataset(ep_client, payload, scope)


def _delete_dataset(ep_client: Any, dataset_id: str, dataset_name: str, scope: str | None) -> None:
    """Attempt to delete a dataset by id or name using ndp_ep helpers."""
    errors: list[str] = []
    deleter_id = getattr(ep_client, "delete_resource_by_id", None)
    if callable(deleter_id):
        try:
            if scope:
                deleter_id(dataset_id, server=scope)
            else:
                deleter_id(dataset_id)
            return
        except Exception as exc:
            errors.append(str(exc))
    deleter_name = getattr(ep_client, "delete_resource_by_name", None)
    if callable(deleter_name):
        try:
            if scope:
                deleter_name(dataset_name, server=scope)
            else:
                deleter_name(dataset_name)
            return
        except Exception as exc:
            errors.append(str(exc))
    raise CKANActionError(
        "Failed to delete dataset before recreation." if not errors else f"Failed to delete dataset: {errors[-1]}"
    )


def _register_dataset(ep_client: Any, payload: Mapping[str, Any], scope: str | None) -> None:
    """Register a dataset payload using ndp_ep.register_general_dataset."""
    registrar = getattr(ep_client, "register_general_dataset", None)
    if not callable(registrar):
        raise CKANActionError("ndp_ep client does not support register_general_dataset.")
    payload_copy = dict(payload)
    if scope:
        registrar(payload_copy, server=scope)
    else:
        registrar(payload_copy)


__all__ = ["recreate_dataset_without_resource"]
