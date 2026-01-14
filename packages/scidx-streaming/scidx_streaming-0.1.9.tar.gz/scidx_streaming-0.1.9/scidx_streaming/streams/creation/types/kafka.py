"""Kafka-derived stream creation helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from .. import base
from ....connectors.kafka import endpoint as kafka_endpoint

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KafkaDerivedResult:
    """Structured response from creating a derived Kafka stream."""

    topic: str
    resource: Mapping[str, Any] | None
    dataset_id: str | None
    sources: tuple[base.SourceResource, ...]
    filters: tuple[Any, ...]
    created_topic: bool
    scope: str | None


def create_kafka_stream(
    streaming_client: Any,
    *,
    sources: Sequence[base.SourceResource],
    filters: Sequence[Any] | None = None,
    server: str | None = None,
    description: str | None = None,
) -> KafkaDerivedResult:
    """Materialize a derived Kafka topic and register it in CKAN.

    Parameters
    ----------
    streaming_client : Any
        Streaming client with Kafka/CKAN connectivity.
    sources : Sequence[SourceResource]
        Normalized source resources.
    filters : Sequence[Any] | None
        Optional filter payloads.
    server : str | None
        Scope override for CKAN registration.
    description : str | None
        Description stored on the derived resource.
    Notes
    -----
    Topic prefix, max streams, partition count, and replication factor use
    library defaults (prefix/max resolved from ndp_ep/env; partitions and
    replication factor default to 1).

    Returns
    -------
    KafkaDerivedResult
        Topic name, CKAN entry, dataset id, sources, filters, and created flag.

    Raises
    ------
    RuntimeError
        If Kafka admin is unavailable or topic creation fails.
    """

    endpoint = kafka_endpoint.resolve_connection(
        streaming_client.ep_client,
        host=getattr(streaming_client, "kafka_host", None),
        port=getattr(streaming_client, "kafka_port", None),
    )

    prefix = base.derive_prefix(streaming_client.ep_client, override=None)
    limit = base.derive_max_streams(streaming_client.ep_client, override=None)
    user_id = base.clean_user_id(getattr(streaming_client, "user_id", None))
    topic_base = base.topic_prefix(prefix, user_id)
    existing_topics = base.list_topics(streaming_client)
    stream_id = base.next_stream_id(existing_topics, topic_base, limit)
    topic = f"{topic_base}{stream_id}"

    created_topic = _ensure_topic(streaming_client, topic, partitions=1, replication_factor=1)
    logger.info("Derived Kafka topic ready: %s (created=%s)", topic, created_topic)

    filter_payload = tuple(filters or ())
    resource_scope = sources[0].scope or server
    definition = _build_kafka_definition(
        topic=topic,
        endpoint=endpoint,
        sources=sources,
        filters=filter_payload,
        description=description,
    )

    target_dataset = sources[0].dataset_id or sources[0].dataset_name
    resource_entry = base.register_derived_resource(
        streaming_client,
        target_dataset,
        definition,
        server=resource_scope,
    )

    return KafkaDerivedResult(
        topic=topic,
        resource=resource_entry,
        dataset_id=target_dataset,
        sources=tuple(sources),
        filters=filter_payload,
        created_topic=created_topic,
        scope=resource_scope,
    )


def _ensure_topic(streaming_client: Any, topic: str, *, partitions: int, replication_factor: int) -> bool:
    """Create the Kafka topic if it doesn't exist. Returns True on creation."""

    connection = getattr(streaming_client, "kafka_connection", None)
    admin = getattr(connection, "admin_client", None)
    if not admin:
        raise RuntimeError("Kafka connection is unavailable; cannot create derived topic.")

    if topic in base.list_topics(streaming_client):
        return False

    new_topic = NewTopic(name=topic, num_partitions=partitions, replication_factor=replication_factor)
    try:
        admin.create_topics([new_topic], validate_only=False)
    except TopicAlreadyExistsError:
        return False
    return True


def _build_kafka_definition(
    *,
    topic: str,
    endpoint: Any,
    sources: Sequence[base.SourceResource],
    filters: Sequence[Any],
    description: str | None,
) -> Mapping[str, Any]:
    """Construct the Kafka resource payload stored in CKAN."""

    source_meta = [
        {
            "resource_id": source.id,
            "dataset_id": source.dataset_id,
            "dataset_name": source.dataset_name,
            "type": (source.definition.get("type") or source.raw.get("format") or "").lower(),
            "name": source.definition.get("name") or source.raw.get("name"),
        }
        for source in sources
    ]

    filter_summary = [f for f in filters] if filters else []
    filter_text = ", ".join(str(item) for item in filter_summary) if filter_summary else "none"
    source_ids = ", ".join(source.id for source in sources)
    desc = description or f"Derived Kafka stream from IDs [{source_ids}]; filters: {filter_text}."

    return {
        "type": "kafka",
        "name": topic,
        "description": desc,
        "host": endpoint.host,
        "port": endpoint.port,
        "topic": topic,
        "sources": source_meta,
        "filters": filter_summary,
    }


__all__ = ["KafkaDerivedResult", "create_kafka_stream"]
