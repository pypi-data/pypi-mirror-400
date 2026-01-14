"""Time helpers used throughout the streaming lifecycle."""

from __future__ import annotations

from datetime import datetime, timezone


def now_utc() -> datetime:
    """Return timezone-aware UTC now."""

    return datetime.now(timezone.utc)


def isoformat(ts: datetime | None = None) -> str:
    """Return ISO-8601 string for the provided timestamp (UTC)."""

    return (ts or now_utc()).isoformat()
