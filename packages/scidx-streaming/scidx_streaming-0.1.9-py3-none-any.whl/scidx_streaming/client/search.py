"""Search helpers for ``StreamingClient``."""

from __future__ import annotations

from typing import Sequence

from ..resources import ResourceSearchResults, search_resources as _search_resources


def search_resources(
    self: "StreamingClient",
    terms: Sequence[str] | None = None,
    *,
    types: Sequence[str] | None = None,
    server: str | None = None,
    include_inactive: bool = False,
) -> ResourceSearchResults:
    """Search CKAN for resource definitions and wrap the response.

    Parameters
    ----------
    terms : Sequence[str] | None
        Dataset names/ids or free-text search terms. Terms are matched against
        dataset names/titles/notes and also against serialized resource
        definitions contained in those datasets.
    types : Sequence[str] | None
        Optional resource types to include (csv/json/kafka/etc.).
    server : str | None
        ndp_ep scope override; falls back to the client's default scope.
    include_inactive : bool
        When True, include resources marked inactive.

    Returns
    -------
    ResourceSearchResults
        Iterable container exposing:
        - ``ids()`` → list of matching resource IDs
        - ``summary()`` → dict with counts, types, and IDs
        - ``as_dicts()`` → raw CKAN resource payloads (dicts)
    """

    return _search_resources(
        self.ep_client,
        terms=terms,
        types=types,
        server=server,
        include_inactive=include_inactive,
    )
