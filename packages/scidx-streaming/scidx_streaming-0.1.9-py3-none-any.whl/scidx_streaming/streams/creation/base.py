"""Shared helpers for derived stream creation."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from kafka.admin import ConfigResource, ConfigResourceType
from kafka.errors import KafkaError, UnknownTopicOrPartitionError

from ...connectors.ckan import CKANActionError, call_action
from ...resources import delete_resource as delete_resource_fn
from ...resources import register_resource as register_resource_fn
from ...resources import update_resource as update_resource_fn
from ...resources.utils import datasets as dataset_utils
from ...resources.utils import registry as resource_registry

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SourceResource:
    """Resolved CKAN resource with dataset and scope metadata."""

    id: str
    dataset_id: str | None
    dataset_name: str | None
    definition: Mapping[str, Any]
    raw: Mapping[str, Any]
    scope: str | None


def resolve_sources(streaming_client: Any, resource_ids: Sequence[str], *, server: str | None = None) -> list[SourceResource]:
    """Locate CKAN resources by ID and return normalized definitions.

    Parameters
    ----------
    streaming_client : Any
        Streaming client exposing ``ep_client`` for CKAN lookups.
    resource_ids : Sequence[str]
        Resource identifiers to resolve.
    server : str | None
        Optional ndp_ep scope override.

    Returns
    -------
    list[SourceResource]
        Resolved resources with dataset metadata, definitions, and scope.

    Raises
    ------
    CKANActionError
        If any resource cannot be found.
    """

    ep_client = getattr(streaming_client, "ep_client", None)
    if ep_client is None:
        raise CKANActionError("Streaming client missing ep_client for CKAN lookups.")

    resolved: list[SourceResource] = []
    for rid in resource_ids:
        dataset, scope, idx = dataset_utils.locate_resource(ep_client, rid, preferred_scope=server)
        if dataset is None or idx is None:
            raise CKANActionError(f"Resource '{rid}' not found in CKAN.")

        resources = dataset.get("resources") or []
        raw_entry = resources[idx]
        definition = resource_registry.load_definition_from_resource(raw_entry)
        resolved.append(
            SourceResource(
                id=str(rid),
                dataset_id=str(dataset.get("id") or dataset.get("name") or ""),
                dataset_name=str(dataset.get("name") or dataset.get("id") or ""),
                definition=definition,
                raw=raw_entry,
                scope=scope,
            )
        )
        dataset_utils.remember_resource_hint(raw_entry, dataset)

    return resolved


def derive_prefix(ep_client: Any, *, override: str | None = None, default: str = "derived_stream_") -> str:
    """Resolve derived-topic prefix: override → ndp_ep config/env → default.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client possibly exposing kafka prefix in configuration.
    override : str | None
        Explicit prefix to use.
    default : str
        Fallback prefix when nothing else is provided.
    """

    if override:
        return str(override)

    env_prefix = os.getenv("SCIDX_KAFKA_PREFIX")
    if env_prefix:
        return env_prefix

    for attr in ("kafka_prefix", "KAFKA_PREFIX"):
        value = getattr(ep_client, attr, None)
        if value:
            return str(value)

    getter = getattr(ep_client, "get_configuration", None)
    if callable(getter):
        try:
            config = getter() or {}
            kafka_config = config.get("kafka") or {}
            for key in ("kafka_prefix", "prefix"):
                candidate = kafka_config.get(key) or config.get(key)
                if candidate:
                    return str(candidate)
        except Exception:  # pragma: no cover - defensive
            logger.debug("get_configuration failed while probing prefix", exc_info=True)

    return default


def derive_max_streams(ep_client: Any, *, override: int | None = None, default: int = 10) -> int:
    """Resolve maximum concurrent derived streams (override/env/config/default)."""

    if override is not None:
        return int(override)

    env_value = os.getenv("SCIDX_MAX_STREAMS")
    if env_value and env_value.isdigit():
        return int(env_value)

    for attr in ("max_streams", "MAX_STREAMS"):
        value = getattr(ep_client, attr, None)
        if isinstance(value, int):
            return value
        try:
            if isinstance(value, str) and value.isdigit():
                return int(value)
        except Exception:
            pass

    getter = getattr(ep_client, "get_configuration", None)
    if callable(getter):
        try:
            config = getter() or {}
            kafka_config = config.get("kafka") or {}
            for key in ("max_streams", "maxStreams", "stream_limit"):
                candidate = kafka_config.get(key) or config.get(key)
                if isinstance(candidate, int):
                    return candidate
                if isinstance(candidate, str) and candidate.isdigit():
                    return int(candidate)
        except Exception:  # pragma: no cover - defensive
            logger.debug("get_configuration failed while probing max_streams", exc_info=True)

    return default


def clean_user_id(user_id: str | None) -> str:
    """Return a Kafka-topic-safe user identifier (alnum/_/-, fallback anonymous)."""

    if not user_id:
        return "anonymous"
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in str(user_id))
    return safe or "anonymous"


def topic_prefix(prefix: str, user_id: str) -> str:
    """Compose the topic prefix including the user id (adds separator if needed)."""

    separator = "" if prefix.endswith("_") else "_"
    return f"{prefix}{separator}{clean_user_id(user_id)}_"


def list_topics(streaming_client: Any) -> tuple[str, ...]:
    """Return current Kafka topics via the admin client, or empty tuple on failure."""

    connection = getattr(streaming_client, "kafka_connection", None)
    admin = getattr(connection, "admin_client", None)
    if not admin:
        logger.warning("Kafka connection unavailable; assuming no existing topics.")
        return tuple()
    try:
        return tuple(sorted(admin.list_topics()))
    except Exception as exc:  # pragma: no cover - depends on broker
        logger.warning("Failed to list Kafka topics: %s", exc)
        return tuple()


def next_stream_id(existing_topics: Sequence[str], topic_base: str, max_streams: int) -> int:
    """Find the next available numeric suffix for a derived topic.

    Raises
    ------
    RuntimeError
        When no free suffix exists up to ``max_streams``.
    """

    used: set[int] = set()
    for topic in existing_topics:
        if not topic.startswith(topic_base):
            continue
        suffix = topic[len(topic_base) :]
        if suffix.isdigit():
            used.add(int(suffix))

    for candidate in range(max_streams):
        if candidate not in used:
            return candidate
    raise RuntimeError(f"No available stream ids for prefix '{topic_base}' (max_streams={max_streams}).")


def register_derived_resource(
    streaming_client: Any,
    dataset_id: str,
    definition: Mapping[str, Any],
    *,
    server: str | None = None,
) -> Mapping[str, Any]:
    """Register or upsert the derived Kafka resource in CKAN.

    Parameters
    ----------
    streaming_client : Any
        Streaming client exposing ``ep_client``.
    dataset_id : str
        Target dataset slug/id for the derived resource.
    definition : Mapping[str, Any]
        Normalized Kafka resource definition.
    server : str | None
        Optional ndp_ep scope override.

    Returns
    -------
    Mapping[str, Any]
        CKAN resource entry returned by registration.
    """

    entry = register_resource_fn(streaming_client.ep_client, dataset_id, definition, server=server)
    logger.info("Registered derived resource on dataset=%s as id=%s", dataset_id, entry.get("id"))
    return entry


def mark_resource_active(
    streaming_client: Any,
    resource_id: str,
    *,
    reason: str | None = None,
    server: str | None = None,
) -> Mapping[str, Any]:
    """Mark a derived resource as active and clear preservation flags when set."""

    updates: dict[str, Any] = {"inactive": False, "preserve_record": False}
    if reason:
        updates["reactivation_reason"] = reason
    # ``merge_definitions`` drops None values, so use empty string to clear.
    updates["deactivation_reason"] = ""
    entry = update_resource_fn(streaming_client.ep_client, resource_id, updates, server=server)
    logger.info("Marked resource %s as active", resource_id)
    return entry


def mark_resource_inactive(
    streaming_client: Any,
    resource_id: str,
    *,
    reason: str | None = None,
    server: str | None = None,
) -> None:
    """Mark a derived resource as inactive with an optional reason.

    Parameters
    ----------
    streaming_client : Any
        Streaming client exposing ``ep_client``.
    resource_id : str
        CKAN resource identifier to mark inactive.
    reason : str | None
        Optional reason tag stored on the resource.
    server : str | None
        Optional ndp_ep scope override.
    """

    from ...resources.update import deactivate_resource  # local import to avoid cycles

    deactivate_resource(streaming_client.ep_client, resource_id, reason=reason, server=server)
    logger.info("Marked resource %s as inactive", resource_id)


def delete_topic(
    streaming_client: Any,
    topic: str,
    *,
    wait: bool = True,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
    force: bool = True,
) -> bool:
    """Delete a Kafka topic when the admin client is available.

    Returns True only when the topic is confirmed absent after all attempts.
    """

    connection = getattr(streaming_client, "kafka_connection", None)
    admin = getattr(connection, "admin_client", None)
    if not admin:
        logger.warning("Kafka connection unavailable; cannot delete topic %s", topic)
        return False
    deleted = False
    errors: list[str] = []

    def _attempt_delete() -> bool:
        try:
            response = admin.delete_topics([topic])
            if isinstance(response, dict):
                futures = response.values()
            else:
                futures = [response]
            for fut in futures:
                # kafka-python may return Future-like or response object
                if hasattr(fut, "result"):
                    try:
                        fut.result(timeout=timeout)
                    except UnknownTopicOrPartitionError:
                        logger.info("Kafka topic %s already absent", topic)
                        return True
                    except KafkaError as exc:  # pragma: no cover - depends on broker
                        errors.append(f"delete_topics error: {exc}")
                        return False
                    except Exception as exc:
                        errors.append(f"delete_topics error: {exc}")
                        return False
                else:
                    # Best-effort: inspect topic error codes if present
                    codes = getattr(fut, "topic_error_codes", None) or getattr(fut, "topics", None)
                    if codes:
                        for _t, code in codes:
                            if code:
                                errors.append(f"delete_topics error code={code}")
                                return False
                    return True
            return True
        except UnknownTopicOrPartitionError:
            logger.info("Kafka topic %s already absent", topic)
            return True
        except KafkaError as exc:  # pragma: no cover - depends on broker
            errors.append(f"delete_topics error: {exc}")
            return False
        except Exception as exc:
            errors.append(f"delete_topics error: {exc}")
            return False

    deleted = _attempt_delete()

    if wait:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if topic not in list_topics(streaming_client):
                logger.info("Kafka topic %s confirmed deleted", topic)
                return True
            time.sleep(poll_interval)

    # If deletion failed or topic still present, optionally force compaction/purge.
    if force and topic in list_topics(streaming_client):
        logger.warning("Kafka topic %s still present; applying forceful cleanup", topic)
        try:
            # Aggressive retention to let broker purge quickly.
            resource = ConfigResource(ConfigResourceType.TOPIC, topic)
            admin.alter_configs(
                {resource: {"retention.ms": "1000", "retention.bytes": "1024", "cleanup.policy": "delete"}}
            )
        except Exception as exc:  # pragma: no cover - broker dependent
            errors.append(f"alter_configs error: {exc}")
        try:
            # Delete all records (reset to earliest).
            admin.delete_records({topic: {0: 0}})
        except Exception as exc:  # pragma: no cover - broker dependent
            errors.append(f"delete_records error: {exc}")

        # Try deletion again after retention change.
        deleted = _attempt_delete() or deleted
        if wait:
            deadline = time.time() + timeout
            while time.time() < deadline:
                if topic not in list_topics(streaming_client):
                    logger.info("Kafka topic %s confirmed deleted after force", topic)
                    return True
                time.sleep(poll_interval)

    still_there = topic in list_topics(streaming_client)
    if still_there:
        logger.error("Kafka topic %s still present after delete attempts. Errors: %s", topic, errors)
    return deleted and not still_there


def find_resources_for_topic(
    streaming_client: Any,
    topic: str,
    *,
    server: str | None = None,
) -> list[tuple[Mapping[str, Any], str | None, int]]:
    """Locate CKAN resources whose name matches the provided topic."""

    ep_client = getattr(streaming_client, "ep_client", None)
    if ep_client is None:
        return []

    matches: list[tuple[Mapping[str, Any], str | None, int]] = []
    seen_ids: set[str] = set()

    def _append_unique(dataset: Mapping[str, Any], scope: str | None, idx: int):
        resources = dataset.get("resources") or []
        rid = None
        if 0 <= idx < len(resources):
            rid = resources[idx].get("id") or resources[idx].get("name")
        rid_text = str(rid) if rid else None
        if rid_text and rid_text in seen_ids:
            return
        if rid_text:
            seen_ids.add(rid_text)
        matches.append((dataset, scope, idx))

    # Fast path: ask CKAN to search resources directly by name to avoid scanning all datasets.
    try:
        search = call_action(
            ep_client,
            "resource_search",
            {"query": f"name:{topic}", "offset": 0, "limit": 50},
            server=server,
        )
        for entry in search.get("results") or []:
            rid = entry.get("id")
            dataset_ref = entry.get("package_id") or entry.get("dataset_id") or entry.get("package_name")
            if not rid or not dataset_ref:
                continue
            try:
                dataset = call_action(ep_client, "package_show", {"id": dataset_ref}, server=server)
            except Exception:
                logger.debug("package_show failed for dataset %s during delete of topic %s", dataset_ref, topic, exc_info=True)
            else:
                resources = dataset.get("resources") or []
                idx = dataset_utils.resource_index(resources, resource_id=str(rid)) or dataset_utils.resource_index(
                    resources, name=topic
                )
                if idx is not None:
                    _append_unique(dataset, server, idx)
    except Exception:
        logger.debug("resource_search failed while deleting topic %s", topic, exc_info=True)

    # Fallback: scan datasets when resource_search is unavailable or returns nothing.
    if not matches:
        for dataset, scope, idx in dataset_utils.find_resources_by_name(ep_client, topic, preferred_scope=server):
            _append_unique(dataset, scope, idx)

    return matches


def delete_resources_for_topic(
    streaming_client: Any,
    topic: str,
    *,
    resource_ids: Iterable[str] | None = None,
    server: str | None = None,
) -> int:
    """Delete CKAN resources associated with a topic by id and name search."""

    ep_client = getattr(streaming_client, "ep_client", None)
    if ep_client is None:
        logger.warning("Streaming client missing ep_client; cannot delete resources for topic %s", topic)
        return 0

    targets: list[tuple[str, str | None]] = []
    for rid in resource_ids or ():
        if rid:
            targets.append((str(rid), server))
    matches = find_resources_for_topic(streaming_client, topic, server=server)
    for dataset, scope, idx in matches:
        resources = dataset.get("resources") or []
        if idx < len(resources):
            candidate = resources[idx].get("id")
            if candidate:
                targets.append((str(candidate), scope or server))

    seen: set[str] = set()
    deleted = 0
    for rid, rid_scope in targets:
        if rid in seen:
            continue
        seen.add(rid)
        try:
            delete_resource_fn(ep_client, rid, server=rid_scope or server)
            deleted += 1
        except CKANActionError as exc:
            logger.warning("Failed to delete CKAN resource %s for topic %s: %s", rid, topic, exc)
    return deleted


def user_topic_base(streaming_client: Any, *, prefix: str | None = None, user_id: str | None = None) -> str:
    """Return the derived-topic base prefix for a specific user."""

    resolved_prefix = prefix or getattr(streaming_client, "kafka_prefix", None) or derive_prefix(streaming_client.ep_client)
    resolved_user = clean_user_id(user_id or getattr(streaming_client, "user_id", None))
    return topic_prefix(resolved_prefix, resolved_user)


__all__ = [
    "SourceResource",
    "clean_user_id",
    "derive_max_streams",
    "derive_prefix",
    "delete_resources_for_topic",
    "delete_topic",
    "find_resources_for_topic",
    "list_topics",
    "mark_resource_active",
    "mark_resource_inactive",
    "next_stream_id",
    "register_derived_resource",
    "resolve_sources",
    "topic_prefix",
    "user_topic_base",
]
