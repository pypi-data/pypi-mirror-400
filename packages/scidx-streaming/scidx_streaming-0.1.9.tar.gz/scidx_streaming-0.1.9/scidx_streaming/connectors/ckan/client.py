"""Utilities that inspect the ndp_ep client for CKAN support."""

from __future__ import annotations

from typing import Any, Dict


def check_connection(ep_client: Any) -> Dict[str, Any]:
    """Verify that the provided ndp_ep client has the fields needed for CKAN calls.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client expected to expose ``base_url``, ``token``, and ``session``.

    Returns
    -------
    Dict[str, Any]
        Minimal CKAN connection metadata (``base_url``, ``has_session``).

    Raises
    ------
    RuntimeError
        If required fields are missing.
    """

    base_url = getattr(ep_client, "base_url", None)
    token = getattr(ep_client, "token", None)
    session = getattr(ep_client, "session", None)
    missing = [name for name, value in (("base_url", base_url), ("token", token), ("session", session)) if not value]
    if missing:
        raise RuntimeError(f"ndp_ep client missing required CKAN fields: {', '.join(missing)}")

    return {
        "base_url": str(base_url),
        "has_session": session is not None,
    }


def fetch_configuration(ep_client: Any) -> Dict[str, Any]:
    """Return CKAN configuration metadata if the client exposes it.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client possibly exposing ``get_configuration``.

    Returns
    -------
    Dict[str, Any]
        Configuration mapping or a minimal dict with ``base_url`` for reference.
    """

    fetcher = getattr(ep_client, "get_configuration", None)
    if callable(fetcher):
        return fetcher()  # pragma: no cover - depends on real ndp_ep
    return {"base_url": getattr(ep_client, "base_url", None)}


__all__ = ["check_connection", "fetch_configuration"]
