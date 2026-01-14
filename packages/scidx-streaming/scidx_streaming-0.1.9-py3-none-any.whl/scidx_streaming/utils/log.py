"""Advanced logging helpers with multi-level SCIDX defaults."""

from __future__ import annotations

import json
import logging
import logging.config
import os
from typing import Any, Dict, Optional

TRACE_LEVEL = 5
DATAFLOW_LEVEL = 15
AUDIT_LEVEL = 25

logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.addLevelName(DATAFLOW_LEVEL, "DATAFLOW")
logging.addLevelName(AUDIT_LEVEL, "AUDIT")

_LOGGING_CONFIGURED = False
_DEFAULT_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


class SCIDXLogger(logging.Logger):
    """Custom logger that exposes trace/dataflow/audit helpers."""

    def trace(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log at TRACE (5)."""
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, msg, args, **kwargs)

    def dataflow(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log data movement events at DATAFLOW (15)."""
        if self.isEnabledFor(DATAFLOW_LEVEL):
            self._log(DATAFLOW_LEVEL, msg, args, **kwargs)

    def audit(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log audit events at AUDIT (25)."""
        if self.isEnabledFor(AUDIT_LEVEL):
            self._log(AUDIT_LEVEL, msg, args, **kwargs)


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter for centralized log shipping."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401 - doc inherited
        base = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            base["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            base["stack"] = record.stack_info
        return json.dumps(base, ensure_ascii=False)


def configure_logging(level: Optional[int | str] = None) -> None:
    """Configure logging once with console/file handlers + custom levels.

    Parameters
    ----------
    level : int | str | None
        Optional override (int or level name). Falls back to env vars
        ``SCIDX_LOG_LEVEL`` / ``SCIDX_DEBUG`` when not provided.

    Notes
    -----
    Respects ``SCIDX_LOG_JSON`` for JSON formatting and ``SCIDX_LOG_FILE`` to
    emit to a file in addition to console.
    """

    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    logging.setLoggerClass(SCIDXLogger)
    resolved_level = _coerce_level(level)
    formatter_key = "json" if os.getenv("SCIDX_LOG_JSON") else "standard"
    log_file = os.getenv("SCIDX_LOG_FILE")

    handlers = ["console"]
    handler_defs: Dict[str, Dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": resolved_level,
            "formatter": formatter_key,
        }
    }
    if log_file:
        handlers.append("file")
        handler_defs["file"] = {
            "class": "logging.FileHandler",
            "level": resolved_level,
            "formatter": formatter_key,
            "filename": log_file,
        }

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": _DEFAULT_FORMAT},
                "json": {"()": "scidx_streaming.utils.log.JsonFormatter"},
            },
            "handlers": handler_defs,
            "loggers": {
                "scidx_streaming": {
                    "handlers": handlers,
                    "level": resolved_level,
                    "propagate": False,
                }
            },
            "root": {
                "handlers": handlers,
                "level": resolved_level,
            },
        }
    )

    _LOGGING_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger ensuring logging is configured."""

    configure_logging()
    qualified = name if name.startswith("scidx_streaming") else f"scidx_streaming.{name}"
    return logging.getLogger(qualified)


def _coerce_level(level: Optional[int | str]) -> int:
    """Normalize a level input (int/name/env) to a logging level int."""
    if isinstance(level, int):
        return level
    raw = level or os.getenv("SCIDX_LOG_LEVEL") or ("DEBUG" if os.getenv("SCIDX_DEBUG") else "INFO")
    if isinstance(raw, str):
        norm = raw.upper()
        return getattr(logging, norm, logging.INFO)
    return logging.INFO
