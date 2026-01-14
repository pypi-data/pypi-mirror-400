"""Lightweight logging helper for the test suite.

Usage:
    from tests.testlog import test_log
    test_log.section("Register dataset flow")
    test_log.step("Creating fake settings")

Configure verbosity via the SCIDX_TEST_LOG_LEVEL env var:
    0 -> silent (default)
    1 -> section-level messages
    2 -> include detailed steps
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass


def _resolve_level() -> int:
    raw = os.getenv("SCIDX_TEST_LOG_LEVEL", "0").strip()
    try:
        return int(raw)
    except ValueError:
        print(f"[TEST][WARN] Invalid SCIDX_TEST_LOG_LEVEL={raw!r}; defaulting to 0", file=sys.stderr)
        return 0


@dataclass(slots=True)
class TestLogger:
    level: int = _resolve_level()
    prefix: str = os.getenv("SCIDX_TEST_LOG_PREFIX", "[TEST]")

    def section(self, message: str) -> None:
        """High-level milestone (shown when level >= 1)."""

        if self.level >= 1:
            print(f"{self.prefix} === {message} ===")

    def step(self, message: str) -> None:
        """Detailed step logging (shown when level >= 2)."""

        if self.level >= 2:
            print(f"{self.prefix} ... {message}")

    def call(self, func: str, **kwargs) -> None:
        """Log a function invocation with keyword arguments."""

        if self.level >= 2:
            arg_str = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
            print(f"{self.prefix} >>> {func}({arg_str})")

    def result(self, func: str, value) -> None:
        """Log the result of a function invocation."""

        if self.level >= 2:
            print(f"{self.prefix} <<< {func} -> {value!r}")


test_log = TestLogger()
