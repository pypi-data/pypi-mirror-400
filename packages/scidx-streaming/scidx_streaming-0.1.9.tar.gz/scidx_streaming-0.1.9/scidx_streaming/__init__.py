"""scidx_streaming core package."""

from __future__ import annotations

from importlib import metadata
import warnings

# ndp_ep warns when its status endpoint cannot provide a version.
# Silence that noisy warning globally so notebooks/tests stay clean.
warnings.filterwarnings(
    "ignore",
    message=r"Could not determine API version from status endpoint.*",
    category=UserWarning,
)

from .client import StreamingClient
from .streams import StreamBlueprint, StreamHandle

try:
    __version__ = metadata.version("scidx_streaming")
except metadata.PackageNotFoundError:  # pragma: no cover - dev install
    __version__ = "0.1.0"

__all__ = ["StreamingClient", "StreamBlueprint", "StreamHandle", "__version__"]
