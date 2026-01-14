# Resource Lifecycle Guide

This guide captures **how we register resource definitions in CKAN**. CKAN is
our catalog: it stores connection details (host/port/topic or URLs) and
metadata, **not the data itself**. Producers publish to the referenced sources;
the streaming library reads these definitions to connect and build derived
streams.

## Dataset metadata

Register datasets directly through `ndp_ep.register_general_dataset` with the
following required fields:

```python
dataset = {
    "name": "air_quality_station",
    "title": "Air Quality Station",
    "notes": "Daily + real-time air quality observations",
    "owner_org": "enviro-lab",
}
```

Optional CKAN fields (`tags`, `groups`, `extras`, `private`, etc.) are preserved
when the streaming helpers recreate datasets during hard deletes.

> **Diagram suggestion**: dataset node with attached resource nodes; arrows
> for register/update/delete.

## Resource payloads

Every resource is represented by a normalized payload:

```python
{
    "type": "kafka",       # required (kafka|csv|txt|json|netcdf|rss|api_stream|stream)
    "name": "drone_fleet_alpha",
    "description": "Kafka telemetry for Fleet Alpha (Barcelona area)",
    # type-specific fields (see below), this is a kafka example
    "host": "localhost",
    "port": 9092,
    "topic": "demo.drone.telemetry.fleet_alpha"
}
```

Type-specific reference tables (fields, meanings, examples) are below. Static
types (csv/txt/json/netcdf) are **URL-backed**; live types (kafka/rss/api_stream/stream)
represent ongoing feeds.

### CSV / TXT (static)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | HTTP(S) location of the text or CSV file. |
| `delimiter` | top-level or `processing` | optional | Field separator (`\t` default for TXT; CSV autodetect). |
| `header_line` | top-level or `processing` | optional | Zero-based header line (default 0). |
| `start_line` | top-level or `processing` | optional | First data line (default 1 when headers present). |

### JSON (batch, static)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | HTTP(S) endpoint returning JSON payloads. |
| `data_key` | top-level or `processing` | optional | Dotted path pointing to the record container. |
| `info_key` / `additional_key` | top-level or `processing` | optional | Paths merged into `stream_info`. |

### STREAM (HTTP streaming / SSE, live)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | Streaming endpoint (SSE, JSON lines). |
| `data_key` | top-level or `processing` | optional | Nested key to extract records before mapping. |
| `batch_mode`, `time_window`, `batch_interval` | top-level | optional | Batch behaviour + flushing cadence. |

### Kafka (live)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `host`, `port`, `topic` | top-level | ✓ | Bootstrap host/port/topic. |
| `security_protocol`, `sasl_mechanism`, `sasl_username`, `sasl_password`, `secret_reference` | top-level | optional | Auth settings (SASL_SSL, SCRAM, etc.). |
| `auto_offset_reset`, `time_window`, `batch_interval` | top-level | optional | Consumer posture (when applicable). |
| `data_key` | top-level or `processing` | optional | Nested key when messages contain nested structures. |

### NetCDF (static)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | HTTP(S) URL to the NetCDF (.nc/.nc4) file. |
| `group` | top-level | optional | HDF5 group inside the file. |

### RSS (live)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | RSS/Atom feed URL. |
| `fetch_mode`, `poll_interval`, `duration` | top-level or `processing` | optional | Polling cadence and lifetime. |

### API stream (live)

| Field | Location | Required | Description |
| --- | --- | --- | --- |
| `url` | top-level | ✓ | Streaming endpoint URL. |
| `headers`, `params`, `auth` | top-level | optional | HTTP request hints. |
| `data_key`, `batch_mode`, `time_window`, `batch_interval` | top-level or `processing` | optional | Batch/record extraction hints. |

## Lifecycle helpers

### Register / upsert

```python
client.register_resource(dataset_id, resource_payload, server="local")
```

Methods overwrite existing CKAN resources by `name` (or explicit `id`). Unique
names create new resources.

### Update

```python
client.update_resource(resource_id, {"description": "Updated"})
```

Updates merge fields and re-normalize the payload.

### Deactivate (soft delete)

```python
client.deactivate_resource(resource_id)
```

Sets `inactive=True` so discovery calls must opt-in via
`include_inactive=True`.

### Hard delete by id or name

```python
# By id (preferred when you have it)
client.delete_resource(resource_id)

# By name (supply dataset_id when duplicates exist)
client.delete_resource("csv_daily", dataset_id=dataset_name)
```

- Attempts deletion by id first; if not found, falls back to name lookup.
- When multiple matches exist for a name and no `dataset_id` is provided, a
  conflict summary is printed (dataset/name/id) and nothing is deleted until
  you disambiguate.
- Uses the same dataset recreation logic to keep CKAN accurate.

## Best practices

- **Idempotency**: use deterministic dataset + resource names so rerunning
  notebooks or scripts simply updates existing entries.
- **Versioning**: if a resource changes semantics radically, register it under a
  new name (e.g., `raw_pop_v2`) and retire the old one.
- **Multi-scope**: `server` defaults to the ndp_ep client scope; pass `"local"`
  or `"global"` explicitly when you need to target a specific CKAN instance.
- **Cleanup**: rely on the hard-delete helpers instead of calling ndp_ep
  directly—recreation keeps dataset metadata synchronized and avoids orphaned
  resources.

## Troubleshooting

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `CKANActionError: Dataset ... not found` | Dataset slug was never registered or lives in a different scope. | Re-run `register_general_dataset` or pass the correct `server`. |
| Delete-by-name deletes the wrong resource | Multiple datasets share the same resource name. | Provide `dataset_id` (or explicit id) to `delete_resource`. |
| Search results still show deleted resources | CKAN search can cache results for a few seconds. | Re-run with `include_inactive=True` to confirm state, or wait for cache to expire. |

## Notebook coverage

- **00_overview.ipynb** – quick tour of registration and both delete paths.
- **01_registration_and_discovery.ipynb** – full CRUD flow with multiple
  datasets and cleanup loops.

Use these notebooks as executable examples when onboarding users or reviewing
changes to lifecycle code.
