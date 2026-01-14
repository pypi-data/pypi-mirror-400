"""Offline regression tests that exercise the majority of ``scidx_streaming``."""

from __future__ import annotations

import base64
import copy
import contextlib
import io
import json
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

import pytest

from ndp_ep import APIClient

from scidx_streaming import StreamingClient
from scidx_streaming.data_cleaning import filters as cleaning_filters
from scidx_streaming.connectors.ckan.actions import CKANActionError, call_action
from scidx_streaming.resources import registry as resource_registry
from scidx_streaming.resources.search import ResourceSearchResults, search_resources
from scidx_streaming.resources.utils import common as resource_common, datasets as dataset_utils
from scidx_streaming.resources.utils.dataset_snapshot import clone_dataset
from scidx_streaming.streams import builder as stream_builder
from scidx_streaming.streams.consumer import StreamHandle
from scidx_streaming.utils import log as log_utils, time as time_utils

from .utils import CoverageMonitor


def _jwt_token(sub: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"sub": sub}).encode()).decode().rstrip("=")
    return f"hdr.{payload}.sig"


class OfflineAPIClient(APIClient):
    """Minimal ndp_ep stand in that stores datasets + resources in memory."""

    def __init__(self) -> None:
        # Intentionally skip parent __init__ to avoid live HTTP calls.
        self.base_url = "https://offline.local/api"
        self.token = _jwt_token("offline-user")
        self.session = object()
        self._datasets: dict[str, dict[str, Any]] = {}
        self.kafka_host = "offline-kafka"
        self.kafka_port = 19092

    # ndp_ep dataset helpers -------------------------------------------------
    def register_general_dataset(self, payload: Mapping[str, Any], server: str | None = None) -> dict[str, Any]:
        dataset = copy.deepcopy(dict(payload))
        dataset_id = str(dataset.get("id") or dataset.get("name") or f"dataset-{len(self._datasets) + 1}")
        dataset_name = str(dataset.get("name") or dataset_id)
        dataset["id"] = dataset_id
        dataset["name"] = dataset_name
        dataset.setdefault("resources", [])
        self._datasets[dataset_id] = dataset
        return copy.deepcopy(dataset)

    def _resolve_dataset(self, identifier: str | None) -> dict[str, Any] | None:
        if identifier and identifier in self._datasets:
            return self._datasets[identifier]
        if not identifier:
            return None
        for dataset in self._datasets.values():
            if dataset.get("name") == identifier:
                return dataset
        return None

    def patch_general_dataset(self, dataset_identifier: str, payload: Mapping[str, Any], server: str | None = None) -> dict[str, Any]:
        dataset = self._resolve_dataset(dataset_identifier)
        if not dataset:
            raise KeyError(dataset_identifier)
        dataset["resources"] = copy.deepcopy(payload.get("resources") or [])
        return copy.deepcopy(dataset)

    def search_datasets(self, queries: Sequence[str] | None = None, server: str | None = None) -> list[dict[str, Any]]:
        normalized = [str(query or "").strip().lower() for query in (queries or [])]
        normalized = [query for query in normalized if query]
        if not normalized:
            normalized = [""]
        results: list[dict[str, Any]] = []
        for dataset in self._datasets.values():
            dataset_id = dataset.get("id", "").lower()
            dataset_name = dataset.get("name", "").lower()
            if "" in normalized or any(query == dataset_id or query == dataset_name for query in normalized):
                results.append(copy.deepcopy(dataset))
        return results

    def delete_resource_by_id(self, dataset_id: str, server: str | None = None) -> None:
        if dataset_id not in self._datasets:
            raise KeyError(dataset_id)
        self._datasets.pop(dataset_id, None)

    def delete_resource_by_name(self, dataset_name: str, server: str | None = None) -> None:
        target_id = None
        for identifier, dataset in self._datasets.items():
            if dataset.get("name") == dataset_name:
                target_id = identifier
                break
        if not target_id:
            raise KeyError(dataset_name)
        self._datasets.pop(target_id, None)

    def get_kafka_details(self) -> Mapping[str, Any]:
        return {"kafka_host": self.kafka_host, "kafka_port": self.kafka_port}

    def get_configuration(self) -> Mapping[str, Any]:
        return {"base_url": self.base_url, "kafka": self.get_kafka_details()}

    # Convenience helpers used by the tests ----------------------------------
    def add_raw_resource(self, dataset_name: str, resource: Mapping[str, Any]) -> None:
        dataset = self._resolve_dataset(dataset_name)
        if not dataset:
            raise KeyError(dataset_name)
        dataset.setdefault("resources", []).append(copy.deepcopy(resource))

    def snapshot(self, dataset_name: str) -> dict[str, Any]:
        dataset = self._resolve_dataset(dataset_name)
        if not dataset:
            raise KeyError(dataset_name)
        return copy.deepcopy(dataset)


PRIMARY_DATASET = {
    "name": "full_coverage_dataset",
    "title": "Full coverage dataset",
    "notes": "Offline dataset for exercising scidx_streaming",
    "owner_org": "scidx",
    "private": False,
    "license_id": "MIT",
    "version": "1.0",
    "tags": ["science", {"name": "derived"}],
    "groups": {"public": True, "research": True},
    "extras": {"source": "lab", "priority": "high"},
    "resources": [],
}

SECONDARY_DATASET = {
    "name": "auxiliary_dataset",
    "title": "Aux dataset",
    "notes": "Holds conflicting resource names",
    "owner_org": "scidx",
    "groups": "aux-group",
    "resources": [],
}

CSV_RESOURCE = {
    "type": "csv",
    "name": "daily_snapshot",
    "description": "Daily CSV export",
    "url": "https://example.com/daily.csv",
    "compression": "gzip",
    "checksum": "abc123",
    "config": {"encoding": "utf-8"},
}

JSON_RESOURCE = {
    "type": "json",
    "name": "json_archive",
    "description": "JSON payload",
    "url": "https://example.com/archive.json",
}

KAFKA_RESOURCE = {
    "type": "kafka",
    "name": "kafka_ingest",
    "description": "Kafka ingest topic",
    "host": "broker.internal",
    "topic": "raw.pop",
    "port": "9093",
    "secret_reference": "vault://kafka/creds",
}

RSS_RESOURCE = {
    "type": "rss",
    "name": "alerts_feed",
    "description": "Alerts RSS",
    "url": "https://example.com/feed",
    "refresh_interval": 60,
}

API_STREAM_RESOURCE = {
    "type": "api_stream",
    "name": "api_ingest",
    "description": "REST poller",
    "url": "https://example.com/api",
    "http_method": "post",
    "poll_interval": 30,
    "headers": {"Accept": "application/json"},
    "params": {"limit": 10},
    "body": {"query": "all"},
}


def build_offline_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Provision an OfflineAPIClient + StreamingClient pair."""

    from scidx_streaming.connectors.kafka import connection as kafka_connection

    class FakeAdminClient:
        def __init__(self, **config: Any) -> None:
            self.config = config
            self.closed = False

        def describe_cluster(self) -> Mapping[str, Any]:
            return {"brokers": [{"node_id": 1}], "controller": 1, "cluster_id": "offline"}

        def list_topics(self) -> list[str]:
            return ["raw.full_coverage", "derived.full_coverage"]

        def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(kafka_connection, "KafkaAdminClient", FakeAdminClient)

    client = OfflineAPIClient()
    client.register_general_dataset(PRIMARY_DATASET)
    client.register_general_dataset(SECONDARY_DATASET)
    client.add_raw_resource(
        PRIMARY_DATASET["name"],
        {"id": "legacy", "name": "legacy", "description": "not json", "format": "legacy"},
    )

    streaming_client = StreamingClient(client)
    return {"client": client, "streaming": streaming_client, "primary": PRIMARY_DATASET["name"], "secondary": SECONDARY_DATASET["name"]}


@pytest.fixture()
def offline_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Return a fully patched ``StreamingClient`` backed by ``OfflineAPIClient``."""

    return build_offline_env(monkeypatch)


def run_offline_full_coverage_workflow(
    offline_env: Mapping[str, Any],
    *,
    coverage_monitor: CoverageMonitor | None = None,
) -> None:
    client: OfflineAPIClient = offline_env["client"]
    streaming: StreamingClient = offline_env["streaming"]
    primary = offline_env["primary"]
    secondary = offline_env["secondary"]

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Starting offline workflow")

    csv_entry = streaming.register_resource(primary, CSV_RESOURCE)
    json_entry = streaming.register_resource(primary, JSON_RESOURCE)
    kafka_entry = streaming.register_resource(primary, KAFKA_RESOURCE)
    rss_entry = streaming.register_resource(primary, RSS_RESOURCE)
    api_entry = streaming.register_resource(primary, API_STREAM_RESOURCE)

    shared_payload = copy.deepcopy(CSV_RESOURCE)
    shared_payload.update({"name": "shared_resource", "description": "Shared resource", "url": "https://example.com/shared.csv"})
    shared_primary = streaming.register_resource(primary, shared_payload)
    shared_secondary = streaming.register_resource(secondary, copy.deepcopy(shared_payload))

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Resources registered")

    updated_csv = streaming.update_resource(csv_entry["id"], {"description": "CSV updated", "schema": {"fields": ["id"]}})
    decoded = resource_registry.load_definition_from_resource(updated_csv)
    assert decoded["description"].startswith("CSV updated")
    assert decoded["schema"] == {"fields": ["id"]}

    deactivated_api = streaming.deactivate_resource(api_entry["id"], reason="maintenance")
    api_meta = resource_registry.load_definition_from_resource(deactivated_api)
    assert api_meta["inactive"] is True
    assert api_meta["deactivation_reason"] == "maintenance"
    assert api_meta["preserve_record"] is True

    results = streaming.search_resources(terms=[primary])
    assert isinstance(results, ResourceSearchResults)
    assert len(results) >= 5
    assert results.ids()
    summary = results.summary()
    assert summary["count"] == len(results)
    assert "csv" in summary["types"]
    assert results.as_dicts()[0]["dataset_id"] == primary
    first_record = results[0]
    assert first_record.name

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Search + summary complete")

    inactive_results = streaming.search_resources(terms=[primary], include_inactive=True, types=["api_stream", "rss"])
    assert any(record.type == "api_stream" for record in inactive_results)

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        streaming.delete_resource_by_name(shared_payload["name"])
    conflict_message = buffer.getvalue()
    assert "Multiple resources" in conflict_message

    streaming.delete_resource_by_name(shared_payload["name"], dataset_id=secondary)
    secondary_snapshot = client.snapshot(secondary)
    assert all(res.get("name") != shared_payload["name"] for res in secondary_snapshot.get("resources", []))

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Delete-by-name verified")

    primary_snapshot = client.snapshot(primary)
    rss_meta = next(resource for resource in primary_snapshot["resources"] if resource.get("name") == RSS_RESOURCE["name"])
    dataset_utils.remember_resource_hint(rss_meta, primary_snapshot)
    ghost_rss_id = rss_entry["id"]
    replacement_payload = copy.deepcopy(RSS_RESOURCE)
    replacement_payload["id"] = "replacement-feed"
    streaming.register_resource(primary, replacement_payload)
    streaming.delete_resource(ghost_rss_id)
    assert all(res.get("id") != ghost_rss_id for res in client.snapshot(primary).get("resources", []))

    streaming.delete_resource(kafka_entry["id"])
    recreated_snapshot = client.snapshot(primary)
    assert all(res.get("name") != KAFKA_RESOURCE["name"] for res in recreated_snapshot.get("resources", []))
    cloned = clone_dataset(recreated_snapshot)
    assert cloned["name"] == primary
    assert cloned["resources"]
    secondary_groups = clone_dataset(client.snapshot(secondary)).get("groups") or []
    assert "aux-group" in secondary_groups

    payload = resource_registry.build_resource_payload(primary, resource_registry.load_definition_from_resource(json_entry))
    assert payload["package_id"] == primary

    assert dataset_utils.resource_hint(shared_secondary["id"]) is None

    handle = StreamHandle(topic="derived.topic")
    assert isinstance(handle, StreamHandle)
    consumer = streaming.consume_stream("derived.topic", host="custom", port=2000)
    assert consumer.overrides["host"] == "custom"
    default_consumer = streaming.consume_stream("derived.topic")
    assert default_consumer.overrides["host"] == client.kafka_host

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Stream helpers invoked")

    with pytest.raises(ValueError):
        streaming.compile_filters([{}])
    compiled_filters = streaming.compile_filters(
        [{"type": "comparison", "column": "value", "op": "gt", "value": 5}]
    )
    assert compiled_filters and compiled_filters[0]["op"] == "gt"

    assert isinstance(time_utils.now_utc(), datetime)
    assert time_utils.isoformat().endswith("Z") is False  # timezone-aware ISO string

    if coverage_monitor:
        coverage_monitor.snapshot("[offline] Offline workflow complete")


def test_full_coverage_workflow_offline(offline_env: Mapping[str, Any]) -> None:
    run_offline_full_coverage_workflow(offline_env)


def test_ckan_call_action_success_and_errors() -> None:
    client = OfflineAPIClient()

    class FakeResponse:
        def __init__(self, payload: Mapping[str, Any]):
            self._payload = payload
            self.ok = payload.get("success", True)

        def json(self) -> Mapping[str, Any]:
            return dict(self._payload)

    class FakeSession:
        def __init__(self) -> None:
            self.payload: Mapping[str, Any] = {"success": True, "result": {"ok": True}}
            self.calls: list[Mapping[str, Any]] = []

        def set_payload(self, payload: Mapping[str, Any]) -> None:
            self.payload = payload

        def post(self, endpoint: str, json: Mapping[str, Any] | None = None, headers: Mapping[str, Any] | None = None, params: Mapping[str, Any] | None = None, timeout: int | None = None) -> FakeResponse:
            self.calls.append({"endpoint": endpoint, "json": json, "headers": headers, "params": params})
            return FakeResponse(self.payload)

    session = FakeSession()
    client.session = session
    result = call_action(client, "ping", {"echo": True}, server="local")
    assert result["ok"] is True
    assert session.calls

    session.set_payload({"success": False, "error": "boom"})
    with pytest.raises(CKANActionError):
        call_action(client, "ping", {})

    class BrokenSession:
        def post(self, *_: Any, **__: Any) -> object:
            return object()

    client.session = BrokenSession()
    with pytest.raises(CKANActionError):
        call_action(client, "ping", {})


def test_clone_dataset_validation_errors() -> None:
    with pytest.raises(CKANActionError):
        clone_dataset({"title": "missing name", "owner_org": "scidx"})
    with pytest.raises(CKANActionError):
        clone_dataset({"name": "missing title", "owner_org": "scidx"})


def test_registry_and_common_validation() -> None:
    with pytest.raises(ValueError):
        resource_common.normalize_port("not-a-number")
    with pytest.raises(ValueError):
        resource_common.normalize_port(-1)
    with pytest.raises(ValueError):
        resource_registry.normalize_definition({"type": "unknown", "name": "x", "description": "y"})
    with pytest.raises(ValueError):
        resource_registry.normalize_definition({"type": "csv", "description": "missing name"})
    with pytest.raises(ValueError):
        resource_registry.build_dataset_resource_entry({"name": "broken"})


def test_search_resources_invalid_client() -> None:
    class NoSearch:
        pass

    with pytest.raises(CKANActionError):
        search_resources(NoSearch())


def test_filter_and_stream_placeholders() -> None:
    with pytest.raises(ValueError):
        cleaning_filters.compile_filters([{}])

    explanation = cleaning_filters.explain_filter({"type": "mapping", "column": "x", "action": "drop"})
    assert "Drop" in explanation

    handle = StreamHandle(topic="derived")
    assert handle.records() == []
    assert handle.dataframe().empty
    with pytest.raises(NotImplementedError):
        handle.plot()
    summary = handle.summary()
    assert summary["stored_records"] == 0


def test_log_configuration_and_time(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    log_file = tmp_path / "scidx.log"
    monkeypatch.setenv("SCIDX_LOG_FILE", str(log_file))
    monkeypatch.setattr(log_utils, "_LOGGING_CONFIGURED", False)
    log_utils.configure_logging(level="DEBUG")
    logger = log_utils.get_logger("tests.coverage")
    logger.trace("trace message")
    logger.dataflow("dataflow message")
    logger.audit("audit message")

    ts = datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert time_utils.isoformat(ts).endswith("+00:00")


def test_clean_payload_and_resource_payload_helpers() -> None:
    cleaned = resource_common.clean_payload({"foo": 1, "config": {"nested": 2}})
    assert cleaned["nested"] == 2
    assert "config" not in cleaned

    payload = resource_registry.build_resource_payload(
        "dataset",
        resource_registry.normalize_definition(CSV_RESOURCE),
        existing_id="existing",
    )
    assert payload["id"] == "existing"
