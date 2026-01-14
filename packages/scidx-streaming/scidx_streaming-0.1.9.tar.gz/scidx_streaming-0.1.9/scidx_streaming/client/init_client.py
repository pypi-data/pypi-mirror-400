"""Entry-point client blueprint for the streaming library."""

from __future__ import annotations

import base64
import json
import logging
import os
from typing import Any

from absl import logging as absl_logging

from ndp_ep import APIClient

from ..connectors import ckan as ckan_connector, kafka as kafka_connector
from ..streams.creation import base as creation_base

# Silence noisy gRPC/absl logs upfront; mirrored from the original prototype.
os.environ["GRPC_PYTHON_LOG_SEVERITY"] = "FATAL"
os.environ["GRPC_PYTHON_LOG_LEVEL"] = "ERROR"
os.environ.setdefault("GRPC_VERBOSITY", "NONE")
os.environ.setdefault("GRPC_TRACE", "")
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("ABSL_LOG_LEVEL", "3")
os.environ.setdefault("ABSL_LOGLEVEL", "3")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

absl_logging.set_verbosity(absl_logging.ERROR)
absl_logging.set_stderrthreshold("fatal")

logger = logging.getLogger(__name__)


def _decode_user_id(token: str | None) -> str | None:
    """Best-effort JWT payload decoder to expose the authenticated user.

    Parameters
    ----------
    token : str | None
        JWT access token (typically from ndp_ep).

    Returns
    -------
    str | None
        User identifier (`sub`, `preferred_username`, or `email`) when
        decodable; otherwise ``None``.
    """

    if not token:
        return None
    parts = token.split(".")
    if len(parts) < 2:
        return None
    payload = parts[1]
    padding = "=" * (-len(payload) % 4)
    try:
        decoded = base64.urlsafe_b64decode(payload + padding)
        data = json.loads(decoded)
    except Exception:  # pragma: no cover - defensive
        return None
    return data.get("sub") or data.get("preferred_username") or data.get("email")


class StreamingClient:
    """Facade around ``ndp_ep.APIClient`` that adds CKAN/Kafka streaming helpers.

    The client keeps the authenticated ndp_ep API client, validates CKAN
    connectivity, discovers/overrides Kafka endpoints, and exposes convenience
    methods for resource lifecycle, discovery, filter compilation, stream
    creation, and consumption.
    """

    ep_client: APIClient
    kafka_host: str | None
    kafka_port: int | None
    kafka_bootstrap: str | None
    kafka_connection: Any
    kafka_cluster_info: Any | None
    ckan_status: dict[str, Any] | None

    def __init__(self, ep_client: APIClient, *, kafka_host: str | None = None, kafka_port: int | None = None) -> None:
        if not isinstance(ep_client, APIClient):
            raise ValueError("`ep_client` must be an instance of ndp_ep.APIClient.")

        self.ep_client = ep_client
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.kafka_bootstrap = None
        self.kafka_connection = None
        self.kafka_cluster_info = None
        self.ckan_status = None
        self.user_id = _decode_user_id(getattr(ep_client, "token", None))
        self.kafka_prefix = creation_base.derive_prefix(self.ep_client, default="derived_stream_")
        self.max_streams = creation_base.derive_max_streams(self.ep_client, default=10)
        self._derived_producers: dict[str, Any] = {}

        # Validate CKAN connectivity and capture basic metadata.
        try:
            self.ckan_status = ckan_connector.check_connection(self.ep_client)
            base_url = self.ckan_status.get("base_url")
            has_session = "yes" if self.ckan_status.get("has_session") else "no"
            logger.info("CKAN connection ready base_url=%s session=%s", base_url, has_session)
        except Exception as exc:  # pragma: no cover - blueprint logging only
            logger.warning("CKAN connection check failed: %s", exc)
            self.ckan_status = None

        # Resolve Kafka endpoint and establish a connector placeholder.
        try:
            user_overrode_kafka = kafka_host is not None or kafka_port is not None
            endpoint = kafka_connector.resolve_connection(
                self.ep_client,
                host=self.kafka_host,
                port=self.kafka_port,
            )
            self.kafka_host = endpoint.host
            self.kafka_port = endpoint.port
            self.kafka_bootstrap = endpoint.bootstrap
            self.kafka_connection = kafka_connector.connect(endpoint)
            if user_overrode_kafka:
                logger.info("Kafka endpoint override provided host=%s port=%s", endpoint.host, endpoint.port)
            else:
                logger.info("Kafka endpoint resolved from ndp_ep host=%s port=%s", endpoint.host, endpoint.port)
            try:
                self.kafka_cluster_info = kafka_connector.describe_cluster(self.kafka_connection)
                info = self.kafka_cluster_info
                logger.info(
                    "Kafka connected bootstrap=%s topics=%d brokers=%d",
                    endpoint.bootstrap,
                    info.topic_count,
                    info.broker_count,
                )
            except Exception as cluster_exc:  # pragma: no cover - blueprint logging only
                logger.warning("Kafka metadata probe failed: %s", cluster_exc)
        except Exception as exc:  # pragma: no cover - blueprint logging only
            logger.warning("Kafka connection setup failed: %s", exc)
            kafka_connector.disconnect(self.kafka_connection)
            self.kafka_connection = None
