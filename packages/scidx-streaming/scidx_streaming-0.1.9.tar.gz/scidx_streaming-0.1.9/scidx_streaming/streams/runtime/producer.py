"""Async producer that fan-in multiple source types into a derived Kafka topic."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
import threading
from typing import Any, Iterable, Mapping, Sequence

from aiokafka import AIOKafkaProducer

from ..creation import base
from .handlers.kafka import consume_kafka_source
from ...data_cleaning import apply_filters

logger = logging.getLogger(__name__)


@dataclass
class _TaskBundle:
    task: asyncio.Task
    description: str


class DerivedProducer:
    """Fan-in ingestion from multiple source resources into a derived Kafka topic."""

    def __init__(
        self,
        *,
        streaming_client: Any,
        topic: str,
        sources: Sequence[base.SourceResource],
        filters: Sequence[Any],
        resource_id: str | None,
        username: str | None = None,
        password: str | None = None,
        server: str | None = None,
    ) -> None:
        """Initialize the derived producer with context and optional auth."""
        self.streaming_client = streaming_client
        self.topic = topic
        self.sources = list(sources)
        self.filters = tuple(filters)
        self.resource_id = resource_id
        self.username = username
        self.password = password
        self.server = server

        bootstrap = f"{streaming_client.kafka_host}:{streaming_client.kafka_port}"
        self._producer_factory = lambda: AIOKafkaProducer(
            bootstrap_servers=bootstrap,
            acks="all",
        )
        self._producer: AIOKafkaProducer | None = None
        self._tasks: list[_TaskBundle] = []
        self._stop_event = asyncio.Event()
        self._started = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._task: asyncio.Task | None = None
        self._stop_reason: str | None = None
        self._marked_inactive_reason: str | None = None
        self._disposed: bool = False
        self._loop_thread: threading.Thread | None = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop | None:
        """Return the loop used by the producer when running."""
        return self._loop

    def start(self) -> asyncio.Task | None:
        """Start the producer on the current running event loop."""
        if self._disposed:
            logger.debug("Derived producer for topic %s was disposed; start() ignored.", self.topic)
            return None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return self.start_background()
        return self._start_on_loop(loop)

    def start_background(self) -> asyncio.Task | None:
        """Start the producer on a dedicated background event loop."""
        if self._disposed:
            logger.debug("Derived producer for topic %s was disposed; start_background ignored.", self.topic)
            return None
        if self._loop_thread and self._loop_thread.is_alive():
            return self._task

        def _runner() -> None:
            loop = asyncio.new_event_loop()
            self._loop = loop
            asyncio.set_event_loop(loop)
            try:
                self._task = loop.create_task(self.run(), name=f"derived-producer-{self.topic}")
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

        self._loop_thread = threading.Thread(target=_runner, name=f"derived-producer-{self.topic}", daemon=True)
        self._loop_thread.start()
        return self._task

    def _start_on_loop(self, loop: asyncio.AbstractEventLoop) -> asyncio.Task:
        """Start on a specific loop, reusing an existing task when present."""
        if self._disposed:
            logger.debug("Derived producer for topic %s was disposed; start_on_loop ignored.", self.topic)
            return self._task or loop.create_task(self._noop(), name="derived-producer-disposed")
        if self._task and not self._task.done():
            return self._task
        self._loop = loop
        self._task = loop.create_task(self.run(), name=f"derived-producer-{self.topic}")
        return self._task

    def _reset_state(self) -> None:
        """Reset run state to allow clean restarts."""
        self._tasks = []
        self._stop_event = asyncio.Event()
        self._stop_reason = None
        self._marked_inactive_reason = None

    async def run(self) -> None:
        """Start all ingestion tasks and wait for completion or failure.

        Starts the Kafka producer, spawns handlers per source, monitors for
        exceptions, and marks the derived resource inactive on failure/stop.
        """

        if self._started:
            return
        if self._disposed:
            logger.debug("Derived producer for topic %s was disposed; run() aborted.", self.topic)
            return
        self._reset_state()
        self._started = True
        self._loop = asyncio.get_running_loop()
        self._producer = self._producer_factory()
        try:
            await self._producer.start()
        except Exception as exc:
            logger.error("Failed to start derived producer for topic %s: %s", self.topic, exc)
            await self._mark_inactive(reason="producer_start_failure")
            return

        try:
            for source in self.sources:
                handler = self._handler_for_source(source)
                if handler:
                    task = asyncio.create_task(handler(source), name=f"derived-source-{source.id}")
                    self._tasks.append(_TaskBundle(task=task, description=source.id))
                else:
                    logger.warning("Source type %s not implemented; skipping id=%s", source.definition.get("type"), source.id)

            # Wait for tasks, reacting to failures.
            await self._watch_tasks()
            await self._mark_inactive(reason=self._stop_reason or "stopped")
        finally:
            await self._shutdown_producer()
            self._started = False
            self._task = None

    async def stop(self, *, reason: str | None = None, mark_inactive: bool = True) -> None:
        """Signal ingestion to stop, cancel tasks, and mark resource inactive."""

        if reason:
            self._stop_reason = reason
        self._disposed = True
        self._stop_event.set()
        for bundle in self._tasks:
            if not bundle.task.done():
                bundle.task.cancel()
        for bundle in self._tasks:
            try:
                await bundle.task
            except asyncio.CancelledError:
                pass
            except Exception as exc:
                logger.error("Error stopping task %s: %s", bundle.description, exc)
        await self._shutdown_producer()
        if mark_inactive:
            await self._mark_inactive(reason=self._stop_reason or "stopped")
        self._task = None
        self._started = False
        self._tasks = []

    async def force_close(self) -> None:
        """Best-effort immediate shutdown without waiting on handlers."""
        self._stop_event.set()
        for bundle in self._tasks:
            if not bundle.task.done():
                bundle.task.cancel()
        await self._shutdown_producer()
        self._task = None
        self._started = False
        self._tasks = []

    def dispose(self) -> None:
        """Mark the producer as permanently stopped; start calls are ignored."""
        self._disposed = True
        self._stop_event.set()

    # Internal helpers -------------------------------------------------
    async def _watch_tasks(self) -> None:
        """Monitor all ingestion tasks and mark resource inactive on failure."""

        if not self._tasks:
            logger.warning("No ingestion tasks started for derived topic %s", self.topic)
            return

        pending = {bundle.task for bundle in self._tasks}
        while pending and not self._stop_event.is_set():
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
            for task in done:
                if task.cancelled():
                    continue
                exc = task.exception()
                if exc:
                    logger.error("Ingestion task failed for topic %s: %s", self.topic, exc)
                    self._stop_reason = self._stop_reason or "ingestion_failure"
                    await self._mark_inactive(reason="ingestion_failure")
                    self._stop_event.set()
                    for bundle in self._tasks:
                        if not bundle.task.done():
                            bundle.task.cancel()
                    break

    def _handler_for_source(self, source: base.SourceResource):
        """Return the async handler function for a source type (None if unsupported)."""
        source_type = (source.definition.get("type") or source.raw.get("format") or "").lower()
        if source_type == "kafka":
            return self._consume_kafka_source
        # Future: csv/json/rss/netcdf/stream/api_stream handlers go here.
        return None

    async def _consume_kafka_source(self, source: base.SourceResource) -> None:
            await consume_kafka_source(
                source=source,
                stop_event=self._stop_event,
                username=self.username,
                password=self.password,
                forward_message=self._forward_message,
                mark_inactive=self._mark_inactive,
            )

    async def _forward_message(self, payload: bytes) -> None:
        """Forward a payload into the derived topic, applying filters when present."""

        try:
            filtered_payloads = self._filter_payload(payload)
            if not filtered_payloads:
                return
            if not self._producer:
                return
            for item in filtered_payloads:
                await self._producer.send_and_wait(self.topic, item)
        except Exception as exc:
            logger.error("Failed to forward message to derived topic %s: %s", self.topic, exc)
            await self._mark_inactive(reason="forward_failure")
            self._stop_event.set()

    def _filter_payload(self, payload: bytes) -> list[bytes]:
        """Apply compiled filters to a payload; return zero or more payloads to forward."""

        if not self.filters:
            return [payload]

        try:
            decoded = json.loads(payload.decode("utf-8"))
        except Exception:
            logger.debug("Skipping payload that failed JSON decode for topic %s", self.topic, exc_info=True)
            return []

        try:
            filtered_df = apply_filters(decoded if isinstance(decoded, list) else [decoded], self.filters)
        except Exception:
            logger.debug("Filter application failed for topic %s", self.topic, exc_info=True)
            return []

        if filtered_df.empty:
            return []

        records = filtered_df.to_dict(orient="records")
        return [json.dumps(record).encode("utf-8") for record in records]

    async def _shutdown_producer(self) -> None:
        """Stop the underlying Kafka producer quietly."""
        producer = self._producer
        self._producer = None
        if not producer:
            return
        try:
            await producer.stop()
        except Exception:
            logger.debug("Derived producer shutdown failed for topic %s", self.topic, exc_info=True)

    async def _mark_inactive(self, reason: str | None = None) -> None:
        """Mark the derived CKAN resource inactive with an optional reason."""
        if not self.resource_id:
            return
        if self._marked_inactive_reason is not None:
            return
        self._marked_inactive_reason = reason or "stopped"
        try:
            base.mark_resource_inactive(
                self.streaming_client,
                self.resource_id,
                reason=reason,
                server=self.server,
            )
        except Exception:
            logger.debug("Failed to mark resource %s inactive", self.resource_id, exc_info=True)

    async def _noop(self) -> None:
        return
