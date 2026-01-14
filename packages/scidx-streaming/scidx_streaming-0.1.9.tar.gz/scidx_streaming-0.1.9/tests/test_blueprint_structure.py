"""Minimal tests that assert the new blueprint-oriented structure."""

from __future__ import annotations

import pytest
from ndp_ep import APIClient

from scidx_streaming import StreamBlueprint, StreamHandle, StreamingClient
from scidx_streaming.connectors.ckan import CKANActionError
from scidx_streaming.resources import ResourceSearchResults
from scidx_streaming.streams.creation.common import create_stream


class DummySession:
    """Minimal requests-like session that surfaces missing CKAN endpoints."""

    def post(self, *_: object, **__: object) -> None:
        raise RuntimeError("CKAN access not configured for tests.")


class DummyAPIClient(APIClient):
    """Subclass the real ``APIClient`` to keep tests close to production behaviour."""

    def __init__(self) -> None:
        super().__init__(base_url="https://example.test", token="dummy")
        self.session = DummySession()
        self._kafka_details = {"kafka_host": "localhost", "kafka_port": 9092}

    def get_kafka_details(self) -> dict[str, int | str]:
        return dict(self._kafka_details)

    def register_general_dataset(self, *_: object, **__: object) -> None:
        raise NotImplementedError

    def search_datasets(self, *_: object, **__: object) -> list[dict[str, object]]:
        return []

    def advanced_search(self, *_: object, **__: object) -> list[dict[str, object]]:
        return []


def test_streaming_client_exposes_blueprint_helpers() -> None:
    client = StreamingClient(DummyAPIClient())

    with pytest.raises(ValueError):
        client.register_resource("dataset-id", {"type": "csv"})

    with pytest.raises(CKANActionError):
        client.update_resource("resource-id", {"description": "demo"})

    with pytest.raises(CKANActionError):
        client.deactivate_resource("resource-id")

    with pytest.raises(CKANActionError):
        client.delete_resource("resource-id")

    results = client.search_resources()
    assert isinstance(results, ResourceSearchResults)
    assert len(results) == 0

    compiled = client.compile_filters(
        [{"type": "comparison", "column": "value", "op": "eq", "value": 1}]
    )
    assert compiled and compiled[0]["op"] == "eq"


def test_stream_blueprint_connects_to_handle() -> None:
    client = StreamingClient(DummyAPIClient())

    # Direct StreamHandle creation (blueprints deprecated on client)
    handle = StreamHandle(topic="demo-topic")
    assert isinstance(handle, StreamHandle)
    assert handle.topic == "demo-topic"

    assert handle.records() == []
