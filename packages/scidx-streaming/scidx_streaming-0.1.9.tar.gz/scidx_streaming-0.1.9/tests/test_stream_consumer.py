from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any

from scidx_streaming.streams.consumer import StreamHandle
from scidx_streaming.client import streams as client_streams


def test_manual_ingest_and_summary() -> None:
    handle = StreamHandle(topic="demo")

    handle.ingest([
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
    ])

    records = handle.records(limit=None)
    assert len(records) == 2
    assert {"id", "value"}.issubset(set(records[0].keys()))

    df = handle.dataframe()
    assert not df.empty

    summary = handle.summary()
    assert summary["total_consumed"] == 2
    assert "id" in summary["columns"]


def test_retention_max_records_enforced() -> None:
    handle = StreamHandle(topic="retention")
    handle.set_retention(max_records=2, max_age_seconds=100)

    handle.ingest([{"id": i} for i in range(3)])
    retained = handle.records(limit=None)
    assert len(retained) == 2
    assert retained[0]["id"] == 1
    assert retained[1]["id"] == 2


def test_retention_max_age_enforced() -> None:
    handle = StreamHandle(topic="retention_age")
    handle.set_retention(max_records=10, max_age_seconds=1)

    old_ts = datetime.now(timezone.utc) - timedelta(seconds=5)
    handle.ingest([{"id": "old"}], timestamp=old_ts)

    time.sleep(1.1)
    retained = handle.records(limit=None)
    assert retained == []


def test_retention_max_bytes_enforced() -> None:
    handle = StreamHandle(topic="retention_bytes")
    handle.set_retention(max_records=10, max_bytes=200, max_age_seconds=100)

    payload = {"blob": "x" * 300}
    handle.ingest([payload, payload])

    retained = handle.records(limit=None)
    # Only one should survive the 200-byte cap
    assert len(retained) == 1


def test_background_poll_with_fake_consumer() -> None:
    class FakeConsumer:
        def __init__(self, *_: Any, **__: Any) -> None:
            self.closed = False
            self._sent = False

        def poll(self, timeout_ms: int | None = None, max_records: int | None = None) -> dict[Any, list[Any]]:
            if self._sent:
                time.sleep(0.01)
                return {}
            self._sent = True
            return {None: [SimpleNamespace(value=b"{\"foo\": 1}", offset=0, partition=0, timestamp=0)]}

        def wakeup(self) -> None:
            return None

        def close(self) -> None:
            self.closed = True

    handle = StreamHandle(
        topic="demo",
        overrides={"host": "localhost", "port": 9092},
        consumer_factory=FakeConsumer,
    )

    handle.start(poll_interval=0.05)
    time.sleep(0.15)
    retained = handle.records(limit=None)
    handle.stop()

    assert retained
    assert retained[0]["foo"] == 1


def test_consume_stream_helper_starts_with_options() -> None:
    class DummyClient:
        kafka_host = "localhost"
        kafka_port = 9092

    class FakeConsumer:
        def __init__(self, *_: Any, **__: Any) -> None:
            self._sent = False

        def poll(self, timeout_ms: int | None = None, max_records: int | None = None) -> dict[Any, list[Any]]:
            if self._sent:
                return {}
            self._sent = True
            return {None: [SimpleNamespace(value=b"{\"foo\": 2}", offset=1, partition=0, timestamp=0)]}

        def wakeup(self) -> None:
            return None

        def close(self) -> None:
            return None

    handle = client_streams.consume_stream(
        DummyClient(),
        "demo",
        from_beginning=True,
        retention_max_records=10,
        retention_max_bytes=1024,
        retention_max_age_seconds=60,
        poll_interval=0.05,
    )

    handle.consumer_factory = FakeConsumer
    handle.start()

    time.sleep(0.15)
    retained = handle.records(limit=None)
    handle.stop()

    assert retained
    assert retained[0]["foo"] == 2
