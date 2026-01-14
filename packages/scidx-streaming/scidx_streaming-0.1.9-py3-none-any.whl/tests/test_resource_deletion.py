"""Unit tests for resource deletion helpers."""

from __future__ import annotations

import copy
import json
from typing import Any, Dict, List

import pytest

from scidx_streaming.connectors.ckan import CKANActionError
from scidx_streaming.resources import delete_resource, delete_resource_by_name
from scidx_streaming.resources.utils.registry import build_dataset_resource_entry


class FakeEPClient:
    """Minimal ndp_ep-like client that stores datasets in-memory."""

    def __init__(self) -> None:
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.register_general_dataset(
            _dataset_payload(
                dataset_id="primary-id",
                name="primary",
                resources=[
                    _build_resource("json-id", "json_batch", "json"),
                    _build_resource("csv-id", "csv_daily", "csv"),
                ],
            )
        )
        self.register_general_dataset(
            _dataset_payload(
                dataset_id="secondary-id",
                name="secondary",
                resources=[_build_resource("json-secondary", "json_batch", "json")],
            )
        )

    def search_datasets(self, terms: List[str], *, server: str | None = None) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for dataset in self.datasets.values():
            if not terms:
                results.append(copy.deepcopy(dataset))
                continue
            for term in terms:
                if not term or term == "*" or dataset["name"] == term or dataset.get("id") == term:
                    results.append(copy.deepcopy(dataset))
                    break
        return results

    def patch_general_dataset(self, dataset_identifier: str, payload: Dict[str, Any], *, server: str | None = None) -> None:
        target = None
        for dataset in self.datasets.values():
            if dataset.get("id") == dataset_identifier or dataset.get("name") == dataset_identifier:
                target = dataset
                break
        if not target:
            raise CKANActionError(f"Dataset {dataset_identifier} not found.")
        target["resources"] = copy.deepcopy(payload.get("resources") or [])

    def delete_resource_by_id(self, dataset_identifier: str, *, server: str | None = None) -> None:
        self._delete_dataset(dataset_identifier)

    def delete_resource_by_name(self, dataset_name: str, *, server: str | None = None) -> None:
        self._delete_dataset(dataset_name)

    def register_general_dataset(self, payload: Dict[str, Any], *, server: str | None = None) -> Dict[str, Any]:
        dataset_name = payload.get("name")
        if not dataset_name:
            raise CKANActionError("name is required.")
        dataset_id = payload.get("id") or dataset_name
        dataset = {
            "id": dataset_id,
            "name": dataset_name,
            "title": payload.get("title") or dataset_name.title(),
            "owner_org": payload.get("owner_org") or "example",
            "resources": copy.deepcopy(payload.get("resources") or []),
        }
        self.datasets[dataset_name] = dataset
        return {"result": {"name": dataset_name, "id": dataset_id}}

    def _delete_dataset(self, identifier: str) -> None:
        target_name = None
        for name, dataset in self.datasets.items():
            if dataset.get("id") == identifier or name == identifier:
                target_name = name
                break
        if target_name:
            self.datasets.pop(target_name, None)
        else:
            raise CKANActionError(f"Dataset {identifier} not found.")


def _dataset_payload(*, dataset_id: str, name: str, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "id": dataset_id,
        "name": name,
        "title": name.title(),
        "owner_org": "example",
        "resources": resources,
    }


def _build_resource(resource_id: str, name: str, resource_type: str) -> Dict[str, Any]:
    definition = {
        "type": resource_type,
        "name": name,
        "description": f"{resource_type} demo",
    }
    if resource_type in {"csv", "json"}:
        definition["url"] = f"https://example.com/{name}.data"
    entry = build_dataset_resource_entry(definition, resource_id=resource_id)
    # Ensure registry.load_definition_from_resource can decode the JSON payload.
    entry["description"] = json.dumps(definition)
    return entry


@pytest.fixture()
def fake_client() -> FakeEPClient:
    return FakeEPClient()


def test_delete_resource_removes_only_target(fake_client: FakeEPClient) -> None:
    delete_resource(fake_client, "csv-id")
    primary_resources = fake_client.datasets["primary"]["resources"]
    assert len(primary_resources) == 1
    assert primary_resources[0]["id"] == "json-id"


def test_delete_resource_by_name_requires_dataset_when_duplicate(
    fake_client: FakeEPClient, capsys: pytest.CaptureFixture[str]
) -> None:
    delete_resource_by_name(fake_client, "json_batch")
    captured = capsys.readouterr().out
    assert "Multiple resources named 'json_batch'" in captured
    assert "primary" in captured
    assert "secondary" in captured
    # Both datasets should remain untouched when ambiguity exists.
    assert any(resource["name"] == "json_batch" for resource in fake_client.datasets["primary"]["resources"])
    assert any(resource["name"] == "json_batch" for resource in fake_client.datasets["secondary"]["resources"])


def test_delete_resource_by_name_scoped_to_dataset(fake_client: FakeEPClient) -> None:
    delete_resource_by_name(fake_client, "json_batch", dataset_id="primary")
    primary_resources = fake_client.datasets["primary"]["resources"]
    secondary_resources = fake_client.datasets["secondary"]["resources"]
    assert not any(resource["name"] == "json_batch" for resource in primary_resources)
    assert any(resource["name"] == "json_batch" for resource in secondary_resources)
