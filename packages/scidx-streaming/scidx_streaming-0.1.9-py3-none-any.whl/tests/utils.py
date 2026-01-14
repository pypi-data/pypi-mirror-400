"""Common helpers shared across integration tests."""

from __future__ import annotations

import io
from pathlib import Path
import warnings

try:  # pragma: no cover - we handle missing coverage gracefully
    import coverage  # type: ignore
    from coverage.exceptions import CoverageException  # type: ignore
except Exception:  # pragma: no cover
    coverage = None  # type: ignore
    CoverageException = RuntimeError

try:  # pragma: no cover - optional import
    from coverage.control import CoverageWarning  # type: ignore
except Exception:  # pragma: no cover
    CoverageWarning = None  # type: ignore


class CoverageMonitor:
    """Simple wrapper that prints coverage snapshots during long tests."""

    def __init__(self, *, source_dir: Path | str | None = None) -> None:
        self._cov = None
        self._running = False
        if source_dir is None:
            source_dir = Path(__file__).resolve().parents[1] / "scidx_streaming"
        self._source_dir = Path(source_dir)
        self._source_label = self._source_dir.name
        if coverage is None:
            print("[coverage] Install 'coverage' to enable live coverage snapshots during the test.")
            return
        self._cov = coverage.Coverage(data_file=None, source=[str(self._source_dir)])
        self._start()

    def snapshot(self, label: str) -> None:
        if not self._cov:
            return
        self._stop()
        percent = self._current_percent()
        self._start()
        print(f"[coverage] {label}: {percent:.2f}% of {self._source_label} lines covered")

    def finalize(self) -> None:
        if not self._cov:
            return
        self._stop()
        percent = self._current_percent()
        print(f"[coverage] Final {self._source_label} coverage: {percent:.2f}%")

    def _current_percent(self) -> float:
        assert self._cov is not None
        data = self._cov.get_data()
        if not data.measured_files():
            return 0.0
        buffer = io.StringIO()
        try:
            with warnings.catch_warnings():
                if CoverageWarning is not None:  # pragma: no branch
                    warnings.filterwarnings("ignore", category=CoverageWarning)
                percent = self._cov.report(show_missing=False, file=buffer)
        except CoverageException:
            return 0.0
        return float(percent)

    def _start(self) -> None:
        if self._cov and not self._running:
            self._cov.start()
            self._running = True

    def _stop(self) -> None:
        if self._cov and self._running:
            self._cov.stop()
            self._running = False


__all__ = ["CoverageMonitor"]
