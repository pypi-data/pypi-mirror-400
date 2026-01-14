# Discovery & Search Guide

`StreamingClient.search_resources()` is the unified way to list resources across datasets, scopes, and lifecycle states. This guide explains how
to compose queries and interpret the results.

## API surface

```python
results = client.search_resources(
    terms=["air", DATASET_NAME],
    types=["kafka", "json"],
    include_inactive=False,
    server="global",   # optional: defaults to ndp_ep scope
)
```

Returns a `ResourceSearchResults` iterable:

```python
for record in results:
    print(record.id, record.type, record.name, record.dataset_id, record.state)

summary = results.summary()
# {'count': 2, 'types': {'kafka': 1, 'json': 1}, 'ids': ['raw_pop', 'json_batch']}
```

## Parameters

| Parameter | Description |
| --- | --- |
| `terms` | List of free-text terms matched against dataset names, titles, notes, or resource metadata. Empty list queries every dataset you can access. |
| `types` | Optional list of resource types (`kafka`, `csv`, etc.). Use `['*']` to match any type explicitly. |
| `include_inactive` | When `True`, results include resources that were deactivated (soft deleted). |
| `server` | Scope of the ndp_ep search (`"local"`, `"global"`, or `"pre_ckan"`). Inherits the API client’s default when omitted. |

## Common patterns

### Discover everything on a dataset

```python
records = client.search_resources(terms=[DATASET_NAME])
for record in records:
    print(f"{record.name} ({record.type}) -> {record.id}")
```

### Filter by type across datasets

```python
json_resources = client.search_resources(terms=[], types=["json"])
```

### Find inactive resources for cleanup

```python
inactive_resources = client.search_resources(terms=[DATASET_NAME], include_inactive=True)
stale = [record for record in inactive_resources if record.state == "inactive"]
```

### Inspect raw metadata

Each `record` exposes `metadata` (dict) in addition to the normalized
properties. Use this for ad-hoc debugging:

```python
record.metadata["method_definition"]
record.metadata.get("extras")
```

## Textual diagram suggestion

> Diagram showing `terms/types/include_inactive` funnel leading into CKAN
> search + dataset resources, highlighting how the client merges datasets from
> multiple scopes.

## Scope tips

- When `server` is omitted, queries run against the ndp_ep client’s default
  scope (usually `"global"`). Override per-call to target `"local"` datasets.
- The helper automatically retries both `"local"` and `"global"` scopes when no
  results are found in the preferred scope; this mirrors how lifecycle helpers
  locate datasets.

## Related notebooks

- `00_overview.ipynb` – demonstrates global vs. dataset-scoped queries.
- `01_registration_and_discovery.ipynb` – prints every record (active +
  inactive) and shows how IDs returned from search map to update/delete calls.
