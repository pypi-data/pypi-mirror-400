"""Kafka source consumption handler for derived stream fan-in."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context

logger = logging.getLogger(__name__)


def _is_auth_error(exc: Exception) -> bool:
    """Detect whether an exception message looks like an auth failure."""
    message = str(exc).lower()
    auth_markers = (
        "sasl",
        "auth",
        "unauthorized",
        "security",
        "denied",
        "permission",
    )
    return any(token in message for token in auth_markers)


def _build_attempts(
    *,
    username: str | None,
    password: str | None,
    declared_protocol: str | None,
    declared_mechanism: str | None,
) -> list[dict[str, Any]]:
    """Return ordered auth attempts (prefer secure paths first when creds available)."""

    attempts: list[dict[str, Any]] = []

    # If the resource hints at security and creds are available, honor that first.
    if (declared_protocol or declared_mechanism) and username and password:
        attempts.append(
            {
                "label": "declared_security",
                "kwargs": {
                    "security_protocol": declared_protocol,
                    "sasl_mechanism": declared_mechanism,
                    "sasl_plain_username": username,
                    "sasl_plain_password": password,
                    "ssl_context": create_ssl_context() if (declared_protocol or "").upper() == "SASL_SSL" else None,
                },
            }
        )

    # Common secure defaults when creds are provided
    if username and password:
        attempts.extend(
            [
                {
                    "label": "sasl_ssl_scram",
                    "kwargs": {
                        "security_protocol": "SASL_SSL",
                        "sasl_mechanism": declared_mechanism or "SCRAM-SHA-512",
                        "sasl_plain_username": username,
                        "sasl_plain_password": password,
                        "ssl_context": create_ssl_context(),
                    },
                },
                {
                    "label": "sasl_ssl_plain",
                    "kwargs": {
                        "security_protocol": "SASL_SSL",
                        "sasl_mechanism": declared_mechanism or "PLAIN",
                        "sasl_plain_username": username,
                        "sasl_plain_password": password,
                        "ssl_context": create_ssl_context(),
                    },
                },
                {
                    "label": "sasl_plaintext_scram",
                    "kwargs": {
                        "security_protocol": "SASL_PLAINTEXT",
                        "sasl_mechanism": declared_mechanism or "SCRAM-SHA-512",
                        "sasl_plain_username": username,
                        "sasl_plain_password": password,
                    },
                },
                {
                    "label": "sasl_plaintext_plain",
                    "kwargs": {
                        "security_protocol": "SASL_PLAINTEXT",
                        "sasl_mechanism": declared_mechanism or "PLAIN",
                        "sasl_plain_username": username,
                        "sasl_plain_password": password,
                    },
                },
            ]
        )

    # Always try plain unauthenticated at the end as a last resort.
    attempts.append({"label": "plain", "kwargs": {}})
    return attempts


async def consume_kafka_source(
    *,
    source: Any,
    stop_event: asyncio.Event,
    username: str | None,
    password: str | None,
    forward_message,
    mark_inactive,
    auto_offset_reset: str | None = None,
) -> None:
    """Consume a Kafka source resource and forward raw messages.

    Parameters
    ----------
    source : Any
        SourceResource containing Kafka host/port/topic and metadata.
    stop_event : asyncio.Event
        Event used to coordinate shutdown.
    username, password : str | None
        Optional credentials for SASL attempts.
    forward_message : Callable
        Coroutine to forward raw message bytes to the derived producer.
    mark_inactive : Callable
        Coroutine to mark the derived resource inactive on failure.
    auto_offset_reset : str | None
        Optional override for the consumer offset reset behaviour.
    """

    conf = source.definition or {}
    host = conf.get("host") or conf.get("kafka_host")
    port = conf.get("port") or conf.get("kafka_port")
    topic = conf.get("topic")
    if not (host and port and topic):
        logger.error("Kafka source missing host/port/topic for resource %s", source.id)
        return

    consumer_kwargs: dict[str, Any] = {
        "bootstrap_servers": f"{host}:{port}",
        "auto_offset_reset": auto_offset_reset or conf.get("auto_offset_reset", "earliest"),
        "enable_auto_commit": False,
        "group_id": f"derived-{topic}-{source.id}",
    }

    declared_protocol = conf.get("security_protocol") or conf.get("kafka_security_protocol")
    declared_mechanism = conf.get("sasl_mechanism") or conf.get("kafka_sasl_mechanism")

    attempts = _build_attempts(
        username=username,
        password=password,
        declared_protocol=declared_protocol,
        declared_mechanism=declared_mechanism,
    )

    consumer = None
    last_error = None
    attempt_results: list[tuple[str, str]] = []

    for attempt in attempts:
        attempt_kwargs = dict(consumer_kwargs)
        attempt_kwargs.update({k: v for k, v in attempt["kwargs"].items() if v is not None})
        logger.info(
            "Kafka source %s connection attempt: %s (protocol=%s mechanism=%s)",
            source.id,
            attempt["label"],
            attempt_kwargs.get("security_protocol"),
            attempt_kwargs.get("sasl_mechanism"),
        )
        consumer = AIOKafkaConsumer(topic, **attempt_kwargs)
        try:
            await consumer.start()
            logger.info("Kafka source %s attempt %s succeeded.", source.id, attempt["label"])
            attempt_results.append((attempt["label"], "success"))
            break
        except Exception as exc:
            last_error = exc
            logger.warning("Kafka source %s attempt %s failed: %s", source.id, attempt["label"], exc)
            try:
                await consumer.stop()
            except Exception:
                pass
            consumer = None
            attempt_results.append((attempt["label"], f"failed:{exc}"))

    if consumer is None:
        if username and password and _is_auth_error(last_error or Exception()):
            reason = "auth_failed"
        elif _is_auth_error(last_error or Exception()):
            reason = "auth_required"
        else:
            reason = "connection_failed"
        logger.error(
            "All connection attempts failed for source %s: %s (reason=%s) attempts=%s",
            source.id,
            last_error,
            reason,
            attempt_results,
        )
        await mark_inactive(reason=reason)
        return

    try:
        while not stop_event.is_set():
            try:
                message = await asyncio.wait_for(consumer.getone(), timeout=1.0)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                logger.error("Consumer error for source %s: %s", source.id, exc)
                break

            await forward_message(message.value)
    finally:
        try:
            await consumer.stop()
        except Exception:
            logger.debug("Consumer stop failed for source %s", source.id, exc_info=True)
