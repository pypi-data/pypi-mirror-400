"""Unit tests for the simplified resource definition helpers."""

from __future__ import annotations

import json

from scidx_streaming.resources.utils import registry as definitions


def test_build_csv_payload_includes_encoded_definition() -> None:
    definition = definitions.normalize_definition(
        {
            "type": "csv",
            "name": "csv_demo",
            "description": "CSV demo",
            "url": "https://example.com/data.csv",
        }
    )
    payload = definitions.build_resource_payload("dataset-id", definition)

    assert payload["name"] == "csv_demo"
    assert payload["format"] == "csv"
    assert payload["url"] == "https://example.com/data.csv"
    encoded = payload["method_definition"]
    assert encoded == payload["description"]
    decoded = json.loads(encoded)
    assert decoded["description"] == "CSV demo"
    assert decoded["url"] == "https://example.com/data.csv"


def test_build_kafka_payload_sets_extra_fields() -> None:
    definition = definitions.normalize_definition(
        {
            "type": "kafka",
            "name": "kafka_demo",
            "description": "Kafka demo",
            "host": "broker.example",
            "port": 9092,
            "topic": "demo.topic",
            "sasl_username": "demo",
        }
    )
    payload = definitions.build_resource_payload("dataset-id", definition)

    assert payload["kafka_host"] == "broker.example"
    assert payload["kafka_port"] == 9092
    assert payload["kafka_topic"] == "demo.topic"
    assert payload["host"] == "broker.example"
    assert payload["protected"] is True
    assert payload["url"] == "kafka://broker.example:9092/demo.topic"
    encoded = payload["method_definition"]
    decoded = json.loads(encoded)
    assert decoded["topic"] == "demo.topic"
