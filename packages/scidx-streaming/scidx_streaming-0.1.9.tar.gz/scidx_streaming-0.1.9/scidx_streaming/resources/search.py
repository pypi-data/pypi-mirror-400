"""Discovery helpers for registered resources."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterator, Mapping, Sequence

from ..connectors.ckan import CKANActionError
from .utils import registry as resource_registry


@dataclass(frozen=True, slots=True)
class ResourceRecord:
    """Normalized view of a CKAN resource representing a streaming resource."""

    id: str
    dataset_id: str | None
    type: str | None
    name: str | None
    description: str | None
    state: str | None
    metadata: Mapping[str, Any]
    raw: Mapping[str, Any]

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "ResourceRecord":
        """Create a ResourceRecord from a raw CKAN mapping."""
        record_id = str(payload.get("id") or payload.get("resource_id") or "")
        dataset_id = payload.get("package_id") or payload.get("dataset_id")
        metadata = resource_registry.load_definition_from_resource(payload)
        name = metadata.get("name") or payload.get("name")
        description = metadata.get("description") or payload.get("description")
        resource_type = metadata.get("type") or payload.get("format") or payload.get("type")
        state = payload.get("state")
        return cls(
            id=record_id,
            dataset_id=str(dataset_id) if dataset_id else None,
            type=str(resource_type) if resource_type else None,
            name=str(name) if name else None,
            description=str(description) if description else None,
            state=str(state) if state else None,
            metadata=dict(metadata),
            raw=dict(payload),
        )


class ResourceSearchResults(Sequence[ResourceRecord]):
    """Container that decorates CKAN resource search responses."""

    def __init__(self, methods: Sequence[ResourceRecord]) -> None:
        self._methods = tuple(methods)

    def __len__(self) -> int:
        return len(self._methods)

    def __getitem__(self, index: int) -> ResourceRecord:
        return self._methods[index]

    def __iter__(self) -> Iterator[ResourceRecord]:
        return iter(self._methods)

    def __repr__(self) -> str:  # pragma: no cover - presentation only
        preview = [{"id": r.id, "type": r.type, "dataset": r.dataset_id} for r in self._methods[:3]]
        return f"ResourceSearchResults(count={len(self)}, preview={preview})"

    def as_dicts(self) -> list[Mapping[str, Any]]:
        """Return raw CKAN resource payloads as a list of dicts."""
        return [dict(record.raw) for record in self._methods]

    def ids(self) -> list[str]:
        """Return a list of resource ids."""
        return [record.id for record in self._methods if record.id]

    def summary(self) -> dict[str, Any]:
        """Return summary counts by type along with ids."""
        type_counts = Counter(record.type or "unknown" for record in self._methods)
        return {"count": len(self), "types": dict(sorted(type_counts.items())), "ids": self.ids()}

    def summary_pretty(self, *, include_details: bool = True) -> str:
        """Return a human-friendly summary string."""

        lines = [f"Search summary of {len(self)} resource(s):"]
        if not self._methods:
            return "\n".join(lines)

        type_counts = Counter(record.type or "unknown" for record in self._methods)
        for rtype, count in sorted(type_counts.items(), key=lambda item: item[0]):
            lines.append(f"- {count} × type '{rtype}'")

        if include_details:
            for record in self._methods:
                lines.append(f"  • id={record.id} type={record.type or 'unknown'} dataset={record.dataset_id or '-'} name={record.name or '-'}")
        return "\n".join(lines)


def search_resources(
    ep_client: Any,
    *,
    terms: Sequence[str] | None = None,
    types: Sequence[str] | None = None,
    server: str | None = None,
    include_inactive: bool = False,
) -> ResourceSearchResults:
    """Search dataset resources via the ndp_ep client and normalize results.

    Parameters
    ----------
    ep_client : Any
        ndp_ep API client exposing ``search_datasets``.
    terms : Sequence[str] | None
        Dataset names/ids or free-text terms; empty list searches everything.
    types : Sequence[str] | None
        Resource types to include (csv/json/kafka/etc.).
    server : str | None
        Preferred scope; automatically falls back to local/global.
    include_inactive : bool
        When True, include resources marked inactive.

    Returns
    -------
    ResourceSearchResults
        Iterable wrapper over normalized ``ResourceRecord`` objects.

    Raises
    ------
    CKANActionError
        If the ndp_ep client does not expose ``search_datasets``.
    """

    searcher = getattr(ep_client, "search_datasets", None)
    if not callable(searcher):
        raise CKANActionError("ndp_ep client does not expose 'search_datasets'.")

    queries = [str(term).strip() for term in (terms or []) if str(term).strip()] or [""]
    scopes = [server] if server else []
    for fallback in ("local", "global"):
        if fallback not in scopes:
            scopes.append(fallback)
    if not scopes:
        scopes = [None]

    desired_types = tuple(type_name.lower() for type_name in (types or []))
    term_set = {term.lower() for term in queries if term}
    seen_datasets: set[str] = set()
    records: list[ResourceRecord] = []

    for scope in scopes:
        try:
            dataset_entries = searcher(list(queries), server=scope) or []
        except Exception:
            continue
        for dataset_entry in dataset_entries:
            dataset_name = str(dataset_entry.get("name") or "")
            dataset_id = str(dataset_entry.get("id") or dataset_name or "")
            if not dataset_id or dataset_id in seen_datasets:
                continue
            if term_set and dataset_id.lower() not in term_set and dataset_name.lower() not in term_set:
                continue
            seen_datasets.add(dataset_id)
            for resource in dataset_entry.get("resources") or []:
                if not _is_serialized_definition(resource.get("description")):
                    continue
                definition = resource_registry.load_definition_from_resource(resource)
                if not _is_valid_definition(definition):
                    continue
                enriched = dict(resource)
                enriched.setdefault("package_id", dataset_id)
                enriched.setdefault("dataset_id", dataset_id)
                record = ResourceRecord.from_mapping(enriched)
                if desired_types and (record.type or "").lower() not in desired_types:
                    continue
                if not include_inactive and not _is_active(record):
                    continue
                records.append(record)

    return ResourceSearchResults(records)


def _is_valid_definition(definition: Mapping[str, Any]) -> bool:
    """Return True when the resource definition has basic required fields."""
    return bool(definition.get("name") and definition.get("type") and definition.get("description"))


def _is_serialized_definition(description: object) -> bool:
    """Return True when the CKAN description field holds JSON for a definition."""
    if not isinstance(description, str):
        return False
    stripped = description.strip()
    return stripped.startswith("{") and stripped.endswith("}")


def _is_active(record: ResourceRecord) -> bool:
    """Return True when the resource is active and not explicitly inactive."""
    inactive_flag = bool(record.metadata.get("inactive"))
    state = (record.state or "active").lower()
    return state == "active" and not inactive_flag


__all__ = ["ResourceRecord", "ResourceSearchResults", "search_resources"]
