# SciDX Streaming Library

SciDX Streaming wraps an authenticated `ndp_ep.APIClient` so you can **register
datasets**, **manage resources**, **discover resources**, and **build derived
Kafka streams with filters**. Everything here is runnable against a CKAN +
Kafka stack.

## Quickstart (Kafka-only streaming)

```python
from ndp_ep import APIClient
from scidx_streaming import StreamingClient

client = StreamingClient(APIClient(base_url=API_URL, token=get_token()))

# Register a Kafka resource definition (stored in CKAN; points at the real topic)
client.register_resource(dataset_id, {
    "type": "kafka",
    "name": "drone_fleet_alpha",
    "description": "Kafka telemetry for Fleet Alpha (Barcelona area)",
    "host": "localhost",
    "port": 9092,
    "topic": "demo.drone.telemetry.fleet_alpha",
})

# Discover resources
results = client.search_resources(terms=[dataset_id], types=["kafka"])

# Build and consume a derived stream with filters
filters = client.compile_filters([
    {"type": "mapping", "column": "STATE", "action": "rename", "new_name": "state"},
    {"type": "comparison", "column": "state", "op": "eq", "value": "UT"},
    {"type": "comparison", "column": "value", "op": "gt", "value": 100},
])
derived = client.create_stream(resource_ids=[results.ids()[0]], filters=filters)
handle = derived.connect(client).start(from_beginning=True)
print(handle.summary())
handle.stop()
```

## What’s implemented in 0.1.8

- **Resource lifecycle**: register/update/deactivate/delete resource definitions (stored in CKAN). Definitions describe where the real data lives (Kafka topic/URL/etc.); CKAN never stores the data itself.
- **Discovery**: search the catalog for resource definitions by terms (keywords) and types.
- **Filters**: Mapping, comparison, and group filters that can be compiled and applied to the live data.
- **Derived streams**: Kafka topics that have been created using the resource definitions to get the real data with applyed filters. Local-only consumption is available for testing purposes or having private streams.
- **Consumers**: Handle for Kafka topics with bounded buffers, retention controls, and optional CSV persistence.

Planned but not yet wired: derived streams from API streams, RSS, and static files (csv/json/txt/netcdf).

## Producers vs. consumers (and CKAN’s role)

- **CKAN** holds **resource definitions only**: dataset metadata + connection
  details (Kafka host/port/topic, URLs, etc.).
- **Producers** publish the actual data to the sources referenced by those
  definitions (e.g., Kafka topics in the drone demo).
- **This library** reads the definitions from CKAN, connects to the real
  sources, and builds **derived Kafka topics** (public by default) that others
  can consume or further derive.
- **Consumers** use `StreamHandle` (or their own Kafka clients) to read derived
  topics; they can also create new derived streams with their own filters.

## Notebooks (GitHub only; not on PyPI)

- `notebooks/simulated_drone_demo/00_start_simulation.ipynb` → `04_cleanup.ipynb`  
  Full resource management + Kafka-derived streams + filters with real data.
- `notebooks/test/00_overview.ipynb`, `03_create_stream.ipynb`, `04_consumption.ipynb`  
  Lightweight regression/demo set.

Keep `.env` local (gitignored); use `.env_template` as a starting point.

## Documentation hub

See `docs/README.md` for the full guide set:

- Architecture/overview
- Resource lifecycle
- Discovery
- Filters (mapping/comparison/group)
- Derived streams & consumption

## Tests

Key checks live in `tests/` (offline + live Kafka/CKAN coverage). Run `pytest`
to validate resource lifecycle, filter compilation, stream creation, and
consumer behaviour before releasing.
