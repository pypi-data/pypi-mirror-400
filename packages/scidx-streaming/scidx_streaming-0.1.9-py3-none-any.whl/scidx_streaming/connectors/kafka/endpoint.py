"""Kafka endpoint resolution utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class KafkaEndpoint:
    """Resolved Kafka endpoint (host/port pair)."""

    host: str
    port: int

    @property
    def bootstrap(self) -> str:
        return f"{self.host}:{self.port}"


def resolve_connection(
    ep_client: Any,
    *,
    host: str | None = None,
    port: int | None = None,
) -> KafkaEndpoint:
    """Resolve Kafka endpoint from overrides or ndp_ep configuration.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client exposing ``get_kafka_details`` when available.
    host, port : str | int | None
        Optional explicit overrides.

    Returns
    -------
    KafkaEndpoint
        Resolved host/port pair with ``bootstrap`` property.

    Raises
    ------
    RuntimeError
        If host/port cannot be determined from overrides or ndp_ep config.
    """

    resolved_host = host
    resolved_port = port

    if resolved_host is None or resolved_port is None:
        details = {}
        getter = getattr(ep_client, "get_kafka_details", None)
        if callable(getter):
            try:
                details = getter()
            except Exception:  # pragma: no cover - blueprint placeholder
                details = {}
        resolved_host = resolved_host or details.get("kafka_host")
        resolved_port = resolved_port or details.get("kafka_port")

    if resolved_host is None or resolved_port is None:
        raise RuntimeError("Kafka endpoint undefined; pass host/port or configure ndp_ep Kafka details.")

    return KafkaEndpoint(host=str(resolved_host), port=int(resolved_port))
