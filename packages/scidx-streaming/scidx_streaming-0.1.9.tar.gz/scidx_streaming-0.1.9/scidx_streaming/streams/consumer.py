"""Lightweight Kafka consumer handle built on kafka-python."""

from __future__ import annotations

import csv
import json
import logging
import os
import threading
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:  # pragma: no cover - optional dependency
    from kafka import KafkaConsumer
    from kafka.errors import NoBrokersAvailable
except Exception as exc:  # pragma: no cover - helpful error if kafka-python is missing
    KafkaConsumer = None  # type: ignore
    NoBrokersAvailable = Exception  # type: ignore
    _kafka_import_error = exc
else:
    _kafka_import_error = None

DEFAULT_MAX_RECORDS = 100_000
DEFAULT_MAX_BYTES = 20 * 1024 * 1024
DEFAULT_MAX_AGE_SECONDS = 900
DEFAULT_POLL_INTERVAL = 1.0

logger = logging.getLogger(__name__)


class _Buffer:
    def __init__(
        self,
        *,
        max_records: int = DEFAULT_MAX_RECORDS,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS,
    ) -> None:
        """In-memory bounded buffer for consumed records."""
        self.max_records = max_records
        self.max_bytes = max_bytes
        self.max_age_seconds = max_age_seconds
        self._records: deque[tuple[dict[str, Any], float, int]] = deque()
        self._current_bytes = 0
        self._total_ingested = 0
        self._columns: set[str] = set()
        self._lock = threading.Lock()

    def configure(self, *, max_records: int | None = None, max_bytes: int | None = None, max_age_seconds: int | None = None) -> None:
        """Update retention limits and evict immediately using the new policy."""
        with self._lock:
            if max_records is not None:
                self.max_records = max_records
            if max_bytes is not None:
                self.max_bytes = max_bytes
            if max_age_seconds is not None:
                self.max_age_seconds = max_age_seconds
            self._evict(now=time.time())

    def add(self, record: Mapping[str, Any], *, ts: float | None = None) -> None:
        """Append a record with timestamp (seconds) and evict beyond limits."""
        payload = dict(record)
        size = _estimate_size(payload)
        ts = ts if ts is not None else time.time()
        with self._lock:
            self._records.append((payload, ts, size))
            self._current_bytes += size
            self._total_ingested += 1
            self._columns.update(payload.keys())
            self._evict(now=time.time())

    def snapshot(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Return a shallow copy of buffered records (oldest → newest)."""
        with self._lock:
            items = list(self._records)
        if limit is not None:
            items = items[-limit:]
        return [dict(item[0]) for item in items]

    def summary(self, topic: str, running: bool) -> Mapping[str, Any]:
        """Return buffer stats for the given topic."""
        with self._lock:
            count = len(self._records)
            oldest_age = None
            if self._records:
                oldest_age = max(0.0, time.time() - self._records[0][1])
            return {
                "topic": topic,
                "running": running,
                "stored_records": count,
                "stored_bytes": self._current_bytes,
                "total_consumed": self._total_ingested,
                "columns": tuple(sorted(self._columns)),
                "retention": {
                    "max_records": self.max_records,
                    "max_bytes": self.max_bytes,
                    "max_age_seconds": self.max_age_seconds,
                },
                "oldest_record_age_seconds": oldest_age,
            }

    def _evict(self, *, now: float) -> None:
        """Evict records based on record count, age, and byte limits."""
        while self.max_records and len(self._records) > self.max_records:
            _, _, size = self._records.popleft()
            self._current_bytes = max(0, self._current_bytes - size)
        if self.max_age_seconds:
            threshold = now - self.max_age_seconds
            while self._records and self._records[0][1] < threshold:
                _, _, size = self._records.popleft()
                self._current_bytes = max(0, self._current_bytes - size)
        if self.max_bytes:
            while self._records and self._current_bytes > self.max_bytes and len(self._records) > 1:
                _, _, size = self._records.popleft()
                self._current_bytes = max(0, self._current_bytes - size)


class StreamHandle:
    """Runtime connector that consumes a Kafka topic with bounded buffering."""

    def __init__(
        self,
        topic: str,
        blueprint: Any | None = None,
        overrides: Mapping[str, Any] | None = None,
        consumer_factory: Any | None = None,
        store_path: str | os.PathLike[str] | None = None,
    ) -> None:
        """Initialize a StreamHandle.

        Parameters
        ----------
        topic : str
            Kafka topic to consume.
        blueprint : Any | None
            Optional blueprint metadata for lineage.
        overrides : Mapping[str, Any] | None
            Host/port overrides for Kafka bootstrap resolution.
        consumer_factory : Any | None
            Optional factory to create KafkaConsumer (inject for tests).
        store_path : str | os.PathLike[str] | None
            Optional path to persist records as CSV while consuming.
        """
        self.topic = topic
        self.blueprint = blueprint
        self.overrides = dict(overrides or {})
        self.consumer_factory = consumer_factory
        self._buffer = _Buffer()
        self._default_from_beginning = False
        self._poll_interval = DEFAULT_POLL_INTERVAL
        self._stop_event = threading.Event()
        self._consumer: Any = None
        self._poller: threading.Thread | None = None
        self._running = False
        self._store_path: Path | None = None
        self._store_file: Any = None
        self._store_writer: csv.DictWriter | None = None
        self._store_header_written = False
        self._store_lock = threading.Lock()
        if store_path:
            self.set_store(store_path)

    # Public API ---------------------------------------------------------
    def start(
        self,
        *,
        from_beginning: bool | None = None,
        retention_max_records: int | None = None,
        retention_max_bytes: int | None = None,
        retention_max_age_seconds: int | None = None,
        poll_interval: float | None = None,
    ) -> StreamHandle:
        """Start background consumption with optional retention/offset overrides."""
        if self._running:
            return self

        self._buffer.configure(
            max_records=retention_max_records,
            max_bytes=retention_max_bytes,
            max_age_seconds=retention_max_age_seconds,
        )
        self._poll_interval = poll_interval if poll_interval is not None else self._poll_interval
        effective_from_beginning = self._default_from_beginning if from_beginning is None else from_beginning

        bootstrap = self._resolve_bootstrap()
        self._consumer = self._build_consumer(
            bootstrap_servers=bootstrap,
            auto_offset_reset="earliest" if effective_from_beginning else "latest",
            enable_auto_commit=False,
            consumer_timeout_ms=1000,
        )
        self._prime_consumer(effective_from_beginning)
        self._wait_for_assignment()
        self._open_store_file()

        self._stop_event.clear()
        self._poller = threading.Thread(target=self._poll_loop, name=f"scidx-consume-{self.topic}", daemon=True)
        self._poller.start()
        self._running = True
        return self

    def stop(self) -> None:
        """Stop the consumer thread and close underlying Kafka resources."""
        self._stop_event.set()
        consumer = self._consumer
        if consumer is not None:
            wakeup = getattr(consumer, "wakeup", None)
            if callable(wakeup):
                try:
                    wakeup()
                except Exception:  # pragma: no cover - best effort
                    pass
        if self._poller and self._poller.is_alive():
            self._poller.join(timeout=max(self._poll_interval * 2, 1.0))
        if consumer is not None:
            try:
                consumer.close()
            except Exception:  # pragma: no cover - best effort
                pass
        self._close_store_file()
        self._consumer = None
        self._poller = None
        self._running = False

    def resume(self, **kwargs: Any) -> StreamHandle:
        """Resume consumption using the same arguments as ``start``."""
        return self.start(**kwargs)

    def records(self, *, limit: int | None = 50) -> list[Mapping[str, Any]]:
        """Return buffered records (oldest → newest), limited when provided."""
        return self._buffer.snapshot(limit=limit)

    def dataframe(self, *, limit: int | None = None) -> Any:
        """Return buffered records as a pandas DataFrame (imports pandas lazily)."""
        try:
            import pandas as pd  # type: ignore
        except Exception as exc:  # pragma: no cover - dependency error surfaced to caller
            raise RuntimeError("pandas is required for dataframe previews") from exc
        return pd.DataFrame(self.records(limit=limit))

    def plot(self) -> Any:  # pragma: no cover - placeholder for future UX
        """Placeholder plot hook for parity with prototype notebooks."""
        raise NotImplementedError("Plotting is not implemented for StreamHandle.")

    def summary(self) -> Mapping[str, Any]:
        """Return lightweight status (topic, running, counts, columns, retention)."""
        return self._buffer.summary(topic=self.topic, running=self._running)

    def ingest(self, records: Iterable[Mapping[str, Any] | Any], *, timestamp: datetime | None = None) -> None:
        """Manually push records into the buffer (test/offline helper)."""
        base_ts = timestamp or datetime.now(timezone.utc)
        ts = base_ts.timestamp()
        for payload in records:
            if isinstance(payload, Mapping):
                self._buffer.add(payload, ts=ts)
                self._persist(payload)
            else:
                data = {"value": payload}
                self._buffer.add(data, ts=ts)
                self._persist(data)

    def set_retention(self, *, max_records: int | None = None, max_bytes: int | None = None, max_age_seconds: int | None = None) -> None:
        """Update in-memory buffer limits (records/bytes/age)."""
        self._buffer.configure(
            max_records=max_records,
            max_bytes=max_bytes,
            max_age_seconds=max_age_seconds,
        )

    def set_store(self, store_path: str | os.PathLike[str] | None) -> None:
        """Configure on-disk storage for consumed records (CSV append)."""

        self._close_store_file()
        if store_path is None:
            self._store_path = None
            return

        path = Path(store_path)
        if path.suffix == "":
            path = path.with_suffix(".csv")
        path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path = path
        self._store_header_written = path.exists() and path.stat().st_size > 0
        # File will be opened on start to keep control of lifecycle.

    # Internal helpers ---------------------------------------------------
    def _poll_loop(self) -> None:
        """Background poll loop that buffers decoded Kafka messages."""
        consumer = self._consumer
        if consumer is None:
            return
        while not self._stop_event.is_set():
            try:
                polled = consumer.poll(timeout_ms=int(self._poll_interval * 1000))
            except Exception as exc:  # pragma: no cover - surfaced via logs
                logger.warning("Stream consumer poll failed: %s", exc, exc_info=True)
                time.sleep(min(1.0, self._poll_interval))
                continue
            if not polled:
                continue
            for records in polled.values():
                for message in records:
                    value = self._decode(getattr(message, "value", None))
                    self._buffer.add(value)
                    self._persist(value)

    def _build_consumer(self, **kwargs: Any) -> Any:
        """Construct a KafkaConsumer (or injected factory) with provided kwargs."""
        factory = self.consumer_factory or KafkaConsumer
        if factory is None:  # pragma: no cover - defensive
            raise RuntimeError(f"kafka-python is not available: {_kafka_import_error}")
        try:
            return factory(self.topic, allow_auto_create_topics=False, **kwargs)
        except NoBrokersAvailable as exc:  # pragma: no cover - surfaced to caller
            raise RuntimeError(f"No Kafka brokers available at {kwargs.get('bootstrap_servers')}") from exc
        except Exception:
            logger.error("Failed to construct Kafka consumer", exc_info=True)
            raise

    def _prime_consumer(self, from_beginning: bool) -> None:
        """Seek consumer to beginning or end depending on ``from_beginning``."""
        consumer = self._consumer
        if consumer is None:
            return
        # Skip priming when the consumer does not support assignments (e.g., fakes).
        if not hasattr(consumer, "assignment"):
            return
        try:
            consumer.poll(timeout_ms=0)
            assignment = consumer.assignment()
            if not assignment:
                return
            if from_beginning:
                consumer.seek_to_beginning(*assignment)
            else:
                consumer.seek_to_end(*assignment)
        except Exception:  # pragma: no cover - best effort
            logger.debug("Consumer prime failed", exc_info=True)

    def _wait_for_assignment(self, *, attempts: int = 10, delay: float = 1.0) -> None:
        """Wait for the consumer to obtain a partition assignment."""

        consumer = self._consumer
        if consumer is None or not hasattr(consumer, "assignment"):
            return

        for _ in range(max(1, attempts)):
            assignment = consumer.assignment()
            if assignment:
                return
            try:
                consumer.poll(timeout_ms=int(delay * 1000))
            except Exception:
                logger.debug("Consumer poll during assignment wait failed", exc_info=True)
            time.sleep(delay)

        assignment = consumer.assignment()
        if not assignment:
            raise RuntimeError(f"No partitions assigned for topic '{self.topic}' after waiting {attempts} attempts.")

    def _resolve_bootstrap(self) -> str:
        """Resolve bootstrap string from host/port overrides."""
        host = self.overrides.get("host") if self.overrides else None
        port = self.overrides.get("port") if self.overrides else None
        if not host or not port:
            raise RuntimeError("Kafka host/port are undefined; configure the streaming client or pass overrides.")
        return f"{host}:{port}"

    def _open_store_file(self) -> None:
        """Open CSV store file when persistence is enabled."""
        if self._store_path is None:
            return
        if self._store_file:
            return
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_file = self._store_path.open("a", newline="", encoding="utf-8")
        self._store_writer = None

    def _close_store_file(self) -> None:
        """Close the CSV store file if open."""
        if self._store_file:
            try:
                self._store_file.close()
            except Exception:
                pass
        self._store_file = None
        self._store_writer = None

    def _persist(self, record: Mapping[str, Any]) -> None:
        """Append a record to the CSV store if configured."""
        if self._store_path is None:
            return
        with self._store_lock:
            if not self._store_file:
                self._open_store_file()
            if not self._store_file:
                return
            if self._store_writer is None:
                fieldnames = sorted(record.keys())
                self._store_writer = csv.DictWriter(self._store_file, fieldnames=fieldnames)
                if not self._store_header_written:
                    self._store_writer.writeheader()
                    self._store_header_written = True
            self._store_writer.writerow({k: record.get(k) for k in self._store_writer.fieldnames})
            try:
                self._store_file.flush()
            except Exception:
                pass

    @staticmethod
    def _decode(raw: Any) -> dict[str, Any]:
        """Decode Kafka message value into a dictionary."""
        if raw is None:
            return {}
        if isinstance(raw, (bytes, bytearray, memoryview)):
            raw = bytes(raw)
            try:
                decoded = raw.decode("utf-8")
                return _normalize(decoded)
            except Exception:
                return {"value": raw}
        if isinstance(raw, str):
            return _normalize(raw)
        if isinstance(raw, Mapping):
            return dict(raw)
        return {"value": raw}

    def __del__(self) -> None:  # pragma: no cover - best effort
        """Ensure background resources are stopped when GC'd."""
        try:
            self.stop()
        except Exception:
            pass


def _normalize(value: str) -> dict[str, Any]:
    """Decode string/JSON payloads into dicts; wrap other values under 'value'."""
    try:
        loaded = json.loads(value)
        if isinstance(loaded, Mapping):
            return dict(loaded)
        return {"value": loaded}
    except Exception:
        return {"value": value}


def _estimate_size(payload: Mapping[str, Any]) -> int:
    """Approximate payload size in bytes for retention accounting."""
    try:
        return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    except Exception:
        try:
            return len(str(payload).encode("utf-8"))
        except Exception:
            return 0
