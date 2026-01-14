"""Kafka admin-client helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Mapping

from kafka import KafkaAdminClient

from .endpoint import KafkaEndpoint

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class KafkaConnection:
    """Wrapper holding the admin client for metadata/lifecycle operations."""

    endpoint: KafkaEndpoint
    admin_client: KafkaAdminClient | None = None


def connect(
    endpoint: KafkaEndpoint,
    *,
    client_id: str = "scidx-streaming",
    security_config: Mapping[str, object] | None = None,
    request_timeout_ms: int = 5000,
) -> KafkaConnection:
    """Instantiate a Kafka admin client used for lifecycle operations.

    Parameters
    ----------
    endpoint : KafkaEndpoint
        Resolved Kafka host/port.
    client_id : str
        Kafka client identifier.
    security_config : Mapping[str, object] | None
        Optional security/auth config to merge into the admin client.
    request_timeout_ms : int
        Admin request timeout in milliseconds.

    Returns
    -------
    KafkaConnection
        Wrapper holding the endpoint and admin client.

    Raises
    ------
    RuntimeError
        If the Kafka admin client cannot be constructed.
    """

    config: dict[str, object] = {
        "bootstrap_servers": endpoint.bootstrap,
        "client_id": client_id,
        "request_timeout_ms": request_timeout_ms,
    }
    if security_config:
        config.update(security_config)

    logger.debug("Connecting to Kafka bootstrap=%s", endpoint.bootstrap)
    admin = KafkaAdminClient(**config)
    return KafkaConnection(endpoint=endpoint, admin_client=admin)


def disconnect(connection: KafkaConnection | None) -> None:
    """Close underlying Kafka clients (best effort)."""

    if not connection:
        return
    admin = connection.admin_client
    if admin is not None:
        try:
            admin.close()
        except Exception:  # pragma: no cover - best effort
            logger.debug("Kafka admin client close failed", exc_info=True)
