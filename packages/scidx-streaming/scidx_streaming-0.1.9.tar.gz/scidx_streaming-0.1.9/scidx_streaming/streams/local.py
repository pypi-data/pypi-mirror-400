"""Local-only stream fan-in that skips Kafka/CKAN registration."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .consumer import StreamHandle
from .creation import base
from .runtime.handlers.kafka import consume_kafka_source
from ..data_cleaning import apply_filters

logger = logging.getLogger(__name__)


class LocalFanIn:
    """Async fan-in that consumes sources and pushes records into a handle buffer."""

    def __init__(
        self,
        *,
        label: str,
        handle: StreamHandle,
        sources: Sequence[base.SourceResource],
        filters: Sequence[Any],
        username: str | None,
        password: str | None,
        from_beginning: bool,
    ) -> None:
        self.label = label
        self.handle = handle
        self.sources = list(sources)
        self.filters = tuple(filters or ())
        self.username = username
        self.password = password
        self.from_beginning = from_beginning

        self._tasks: list[asyncio.Task] = []
        self._stop_event = asyncio.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task | None = None
        self._thread: threading.Thread | None = None

    # Lifecycle ---------------------------------------------------------
    def start(self) -> asyncio.Task | None:
        """Start fan-in on the current loop if present, otherwise background."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return self.start_background()
        return self._start_on_loop(loop)

    def start_background(self) -> asyncio.Task | None:
        """Start fan-in on a dedicated background loop."""
        if self._thread and self._thread.is_alive():
            return self._task

        def _runner() -> None:
            loop = asyncio.new_event_loop()
            self._loop = loop
            asyncio.set_event_loop(loop)
            try:
                self._task = loop.create_task(self.run(), name=f"local-fanin-{self.label}")
                loop.run_until_complete(self._task)
            finally:
                pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
                for task in pending:
                    task.cancel()
                if pending:
                    try:
                        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass
                loop.close()

        self._thread = threading.Thread(target=_runner, name=f"local-fanin-{self.label}", daemon=True)
        self._thread.start()
        return self._task

    def _start_on_loop(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        """Start fan-in on a specific loop, reusing an existing task when present."""
        if self._task and not self._task.done():
            return self._task
        self._loop = loop
        self._task = loop.create_task(self.run(), name=f"local-fanin-{self.label}")
        return self._task

    def stop(self, *, timeout: float = 5.0) -> None:
        """Signal fan-in to stop and wait briefly for shutdown."""
        self._stop_event.set()
        loop = self._loop
        if loop and loop.is_running() and self._task:
            try:
                fut = asyncio.run_coroutine_threadsafe(self._shutdown_tasks(), loop)
                fut.result(timeout=timeout)
            except Exception:
                logger.debug("Local fan-in stop timed out for %s", self.label, exc_info=True)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout)

    async def run(self) -> None:
        """Start handlers for each source and monitor failures."""
        self._stop_event = asyncio.Event()
        self._loop = asyncio.get_running_loop()
        self._tasks = []

        for source in self.sources:
            handler = self._handler_for_source(source)
            if handler:
                task = asyncio.create_task(handler(source), name=f"local-source-{source.id}")
                self._tasks.append(task)
            else:
                logger.warning("Local stream %s: unsupported source type %s", self.label, source.definition.get("type"))

        await self._watch_tasks()

    async def _shutdown_tasks(self) -> None:
        """Cancel tasks and wait for completion."""
        self._stop_event.set()
        for task in self._tasks:
            if not task.done():
                task.cancel()
        if self._tasks:
            try:
                await asyncio.gather(*self._tasks, return_exceptions=True)
            except Exception:
                logger.debug("Local fan-in gather failed for %s", self.label, exc_info=True)
        self._tasks = []
        self._task = None

    async def _watch_tasks(self) -> None:
        """Monitor ingestion tasks and propagate stop on failure."""
        if not self._tasks:
            logger.warning("Local stream %s started with no sources.", self.label)
            return

        pending = {task for task in self._tasks}
        while pending and not self._stop_event.is_set():
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
            for task in done:
                if task.cancelled():
                    continue
                exc = task.exception()
                if exc:
                    logger.error("Local stream %s source task failed: %s", self.label, exc)
                    self._stop_event.set()
                    for p in pending:
                        if not p.done():
                            p.cancel()
                    break
        self._stop_event.set()
        for task in pending:
            task.cancel()
        if pending:
            try:
                await asyncio.gather(*pending, return_exceptions=True)
            except Exception:
                logger.debug("Local stream %s pending task gather failed", self.label, exc_info=True)

    # Handlers ----------------------------------------------------------
    def _handler_for_source(self, source: base.SourceResource):
        source_type = (source.definition.get("type") or source.raw.get("format") or "").lower()
        if source_type == "kafka":
            return self._consume_kafka_source
        return None

    async def _consume_kafka_source(self, source: base.SourceResource) -> None:
        await consume_kafka_source(
            source=source,
            stop_event=self._stop_event,
            username=self.username,
            password=self.password,
            forward_message=self._forward_message,
            mark_inactive=self._mark_inactive,
            auto_offset_reset="earliest" if self.from_beginning else "latest",
        )

    async def _forward_message(self, payload: bytes) -> None:
        """Decode/filter payloads and push them into the handle buffer."""
        for record in self._prepare_records(payload):
            self.handle.ingest([record])

    def _prepare_records(self, payload: bytes) -> list[Mapping[str, Any]]:
        """Decode bytes → records and apply filters when provided."""
        if payload is None:
            return []
        decoded = self._decode_payload(payload)
        if decoded is None:
            return []

        rows: list[Mapping[str, Any]]
        if self.filters:
            if not isinstance(decoded, list):
                decoded = [decoded]
            if not decoded:
                return []
            try:
                filtered = apply_filters(decoded, self.filters)
            except Exception:
                logger.debug("Filter application failed for local stream %s", self.label, exc_info=True)
                return []
            rows = filtered.to_dict(orient="records")
        else:
            rows = decoded if isinstance(decoded, list) else [decoded]

        normalized: list[Mapping[str, Any]] = []
        for row in rows:
            if isinstance(row, Mapping):
                normalized.append(dict(row))
            else:
                normalized.append({"value": row})
        return normalized

    def _decode_payload(self, payload: bytes) -> Any:
        """Return a best-effort decoded payload for filtering/persistence."""
        if isinstance(payload, (bytes, bytearray, memoryview)):
            try:
                payload = bytes(payload).decode("utf-8")
            except Exception:
                return None
        if isinstance(payload, str):
            try:
                return json.loads(payload)
            except Exception:
                return {"value": payload}
        if isinstance(payload, Mapping):
            return dict(payload)
        return {"value": payload}

    async def _mark_inactive(self, reason: str | None = None) -> None:
        """Stop fan-in; no CKAN resource is involved in local mode."""
        logger.warning("Local stream %s marked inactive (reason=%s)", self.label, reason)
        self._stop_event.set()


class LocalStreamHandle(StreamHandle):
    """StreamHandle variant that runs source fan-in locally (no Kafka topic)."""

    def __init__(
        self,
        *,
        topic: str,
        sources: Sequence[base.SourceResource],
        filters: Sequence[Any] | None = None,
        username: str | None = None,
        password: str | None = None,
        store_path: str | None = None,
    ) -> None:
        super().__init__(topic=topic, store_path=store_path)
        self._sources = tuple(sources)
        self._filters = tuple(filters or ())
        self._username = username
        self._password = password
        self._fanin: LocalFanIn | None = None
        self._last_from_beginning = False

    def start(
        self,
        *,
        from_beginning: bool | None = None,
        retention_max_records: int | None = None,
        retention_max_bytes: int | None = None,
        retention_max_age_seconds: int | None = None,
        poll_interval: float | None = None,
    ) -> StreamHandle:
        """Start local fan-in and buffering."""
        if self._running:
            return self

        self._buffer.configure(
            max_records=retention_max_records,
            max_bytes=retention_max_bytes,
            max_age_seconds=retention_max_age_seconds,
        )
        effective_from_beginning = self._default_from_beginning if from_beginning is None else bool(from_beginning)
        self._last_from_beginning = effective_from_beginning

        self._fanin = LocalFanIn(
            label=self.topic,
            handle=self,
            sources=self._sources,
            filters=self._filters,
            username=self._username,
            password=self._password,
            from_beginning=effective_from_beginning,
        )
        self._fanin.start()
        self._running = True
        return self

    def stop(self) -> None:
        """Stop local fan-in and close any open store file."""
        if self._fanin:
            self._fanin.stop()
            self._fanin = None
        super().stop()

    def resume(self, **kwargs: Any) -> StreamHandle:
        """Resume local fan-in with the previous offset behaviour unless overridden."""
        if "from_beginning" not in kwargs:
            kwargs["from_beginning"] = self._last_from_beginning
        return self.start(**kwargs)


@dataclass(frozen=True)
class LocalStreamResult:
    """Structured response for a local-only derived stream."""

    streaming_client: Any
    topic: str
    sources: tuple[base.SourceResource, ...]
    filters: tuple[Any, ...]
    source_types: tuple[str, ...]
    username: str | None
    password: str | None
    server: str | None = None
    producer: Any | None = None
    _handles: tuple["LocalStreamHandle", ...] = field(default_factory=tuple, init=False, repr=False, compare=False)
    _store_paths: tuple[Path, ...] = field(default_factory=tuple, init=False, repr=False, compare=False)

    @property
    def resource(self) -> None:
        """Compatibility shim; local streams do not register CKAN resources."""
        return None

    @property
    def resource_id(self) -> None:
        return None

    @property
    def dataset_id(self) -> None:
        return None

    @property
    def created_topic(self) -> bool:
        return False

    def connect(self, streaming_client: Any | None = None, **overrides: Any) -> LocalStreamHandle:
        """Return a local stream handle ready to start fan-in."""
        client = streaming_client or self.streaming_client
        _ = client  # kept for symmetry; not required today
        store_path = overrides.pop("store_path", None)
        handle = LocalStreamHandle(
            topic=self.topic,
            sources=self.sources,
            filters=self.filters,
            username=self.username,
            password=self.password,
            store_path=store_path,
        )
        # Track handles and store paths for cleanup on delete().
        handles = getattr(self, "_handles", tuple())
        paths = getattr(self, "_store_paths", tuple())
        object.__setattr__(self, "_handles", handles + (handle,))
        if store_path:
            path_obj = Path(store_path)
            object.__setattr__(self, "_store_paths", paths + (path_obj,))
        return handle

    def deactivate(self, *, server: str | None = None, reason: str | None = None) -> Mapping[str, Any]:
        """Parity with DerivedStreamResult.deactivate (no-op for local streams)."""
        _ = reason
        return {"resource_id": None, "server": server or self.server, "local": True}

    def reactivate(self, *, server: str | None = None, reason: str | None = None) -> Mapping[str, Any]:
        """Parity with DerivedStreamResult.reactivate (no-op for local streams)."""
        _ = reason
        return {"resource_id": None, "producer_started": False, "server": server or self.server, "local": True}

    def delete(self, *, server: str | None = None, delete_topic: bool = True) -> Mapping[str, Any]:
        """Parity with DerivedStreamResult.delete (no-op for local streams)."""
        _ = delete_topic
        stopped = 0
        for handle in getattr(self, "_handles", ()):
            try:
                handle.stop()
                stopped += 1
            except Exception:
                logger.debug("Failed to stop local handle %s", getattr(handle, "topic", "?"), exc_info=True)

        seen_paths = []
        path_candidates = list(getattr(self, "_store_paths", ()))
        for handle in getattr(self, "_handles", ()):
            candidate = getattr(handle, "_store_path", None)
            if candidate:
                path_candidates.append(Path(candidate))
        # Deduplicate while preserving order
        deduped_paths: tuple[Path, ...] = tuple(dict.fromkeys(path_candidates))

        return {
            "deleted_resources": 0,
            "deleted_topic": False,
            "server": server or self.server,
            "local": True,
            "stopped_handles": stopped,
            "store_paths": tuple(str(p) for p in deduped_paths),
        }
