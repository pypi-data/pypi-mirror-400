"""Common dispatcher for derived stream creation."""

from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass
import uuid
from typing import Any, Mapping, Sequence, TYPE_CHECKING

from . import base
from .types import kafka as kafka_type
from ..runtime.producer import DerivedProducer

if TYPE_CHECKING:  # pragma: no cover - typing aid
    from ..local import LocalStreamResult

logger = logging.getLogger(__name__)


SUPPORTED_INPUT_TYPES = {
    "kafka",
    "csv",
    "json",
    "txt",
    "netcdf",
    "rss",
    "api_stream",
    "stream",
}


@dataclass(frozen=True)
class DerivedStreamResult:
    """Structured response from creating a derived stream.

    Attributes
    ----------
    streaming_client : Any
        Client used to build the stream; reused for lifecycle helpers.
    topic : str
        Derived Kafka topic name.
    resource : Mapping[str, Any] | None
        CKAN resource entry for the derived stream.
    dataset_id : str | None
        Dataset where the derived resource is registered.
    server : str | None
        CKAN scope used when registering the derived resource.
    sources : tuple[base.SourceResource, ...]
        Source resource metadata used to build the stream.
    filters : tuple[Any, ...]
        Filter payloads attached to the derived stream.
    created_topic : bool
        True if the topic was newly created; False if it already existed.
    source_types : tuple[str, ...]
        Normalized types of the source resources.
    producer : DerivedProducer | None
        Async producer responsible for fan-in.
    """

    streaming_client: Any
    topic: str
    resource: Mapping[str, Any] | None
    dataset_id: str | None
    server: str | None
    sources: tuple[base.SourceResource, ...]
    filters: tuple[Any, ...]
    created_topic: bool
    source_types: tuple[str, ...]
    producer: DerivedProducer | None

    @property
    def resource_id(self) -> str | None:
        """Convenience accessor for the derived CKAN resource id."""
        if self.resource and isinstance(self.resource, Mapping):
            rid = self.resource.get("id") or self.resource.get("name")
            return str(rid) if rid else None
        return None

    def connect(self, streaming_client: Any | None = None, **overrides: Any):
        """Return a consumer handle connected to the derived topic."""

        from ..builder import StreamBlueprint  # local import to avoid cycles
        from .. import consumer as stream_consumer

        client = streaming_client or self.streaming_client
        if client is None:
            raise ValueError("A streaming_client is required to connect to the derived stream.")

        resolved_host = overrides.pop("host", None) or getattr(client, "kafka_host", None)
        resolved_port = overrides.pop("port", None) or getattr(client, "kafka_port", None)
        blueprint = StreamBlueprint(
            resource_ids=tuple(source.id for source in self.sources),
            filters=self.filters,
            description=None,
        )
        return stream_consumer.StreamHandle(
            topic=self.topic,
            blueprint=blueprint,
            overrides={"host": resolved_host, "port": resolved_port},
            **overrides,
        )

    def deactivate(self, *, server: str | None = None, reason: str | None = None):
        """Stop fan-in and mark the derived resource inactive."""

        return _run_coro_blocking_anywhere(self.adeactivate(server=server, reason=reason))

    async def adeactivate(self, *, server: str | None = None, reason: str | None = None):
        """Async version of ``deactivate``."""

        target_server = server or self.server
        chosen_reason = reason or "user_deactivated"
        await self._stop_producer(reason=chosen_reason, mark_inactive=True)
        if self.resource_id:
            try:
                base.mark_resource_inactive(self.streaming_client, self.resource_id, reason=chosen_reason, server=target_server)
            except Exception as exc:  # pragma: no cover - CKAN dependent
                logger.warning("Failed to mark resource %s inactive: %s", self.resource_id, exc)
        return {"resource_id": self.resource_id, "server": target_server}

    def reactivate(self, *, server: str | None = None, reason: str | None = None):
        """Clear inactive flags and resume fan-in if possible."""

        return _run_coro_blocking_anywhere(self.areactivate(server=server, reason=reason))

    async def areactivate(self, *, server: str | None = None, reason: str | None = None):
        """Async version of ``reactivate``."""

        target_server = server or self.server
        started = False
        if self.resource_id:
            try:
                base.mark_resource_active(self.streaming_client, self.resource_id, reason=reason or "reactivated", server=target_server)
            except Exception as exc:  # pragma: no cover - CKAN dependent
                logger.warning("Failed to mark resource %s active: %s", self.resource_id, exc)
        if self.producer:
            task = self.producer.start()
            started = bool(task)
        return {"resource_id": self.resource_id, "producer_started": started, "server": target_server}

    def delete(self, *, server: str | None = None, delete_topic: bool = True):
        """Delete the derived stream (Kafka topic + CKAN resource)."""

        if self.streaming_client and hasattr(self.streaming_client, "delete_my_stream"):
            try:
                return self.streaming_client.delete_my_stream(
                    self.topic, server=server, delete_topic=delete_topic
                )
            except Exception as exc:
                logger.warning("Delegated delete_my_stream failed, falling back to direct delete: %s", exc)

        return _run_coro_blocking_anywhere(self.adelete(server=server, delete_topic=delete_topic))

    async def adelete(self, *, server: str | None = None, delete_topic: bool = True):
        """Async version of ``delete``."""

        target_server = server or self.server
        await self._stop_producer(reason="user_delete", mark_inactive=True)
        if self.producer:
            self.producer.dispose()
        deleted_resources = base.delete_resources_for_topic(
            self.streaming_client,
            self.topic,
            resource_ids=(self.resource_id,) if self.resource_id else (),
            server=target_server,
        )
        topic_removed = base.delete_topic(self.streaming_client, self.topic, force=True) if delete_topic else False
        self._forget_local_producer()
        return {"deleted_resources": deleted_resources, "deleted_topic": topic_removed, "server": target_server}

    # Internal helpers -------------------------------------------------
    async def _stop_producer(self, *, reason: str, mark_inactive: bool) -> bool:
        """Stop the local producer if it was created, optionally marking inactive."""

        if not self.producer:
            return False
        # Dispose early to prevent restarts while shutdown is in-flight.
        self.producer.dispose()
        try:
            await _stop_producer_cross_loop(self.producer, reason=reason, mark_inactive=mark_inactive)
            return True
        except Exception as exc:  # pragma: no cover - runtime dependent
            logger.warning("Failed to stop derived producer for topic %s: %s", self.topic, exc)
            return False

    def _forget_local_producer(self) -> None:
        """Remove the producer from the client's registry when present."""

        registry = getattr(self.streaming_client, "_derived_producers", None)
        if isinstance(registry, dict):
            registry.pop(self.topic, None)


def _run_coro_blocking_anywhere(coro, *, timeout: float | None = None):
    """Run a coroutine to completion, even when an event loop is already running.

    A timeout guards against indefinite blocking when the coroutine internally
    performs network or broker operations.
    """

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        if timeout is not None:
            return asyncio.run(asyncio.wait_for(coro, timeout))
        return asyncio.run(coro)

    result_box: dict[str, Any] = {}
    error_box: dict[str, BaseException] = {}

    def _runner():
        try:
            if timeout is not None:
                result_box["result"] = asyncio.run(asyncio.wait_for(coro, timeout))
            else:
                result_box["result"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - runtime dependent
            error_box["error"] = exc

    thread = threading.Thread(target=_runner, name="derived-stream-dispatch", daemon=True)
    thread.start()
    thread.join(timeout if timeout is not None else None)

    if thread.is_alive():
        raise TimeoutError(f"Coroutine did not finish within {timeout} seconds")

    if error_box:
        raise error_box["error"]
    return result_box.get("result")


async def _stop_producer_cross_loop(producer: DerivedProducer, *, reason: str, mark_inactive: bool, timeout: float = 5.0):
    """Stop a producer on its owning loop, even when called from another loop/thread."""

    target_loop = producer.loop
    coro = producer.stop(reason=reason, mark_inactive=mark_inactive)
    if target_loop and target_loop.is_running() and target_loop is not asyncio.get_running_loop():
        try:
            fut = asyncio.run_coroutine_threadsafe(coro, target_loop)
            return fut.result(timeout=timeout)
        except FutureTimeout:
            fut.cancel()
            logger.warning("Timed out stopping producer for topic %s; forcing close.", producer.topic)
            try:
                fut_close = asyncio.run_coroutine_threadsafe(producer.force_close(), target_loop)
                fut_close.result(timeout=2.0)
            except Exception:
                pass
            return None
        except Exception as exc:
            logger.warning("Cross-loop stop failed for topic %s (%s); falling back to direct await", producer.topic, exc)
    return await coro


def _start_producer(producer: DerivedProducer) -> None:
    """Launch the derived producer on the current event loop if running."""

    producer.start()


def create_stream(
    streaming_client: Any,
    *,
    resource_ids: Sequence[str],
    filters: Sequence[Any] | None = None,
    server: str | None = None,
    description: str | None = None,
    username: str | None = None,
    password: str | None = None,
    use_kafka: bool = True,
) -> DerivedStreamResult | LocalStreamResult:
    """Create a derived stream fed by supported source types.

    Parameters
    ----------
    streaming_client : Any
        Streaming client with CKAN/Kafka connectivity.
    resource_ids : Sequence[str]
        Resource identifiers to fan-in.
    filters : Sequence[Any] | None
        Optional compiled filters (placeholder today).
    server : str | None
        Preferred ndp_ep scope when resolving sources/CKAN registration.
    description : str | None
        Optional description stored with the derived resource.
    username, password : str | None
        Optional credentials forwarded to source handlers (Kafka).
    use_kafka : bool
        When True (default), creates a derived Kafka topic and registers it in
        CKAN. When False, skips Kafka/CKAN and returns a local fan-in result
        for in-process consumption only.

    Returns
    -------
    DerivedStreamResult | LocalStreamResult
        Kafka-backed streams return ``DerivedStreamResult``; local fan-in
        streams return ``LocalStreamResult``.

    Raises
    ------
    ValueError
        If ``resource_ids`` is empty.
    NotImplementedError
        If any source type is not supported.
    RuntimeError
        If Kafka topic creation fails.
    """

    if not resource_ids:
        raise ValueError("At least one consumption method id is required.")

    sources = base.resolve_sources(streaming_client, resource_ids, server=server)
    source_types = tuple((s.definition.get("type") or s.raw.get("format") or "").lower() for s in sources)
    unknown_types = {t for t in source_types if t not in SUPPORTED_INPUT_TYPES}
    if unknown_types:
        raise NotImplementedError(f"Stream creation for types {sorted(unknown_types)} is not implemented yet.")

    if not use_kafka:
        from ..local import LocalStreamResult
        suffix = uuid.uuid4().hex[:8]
        topic = f"local_{base.clean_user_id(getattr(streaming_client, 'user_id', None))}_{suffix}"
        return LocalStreamResult(
            streaming_client=streaming_client,
            topic=topic,
            sources=tuple(sources),
            filters=tuple(filters or ()),
            source_types=source_types,
            username=username,
            password=password,
        )

    # Derived output is always Kafka.
    kafka_result = kafka_type.create_kafka_stream(
        streaming_client,
        sources=sources,
        filters=filters,
        server=server,
        description=description,
    )

    producer = DerivedProducer(
        streaming_client=streaming_client,
        topic=kafka_result.topic,
        sources=sources,
        filters=tuple(filters or ()),
        resource_id=kafka_result.resource.get("id") if kafka_result.resource else None,
        username=username,
        password=password,
        server=kafka_result.scope,
    )
    _start_producer(producer)
    registry = getattr(streaming_client, "_derived_producers", None)
    if isinstance(registry, dict):
        registry[kafka_result.topic] = producer

    return DerivedStreamResult(
        streaming_client=streaming_client,
        topic=kafka_result.topic,
        resource=kafka_result.resource,
        dataset_id=kafka_result.dataset_id,
        server=kafka_result.scope,
        sources=tuple(sources),
        filters=tuple(filters or ()),
        created_topic=kafka_result.created_topic,
        source_types=source_types,
        producer=producer,
    )
