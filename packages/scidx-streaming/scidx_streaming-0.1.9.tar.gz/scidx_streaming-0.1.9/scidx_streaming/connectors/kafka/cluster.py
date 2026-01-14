"""Kafka cluster metadata utilities."""

from __future__ import annotations

from dataclasses import dataclass

from kafka.errors import KafkaError

from .connection import KafkaConnection


@dataclass(slots=True)
class KafkaClusterInfo:
    """High-level cluster metadata used for logging/diagnostics."""

    topic_count: int
    topics: tuple[str, ...]
    broker_count: int
    controller_id: int | None = None
    cluster_id: str | None = None


def describe_cluster(connection: KafkaConnection) -> KafkaClusterInfo:
    """Return summary metadata for the connected cluster.

    Parameters
    ----------
    connection : KafkaConnection
        Connection containing the admin client.

    Returns
    -------
    KafkaClusterInfo
        Topic counts, broker counts, controller/cluster ids, and topic names.

    Raises
    ------
    RuntimeError
        If the admin client is unavailable or description fails.
    """

    if not connection.admin_client:
        raise RuntimeError("Kafka admin client is not initialized.")

    try:
        cluster = connection.admin_client.describe_cluster()
    except KafkaError as exc:  # pragma: no cover - surfaced to caller
        raise RuntimeError("Unable to describe Kafka cluster.") from exc

    try:
        topics = tuple(sorted(connection.admin_client.list_topics()))
    except KafkaError:
        topics = tuple()

    brokers = cluster.get("brokers") or ()
    return KafkaClusterInfo(
        topic_count=len(topics),
        topics=topics,
        broker_count=len(brokers),
        controller_id=cluster.get("controller"),
        cluster_id=cluster.get("cluster_id"),
    )
