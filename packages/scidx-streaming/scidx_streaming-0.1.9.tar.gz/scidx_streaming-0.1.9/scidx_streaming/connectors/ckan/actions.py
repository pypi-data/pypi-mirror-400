"""CKAN action invocation helpers."""

from __future__ import annotations

import logging
from typing import Any, Mapping
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class CKANActionError(RuntimeError):
    """Raised when CKAN action calls fail."""


def call_action(ep_client: Any, action: str, payload: Mapping[str, Any], *, server: str | None = None) -> Any:
    """Invoke a CKAN action using the ``ndp_ep`` client session.

    Parameters
    ----------
    ep_client : Any
        ndp_ep client exposing ``base_url`` and ``session``.
    action : str
        CKAN action name (e.g., ``package_show``).
    payload : Mapping[str, Any]
        JSON-serializable payload to send.
    server : str | None
        Optional ndp_ep scope override.

    Returns
    -------
    Any
        CKAN action result payload (dict-like; specific to the invoked action).

    Raises
    ------
    CKANActionError
        When the session is invalid, response is malformed, or CKAN reports failure.
    """

    base_url = getattr(ep_client, "base_url", None)
    session = getattr(ep_client, "session", None)
    token = getattr(ep_client, "token", None)
    if not base_url or not session:
        raise CKANActionError("CKAN session unavailable; ensure ndp_ep exposes base_url/session.")

    request = getattr(session, "post", None) or getattr(session, "request", None)
    if not callable(request):
        raise CKANActionError("CKAN session must expose 'post' or 'request'.")

    endpoint = urljoin(str(base_url).rstrip("/") + "/", f"api/3/action/{action}")
    headers = {"Authorization": token} if token else None
    logger.debug("Calling CKAN action '%s' at %s", action, endpoint)

    params = {"server": server} if server else None

    try:
        response = request(endpoint, json=payload, headers=headers, params=params, timeout=30)
    except Exception as exc:  # pragma: no cover - network failure
        raise CKANActionError(f"CKAN action '{action}' failed: {exc}") from exc

    if not hasattr(response, "json"):
        raise CKANActionError(f"CKAN action '{action}' returned an invalid response.")

    try:
        data = response.json()
    except Exception as exc:  # pragma: no cover - invalid JSON
        raise CKANActionError(f"CKAN action '{action}' returned non-JSON content.") from exc

    success = data.get("success", getattr(response, "ok", False))
    if not success:
        error = data.get("error") or data
        raise CKANActionError(f"CKAN action '{action}' failed: {error}")

    return data.get("result", data)


__all__ = ["CKANActionError", "call_action"]
