"""Kafka resource helpers."""

from __future__ import annotations

from typing import Any, Mapping

from .. import common

RESOURCE_TYPE = "kafka"


def normalize(payload: Mapping[str, Any], *, resource_type: str = RESOURCE_TYPE) -> dict[str, Any]:
    """Validate the Kafka-specific fields.

    Parameters
    ----------
    payload : Mapping[str, Any]
        Raw resource definition containing host/port/topic (+ optional auth).
    resource_type : str
        Resource type label (defaults to ``"kafka"``).

    Returns
    -------
    dict[str, Any]
        Normalized Kafka definition with required keys coerced to text/ints.

    Raises
    ------
    ValueError
        If required fields are missing or invalid.
    """

    normalized = {
        "host": common.require_text(payload.get("host"), "host"),
        "topic": common.require_text(payload.get("topic"), "topic"),
        "port": common.normalize_port(payload.get("port")),
    }
    for key in ("security_protocol", "sasl_mechanism", "sasl_username", "sasl_password", "secret_reference"):
        if key in payload and payload[key] is not None:
            normalized[key] = payload[key]
    if "protected" in payload:
        normalized["protected"] = bool(payload["protected"])
    return normalized


def resource_extras(definition: Mapping[str, Any]) -> dict[str, Any]:
    """Provide CKAN resource extras for Kafka methods.

    Returns
    -------
    dict[str, Any]
        Extras merged into CKAN resource payload (host/port/topic/auth flags,
        `protected` flag inferred when creds are present).
    """

    extras: dict[str, Any] = {}
    host = definition.get("host")
    port = definition.get("port")
    topic = definition.get("topic")
    if host:
        extras["host"] = host
        extras["kafka_host"] = host
    if port is not None:
        extras["port"] = port
        extras["kafka_port"] = port
    if topic:
        extras["topic"] = topic
        extras["kafka_topic"] = topic

    for key in ("security_protocol", "sasl_mechanism", "sasl_username", "sasl_password", "secret_reference"):
        if key in definition and definition[key] is not None:
            extras[key] = definition[key]

    protected = definition.get("protected")
    if protected is None:
        protected = bool(
            definition.get("sasl_mechanism")
            or definition.get("sasl_username")
            or definition.get("sasl_password")
            or definition.get("secret_reference")
        )
    extras["protected"] = bool(protected)
    return extras


def build_url(definition: Mapping[str, Any]) -> str | None:
    """Build a kafka:// URL when host/port/topic are available."""
    host = definition.get("host")
    port = definition.get("port")
    topic = definition.get("topic")
    if host and port and topic:
        return f"kafka://{host}:{port}/{topic}"
    return None


__all__ = ["RESOURCE_TYPE", "build_url", "normalize", "resource_extras"]
