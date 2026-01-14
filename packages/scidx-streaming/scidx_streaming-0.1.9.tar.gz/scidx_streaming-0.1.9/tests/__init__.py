"""Test suite helpers for scidx_streaming."""

import warnings

warnings.filterwarnings(
    "ignore",
    message=r"Could not determine API version from status endpoint.*",
    category=UserWarning,
)
