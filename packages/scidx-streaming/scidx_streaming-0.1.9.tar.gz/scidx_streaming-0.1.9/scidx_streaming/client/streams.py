"""Stream helpers for ``StreamingClient``."""

from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import TimeoutError as FutureTimeout
import time
from typing import Sequence

from ..data_cleaning import CompiledFilters
from ..streams import consumer as stream_consumer
from ..streams.creation import base as creation_base
from ..streams.creation import create_stream as _create_stream

logger = logging.getLogger(__name__)


def create_stream(
    self: "StreamingClient",
    *,
    resource_ids: Sequence[str],
    filters: CompiledFilters | None = None,
    description: str | None = None,
    server: str | None = None,
    username: str | None = None,
    password: str | None = None,
    use_kafka: bool = True,
):
    """Create a derived stream from registered resource definitions.

    Parameters
    ----------
    resource_ids : Sequence[str] (required)
        Resource definition IDs to fan-in.
    filters : CompiledFilters | None (optional, default None)
        Optional compiled filters from ``compile_filters``.
    description : str | None (optional, default None)
        Human-readable description stored with the derived resource.
    server : str | None (optional, default None)
        ndp_ep scope override when resolving CKAN/Kafka.
    username, password : str | None (optional, default None)
        Optional auth forwarded to source handlers (Kafka today).
    use_kafka : bool (optional, default True)
        When False, skip Kafka/CKAN registration and build a local-only stream
        for in-process consumption.

    Returns
    -------
    DerivedStreamResult | LocalStreamResult
        Structured response containing:
        - ``topic`` – derived Kafka topic name or local stream label
        - ``resource`` – CKAN resource entry (Kafka mode only)
        - ``dataset_id`` – dataset where the derived resource is stored (Kafka mode only)
        - ``sources`` – source resource metadata used to build the stream
        - ``filters`` – filter payloads applied
        - ``created_topic`` – whether the topic was newly created (Kafka mode only)
        - ``connect(...)`` – helper to return a consumer handle bound to this topic

    Raises
    ------
    ValueError
        If no resource IDs are provided.
    NotImplementedError
        If a requested source type is unsupported.
    RuntimeError
        If Kafka topic creation or CKAN registration fails.
    """

    return _create_stream(
        self,
        resource_ids=resource_ids,
        filters=filters,
        description=description,
        server=server,
        username=username,
        password=password,
        use_kafka=use_kafka,
    )


def consume_stream(
    self: "StreamingClient",
    topic: str,
    *,
    host: str | None = None,
    port: int | None = None,
    from_beginning: bool | None = None,
    retention_max_records: int | None = None,
    retention_max_bytes: int | None = None,
    retention_max_age_seconds: int | None = None,
    poll_interval: float | None = None,
    store_path: str | None = None,
):
    """Create an on-demand consumer for an already existing derived topic.

    Parameters
    ----------
    topic : str (required)
        Kafka topic name to consume.
    host, port : str | int | None (optional, default None)
        Optional broker overrides; default to the client's resolved Kafka host/port.
    from_beginning : bool | None (optional, default None)
        If set, overrides the handle's default offset behaviour.
    retention_max_records, retention_max_bytes, retention_max_age_seconds : int | None (optional, default None)
        Optional buffer limits for the in-memory store.
    poll_interval : float | None (optional, default None)
        Seconds between poll calls.
    store_path : str | None (optional, default None)
        Optional CSV file path for persistence.

    Returns
    -------
    StreamHandle
        Configured consumer handle (not started) with retention/poll overrides applied.
    """

    resolved_host = host or self.kafka_host
    resolved_port = port or self.kafka_port
    handle = stream_consumer.StreamHandle(
        topic=topic,
        overrides={"host": resolved_host, "port": resolved_port},
        store_path=store_path,
    )

    if from_beginning is not None:
        handle._default_from_beginning = bool(from_beginning)
    if any(val is not None for val in (retention_max_records, retention_max_bytes, retention_max_age_seconds)):
        handle.set_retention(
            max_records=retention_max_records,
            max_bytes=retention_max_bytes,
            max_age_seconds=retention_max_age_seconds,
        )
    if poll_interval is not None:
        handle._poll_interval = poll_interval

    return handle


def view_my_streams(
    self: "StreamingClient",
    *,
    server: str | None = None,
    include_details: bool = False,
    preview_limit: int = 5,
):
    """Print and return streams owned by the authenticated user.

    Parameters
    ----------
    server : str | None
        Optional CKAN scope override for resource lookups (used only when details are requested).
    include_details : bool
        When True, cross-reference CKAN resources and report per-topic metadata. Defaults to False for speed.
    preview_limit : int
        When details are disabled, limit the number of topic names printed (keeps output short).
    """

    prefix = creation_base.user_topic_base(self)
    topics = creation_base.list_topics(self)
    user_topics = sorted(topic for topic in topics if topic.startswith(prefix))
    registry = getattr(self, "_derived_producers", {}) if hasattr(self, "_derived_producers") else {}

    rows = []
    print(f"Found {len(user_topics)} stream(s) for prefix '{prefix}':")
    if not user_topics:
        print("  none")
        return rows

    if not include_details:
        preview = user_topics[:preview_limit]
        for topic in preview:
            suffix = topic[len(prefix) :] if topic.startswith(prefix) else topic
            print(f"  [{suffix}] topic={topic}")
            rows.append({"topic": topic, "suffix": suffix})
        if len(user_topics) > preview_limit:
            print(f"  ...and {len(user_topics) - preview_limit} more (use include_details=True to enumerate all).")
        return rows

    for topic in user_topics:
        matches = creation_base.find_resources_for_topic(self, topic, server=server)
        resource_ids: list[str] = []
        dataset_ids: list[str] = []
        inactive = False
        scope = None
        for dataset, scope_match, idx in matches:
            resources = dataset.get("resources") or []
            resource = resources[idx] if idx < len(resources) else {}
            rid = resource.get("id") or resource.get("name")
            if rid:
                resource_ids.append(str(rid))
            ds_identifier = dataset.get("id") or dataset.get("name")
            if ds_identifier:
                dataset_ids.append(str(ds_identifier))
            if resource.get("inactive") or resource.get("state") == "inactive":
                inactive = True
            scope = scope or scope_match

        suffix = topic[len(prefix) :] if topic.startswith(prefix) else topic
        producer_running = topic in registry if isinstance(registry, dict) else False
        status_bits = []
        status_bits.append("inactive" if inactive else "active")
        if producer_running:
            status_bits.append("local-producer")
        status = ",".join(status_bits)
        print(
            f"  [{suffix}] topic={topic} resources={resource_ids or ['-']} datasets={dataset_ids or ['-']} status={status}"
        )
        rows.append(
            {
                "topic": topic,
                "suffix": suffix,
                "resources": tuple(resource_ids),
                "datasets": tuple(dataset_ids),
                "inactive": inactive,
                "scope": scope,
                "local_producer": producer_running,
            }
        )
    return rows


def delete_my_stream(
    self: "StreamingClient",
    target: str | int = "all",
    *,
    server: str | None = None,
    delete_topic: bool = True,
    timeout_seconds: float | None = None,
):
    """Delete one or more derived streams owned by the authenticated user.

    Parameters
    ----------
    target : str | int (default "all")
        "all" to delete every stream for the current user, a numeric suffix
        (e.g. 0–50) to delete a specific stream id, or a full topic name.
    server : str | None
        Optional CKAN scope override.
    delete_topic : bool
        When False, only CKAN resources are removed (Kafka topic preserved).
    timeout_seconds : float | None
        Optional wall-clock timeout for the deletion routine. When None, each step uses a 30s timeout while the overall call remains unbounded.
    """

    prefix = creation_base.user_topic_base(self)
    topics = [topic for topic in creation_base.list_topics(self) if topic.startswith(prefix)]
    if target == "all":
        selected = topics
    else:
        suffix = str(target)
        if isinstance(target, int) or suffix.isdigit():
            selected = [topic for topic in topics if topic.endswith(f"_{suffix}")]
        else:
            selected = [topic for topic in topics if topic == suffix or topic.endswith(f"_{suffix}")]
        if not selected:
            raise ValueError(f"No derived stream found for target '{target}' with prefix '{prefix}'.")

    registry = getattr(self, "_derived_producers", None)
    print(f"delete_my_stream: deleting {len(selected)} stream(s) for prefix '{prefix}': {selected}")

    step_timeout = max(2.0, min(timeout_seconds, 30.0)) if timeout_seconds is not None else 30.0

    async def _run_step(label: str, coro):
        """Run a step with optional timeout and error handling."""
        t0 = time.monotonic()
        try:
            if step_timeout is not None:
                result = await asyncio.wait_for(coro, timeout=step_timeout)
            else:
                result = await coro
            return result, (time.monotonic() - t0) * 1000, None
        except asyncio.TimeoutError as exc:
            logger.error("delete_my_stream step '%s' timed out after %.1fs", label, step_timeout)
            return None, (time.monotonic() - t0) * 1000, exc
        except Exception as exc:  # pragma: no cover - runtime dependent
            logger.error("delete_my_stream step '%s' failed: %s", label, exc)
            return None, (time.monotonic() - t0) * 1000, exc

    async def _delete_one(topic: str, producer):
        timings: dict[str, float] = {}
        started = time.monotonic()
        print(f"[delete_my_stream] topic={topic} starting", flush=True)
        # Remove from registry up front to prevent future reuse while deleting.
        if isinstance(registry, dict):
            producer = registry.pop(topic, producer)

        stop_timeout = 5.0 if timeout_seconds is None else min(timeout_seconds, 10.0)
        if producer:
            try:
                # Dispose first so no restart happens while we're stopping.
                producer.dispose()
                print(f"[delete_my_stream] topic={topic} stopping producer (timeout={stop_timeout}s)", flush=True)
                await _stop_producer_cross_loop(
                    producer,
                    reason="user_delete",
                    mark_inactive=True,
                    timeout=stop_timeout,
                )
                timings["stop_producer_ms"] = (time.monotonic() - started) * 1000
                print(f"[delete_my_stream] topic={topic} producer stopped in {timings['stop_producer_ms']:.1f}ms", flush=True)
            except Exception as exc:
                logger.warning("Failed to stop producer for topic %s: %s", topic, exc)
                try:
                    await producer.force_close()
                except Exception:
                    logger.debug("Force close failed for producer %s", topic, exc_info=True)
        t0 = time.monotonic()
        print(f"[delete_my_stream] topic={topic} deleting CKAN resources (timeout={step_timeout}s)", flush=True)
        deleted_resources, dur, err = await _run_step(
            "delete_resources",
            asyncio.to_thread(creation_base.delete_resources_for_topic, self, topic, server=server),
        )
        timings["delete_resources_ms"] = dur
        print(f"[delete_my_stream] topic={topic} deleted_resources={deleted_resources} "
              f"in {timings['delete_resources_ms']:.1f}ms error={err}", flush=True)

        topic_removed = False
        if delete_topic:
            print(f"[delete_my_stream] topic={topic} deleting Kafka topic (timeout={step_timeout}s)", flush=True)
            topic_removed, dur, err = await _run_step(
                "delete_topic",
                asyncio.to_thread(creation_base.delete_topic, self, topic, force=True),
            )
            timings["delete_topic_ms"] = dur
            print(f"[delete_my_stream] topic={topic} delete_topic result={topic_removed} "
                  f"in {timings.get('delete_topic_ms', 0.0):.1f}ms error={err}", flush=True)

        still_present = False
        if delete_topic:
            still_present, dur, err = await _run_step(
                "list_topics",
                asyncio.to_thread(creation_base.list_topics, self),
            )
            timings["list_topics_ms"] = dur
            present = topic in tuple(still_present or ())
            still_present = present
            print(f"[delete_my_stream] topic={topic} list_topics present={still_present} "
                  f"in {timings.get('list_topics_ms', 0.0):.1f}ms error={err}", flush=True)
        if still_present and delete_topic:
            # Retry once in case Kafka metadata lagged.
            try:
                t1 = time.monotonic()
                print(f"[delete_my_stream] topic={topic} retrying delete_topic", flush=True)
                topic_removed, dur, err = await _run_step(
                    "retry_delete_topic",
                    asyncio.to_thread(creation_base.delete_topic, self, topic, force=True),
                )
                timings["retry_delete_topic_ms"] = (time.monotonic() - t1) * 1000
                still_present = topic in tuple(await asyncio.to_thread(creation_base.list_topics, self) or ())
                print(f"[delete_my_stream] topic={topic} retry delete_topic result={topic_removed} present={still_present} "
                      f"in {timings['retry_delete_topic_ms']:.1f}ms error={err}", flush=True)
            except Exception:
                logger.debug("Retry delete_topic failed for %s", topic, exc_info=True)
        if still_present:
            logger.error("Kafka topic %s still present after delete attempt", topic)
        timings["total_ms"] = (time.monotonic() - started) * 1000
        print(f"[delete_my_stream] topic={topic} finished total={timings['total_ms']:.1f}ms "
              f"deleted_resources={deleted_resources} deleted_topic={topic_removed} still_present={still_present}",
              flush=True)
        logger.info(
            "delete_my_stream topic=%s timings_ms=%s deleted_resources=%s deleted_topic=%s still_present=%s",
            topic,
            timings,
            deleted_resources,
            topic_removed,
            still_present,
        )
        return {
            "topic": topic,
            "deleted_resources": deleted_resources,
            "deleted_topic": topic_removed,
            "topic_present_after_delete": still_present,
            "timings_ms": timings,
        }

    async def _delete_all():
        results = []
        for topic in selected:
            producer = registry.get(topic) if isinstance(registry, dict) else None
            results.append(await _delete_one(topic, producer))
        return results

    results = _run_coro_blocking_anywhere(_delete_all(), timeout=timeout_seconds)
    _print_deletion_results(results)
    return results


def _print_deletion_results(results):
    print("Deletion summary:")
    for entry in results or []:
        if not isinstance(entry, dict):
            continue
        print(
            f"  topic={entry.get('topic')} deleted_resources={entry.get('deleted_resources')} "
            f"deleted_topic={entry.get('deleted_topic')} topic_present_after_delete={entry.get('topic_present_after_delete')} "
            f"timings_ms={entry.get('timings_ms')}"
        )


async def _stop_producer_cross_loop(producer, *, reason: str, mark_inactive: bool, timeout: float = 5.0):
    """Stop a DerivedProducer on its owning loop, even if called from another loop."""

    target_loop = getattr(producer, "loop", None)
    coro = producer.stop(reason=reason, mark_inactive=mark_inactive)
    if target_loop and target_loop.is_running() and target_loop is not asyncio.get_running_loop():
        try:
            fut = asyncio.run_coroutine_threadsafe(coro, target_loop)
            return fut.result(timeout=timeout)
        except FutureTimeout:
            fut.cancel()
            logger.warning("Timed out stopping producer for topic %s; forcing close.", getattr(producer, "topic", "?"))
            try:
                fut_close = asyncio.run_coroutine_threadsafe(producer.force_close(), target_loop)
                fut_close.result(timeout=2.0)
            except Exception:
                pass
            return None
        except Exception as exc:
            logger.warning("Cross-loop stop failed for topic %s (%s); falling back to direct await", getattr(producer, "topic", "?"), exc)
    return await coro


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

    result_box: dict[str, object] = {}
    error_box: dict[str, BaseException] = {}

    def _runner():
        try:
            if timeout is not None:
                result_box["result"] = asyncio.run(asyncio.wait_for(coro, timeout))
            else:
                result_box["result"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - runtime dependent
            error_box["error"] = exc

    thread = threading.Thread(target=_runner, name="delete-my-streams-dispatch", daemon=True)
    thread.start()
    thread.join(timeout if timeout is not None else None)

    if thread.is_alive():
        raise TimeoutError(f"Coroutine did not finish within {timeout} seconds")

    if error_box:
        raise error_box["error"]
    return result_box.get("result")


def _run_coro_blocking(coro):
    """Run a coroutine immediately or schedule it when a loop is active."""

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    return loop.create_task(coro)
