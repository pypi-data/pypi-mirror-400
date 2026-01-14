"""Derived stream builder placeholders."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence, Tuple

from ..data_cleaning import CompiledFilters

from . import consumer as stream_consumer


@dataclass(slots=True)
class StreamBlueprint:
    """Immutable description of a derived stream request.

    The blueprint keeps enough metadata to:

    - Allocate a derived Kafka topic and register it in CKAN.
    - Recreate the compiled filters whenever workers restart.
    - Produce friendly docs/notebook snippets before the backend exists.
    """

    resource_ids: Tuple[str, ...] = field(default_factory=tuple)
    filters: CompiledFilters = field(default_factory=tuple)
    description: str | None = None

    def connect(self, topic: str, **overrides: Any) -> stream_consumer.StreamHandle:
        """Return a ``StreamHandle`` configured for the resolved topic."""

        return stream_consumer.StreamHandle(topic=topic, blueprint=self, overrides=overrides or None)


def create_stream_blueprint(
    *,
    resource_ids: Sequence[str],
    filters: CompiledFilters | None = None,
    description: str | None = None,
) -> StreamBlueprint:
    """Factory used by :class:`StreamingClient` to describe a derived stream.

    Parameters
    ----------
    resource_ids : Sequence[str]
        Source resource identifiers.
    filters : CompiledFilters | None
        Optional compiled filter tuple.
    description : str | None
        Optional human description carried with the blueprint.

    Returns
    -------
    StreamBlueprint
        Immutable blueprint that can be connected to a resolved topic.
    """

    return StreamBlueprint(
        resource_ids=tuple(resource_ids),
        filters=tuple(filters or ()),
        description=description,
    )
