"""Static file resource helpers (CSV, TXT, JSON, NetCDF)."""

from __future__ import annotations

from typing import Mapping

from .. import common

STATIC_FILE_TYPES = ("csv", "txt", "json", "netcdf")


def normalize(payload: Mapping[str, object], *, resource_type: str) -> dict[str, object]:
    """Validate URL-backed static file definitions.

    Parameters
    ----------
    payload : Mapping[str, object]
        Raw definition containing ``url`` and optional file hints.
    resource_type : str
        One of ``csv``, ``txt``, ``json``, ``netcdf``.

    Returns
    -------
    dict[str, object]
        Normalized static-file definition with required url and optional hints.

    Raises
    ------
    ValueError
        If required fields are missing.
    """

    normalized: dict[str, object] = {
        "url": common.require_text(payload.get("url"), "url"),
    }
    for key in ("compression", "checksum", "encoding", "delimiter", "schema"):
        if key in payload and payload[key] is not None:
            normalized[key] = payload[key]
    return normalized


def resource_extras(_: Mapping[str, object]) -> dict[str, object]:
    """Return CKAN extras for static file resources (none required)."""
    return {}


def build_url(definition: Mapping[str, object]) -> str | None:
    """Return the resource URL if present, otherwise None."""
    url = common.clean_text(definition.get("url"))
    return url or None


__all__ = ["STATIC_FILE_TYPES", "build_url", "normalize", "resource_extras"]
