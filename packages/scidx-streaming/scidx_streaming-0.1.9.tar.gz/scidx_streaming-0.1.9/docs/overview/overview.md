# SciDX Streaming – Overview

SciDX Streaming sits between two systems:

- A **data catalog** (datasets + resource definitions).
- A **Kafka cluster** (live/derived streams).

The library only stores **metadata** about sources (where data lives and how to
connect); it never stores the data itself. CKAN holds resource definitions
(host/port/topic or URLs); producers publish to those sources; the streaming
library reads the definitions to build derived Kafka topics others can consume.

## Who uses it

- **Providers / producers** – register and manage resource definitions in the
  catalog and publish data to the referenced sources.
- **Consumers** – discover resource definitions and create “SciDX derived
  streams” on Kafka from those resources, or consume existing derived topics.

## What lives in the catalog vs. Kafka

### Catalog side – resource definitions

Providers can:

- Register new **resource definitions** (static files or live feeds) on a
  dataset. Definitions include host/port/topic or URLs plus metadata—no data
  is stored in CKAN.
- Discover existing resources and their configuration.
- Manage lifecycle: update fields, temporarily deactivate, or delete.

### Kafka side – scidx derived streams

We can:

- Create derived streams from one or more resources.
- Apply filters (for example, only a subset of records).
- Share the created derived streams.
- Consume the derived stream from a Kafka topic via a helper.

> Parts of the stream behaviour (filters, record handling, plotting) are still
> being implemented. The code is modular and versioned so we can evolve safely.

## Main object: `StreamingClient`

`StreamingClient` extends the existing `ndp_ep.APIClient` with SciDX streaming
capabilities (catalog management + Kafka topic helpers).

When you construct it, you pass the `APIClient` you already use. The streaming
client then:

1. Keeps a reference to that `APIClient`.
2. Checks catalog connectivity.
3. Finds and connects to Kafka (or respects explicit host/port overrides).

After that:

- Use the `APIClient` for dataset-level operations (create, patch, delete).
- Use `StreamingClient` for resource operations and stream operations.

## What `StreamingClient` can do

### Resource operations (providers)

- **`register_resource`** – register one resource definition on an existing
  dataset (CSV, TXT, JSON, NetCDF, Kafka, RSS, API stream).
- **`update_resource`** – patch selected fields on a resource definition.
- **`deactivate_resource`** – mark a resource inactive instead of deleting it;
  shows up only when `include_inactive=True`.
- **`delete_resource`** – delete by ID or name (name deletion guards against
  ambiguity by asking for a dataset id if multiple matches exist).
- **`register_dataset`** – _planned_ helper to create a dataset and register
  resources in one call.

### Discovery (providers and consumers)

- **`search_resources`** – discover resource definitions matching text terms
  and/or types; returns a `ResourceSearchResults` container with `.ids()`,
  `.summary()`, and `.as_dicts()`.

### Stream-related (next steps)

The stream story follows three steps. Today **only Kafka sources** are wired
end-to-end; other resource types can be registered/discovered but cannot yet
feed a derived stream.

1. **`compile_filters`** – accept mapping/comparison/group rules, normalize,
   and return a compiled filter tuple.
2. **`create_stream`** – fan-in **Kafka resources** into a derived Kafka topic;
   filters are applied before forwarding. Set `use_kafka=False` to consume
   Kafka sources locally without creating a derived topic.
3. **`consume_stream`** – return a `StreamHandle` consumer for an existing
   derived topic with helpers for start/stop/summary/dataframe/persistence.

## Documentation map

- **API reference (all functions, signatures, examples)** – `docs/api_reference.md`
- **Resources** – `docs/resources.md`
- **Discovery** – `docs/discovery.md`
- **Filters** – `docs/filters.md`
- **Streams** – `docs/streams.md`
- **Stream consumption runtime** – `docs/streams/consumption.md`

The `docs/README.md` hub links every guide and notebook.

## Notebooks

- `notebooks/test/00_overview.ipynb` – registration + lifecycle + discovery.
- `notebooks/test/03_create_stream.ipynb` / `04_consumption.ipynb` – Kafka
  stream creation and consumption with filters.
- `notebooks/simulated_drone_demo/*` – full drone scenario (resource
  management, Kafka-derived streams with filters, sharing/consuming).

Use notebooks as living run-books and keep them aligned with the API reference
as stream features mature.
