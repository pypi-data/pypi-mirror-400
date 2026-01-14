"""API stream resource helpers (polling HTTP endpoints)."""

from __future__ import annotations

from typing import Any, Mapping

from .. import common

RESOURCE_TYPE = "api_stream"


def normalize(payload: Mapping[str, Any], *, resource_type: str = RESOURCE_TYPE) -> dict[str, Any]:
    """Validate API stream definitions.

    Parameters
    ----------
    payload : Mapping[str, Any]
        Raw definition with url and optional HTTP/polling settings.
    resource_type : str
        Resource type label (defaults to ``api_stream``).

    Returns
    -------
    dict[str, Any]
        Normalized API stream definition.

    Raises
    ------
    ValueError
        If required fields are missing.
    """

    normalized: dict[str, Any] = {
        "url": common.require_text(payload.get("url"), "url"),
    }
    if "http_method" in payload:
        normalized["http_method"] = common.clean_text(payload.get("http_method") or "GET").upper() or "GET"
    if "poll_interval" in payload and payload["poll_interval"] is not None:
        normalized["poll_interval"] = payload["poll_interval"]
    for key in ("headers", "params", "body"):
        if key in payload and payload[key] is not None:
            normalized[key] = payload[key]
    return normalized


def resource_extras(_: Mapping[str, Any]) -> dict[str, Any]:
    """Return CKAN extras for API stream resources (none required)."""
    return {}


def build_url(definition: Mapping[str, Any]) -> str | None:
    """Return the API URL if present, otherwise None."""
    url = common.clean_text(definition.get("url"))
    return url or None


__all__ = ["RESOURCE_TYPE", "build_url", "normalize", "resource_extras"]
