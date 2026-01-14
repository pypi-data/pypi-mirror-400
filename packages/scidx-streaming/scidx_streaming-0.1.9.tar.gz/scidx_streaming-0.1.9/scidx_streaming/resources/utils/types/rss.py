"""RSS/Atom resource helpers."""

from __future__ import annotations

from typing import Mapping

from .. import common

RESOURCE_TYPE = "rss"


def normalize(payload: Mapping[str, object], *, resource_type: str = RESOURCE_TYPE) -> dict[str, object]:
    """Validate RSS/Atom feed definitions.

    Parameters
    ----------
    payload : Mapping[str, object]
        Raw definition containing ``url`` and optional refresh hints.
    resource_type : str
        Resource type label (defaults to ``rss``).

    Returns
    -------
    dict[str, object]
        Normalized RSS definition with required url and optional refresh interval.

    Raises
    ------
    ValueError
        If required fields are missing.
    """

    normalized: dict[str, object] = {"url": common.require_text(payload.get("url"), "url")}
    if "refresh_interval" in payload and payload["refresh_interval"] is not None:
        normalized["refresh_interval"] = payload["refresh_interval"]
    return normalized


def resource_extras(_: Mapping[str, object]) -> dict[str, object]:
    """Return CKAN extras for RSS resources (none required)."""
    return {}


def build_url(definition: Mapping[str, object]) -> str | None:
    """Return the RSS/Atom URL if present, otherwise None."""
    url = common.clean_text(definition.get("url"))
    return url or None


__all__ = ["RESOURCE_TYPE", "build_url", "normalize", "resource_extras"]
