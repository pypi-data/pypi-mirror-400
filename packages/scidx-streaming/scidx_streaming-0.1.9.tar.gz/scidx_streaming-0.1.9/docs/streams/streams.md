# Stream Creation & Consumption

SciDX Streaming builds **derived Kafka topics** from catalog resources and
provides a lightweight consumer for those topics. Derived topics are registered
in CKAN (public by default) so others can consume or build their own derived
streams on top.

CKAN stores **resource definitions only** (Kafka host/port/topic, etc.); the
library reads those definitions, connects to the real sources, and pushes
filtered records into derived topics.

## 1) Compile filters (mapping / comparison / group)

```python
filters = client.compile_filters([
    {"type": "mapping", "column": "STATE", "action": "rename", "new_name": "state"},
    {"type": "comparison", "column": "state", "op": "eq", "value": "UT"},
    {"type": "comparison", "column": "value", "op": "gt", "value": 100},
])
```

- Rules are structured dicts with `type` in `{"mapping","comparison","group"}`.
- Mapping rules drop/rename columns; comparison rules cover `eq/neq/gt/gte/lt/lte/in/nin/between`; group rules combine comparisons with AND/OR.
- Compilation validates the shape and returns immutable tuples applied at runtime (before forwarding records).

## 2) Create a derived stream (Kafka today)

```python
derived = client.create_stream(
    resource_ids=["raw.kafka.pop"],
    filters=filters,
    description="Population stream filtered by state",
    use_kafka=True,   # default; set False for local-only consumption
)

print(derived.topic, derived.created_topic)
print(derived.resource)  # CKAN entry describing the derived topic
```

Topic prefix and max-stream allocation are derived from ndp_ep/env defaults;
partition/replication settings currently use library defaults.

### Supported sources

- **Kafka resources only**: fan-in one or more Kafka sources into a new Kafka
  topic. Filters are applied before messages are forwarded.
- `use_kafka=False` fans in Kafka sources locally (no CKAN/Kafka footprint) but
  still applies the same filters and exposes the StreamHandle API.

Static files, RSS, API stream, and NetCDF resources can be registered and
discovered, but they cannot yet drive derived streams.

### Result fields

- `topic` – derived Kafka topic name (Kafka mode) or local stream label.
- `resource` – CKAN resource entry registered for the derived stream (Kafka mode).
- `dataset_id` – dataset that holds the derived resource definition (Kafka mode).
- `sources` – `SourceResource` objects for each input.
- `filters` – filter payloads applied (may be empty).
- `created_topic` – `True` when topic was newly created (Kafka mode).
- `connect(streaming_client, host=None, port=None, **overrides)` – convenience
  to get a `StreamHandle`/`LocalStreamHandle` bound to this topic. Pass
  `store_path="local.csv"` to append consumed rows to disk.

Topic names follow `derive_prefix(user)_N` where `derive_prefix` comes from
ndp_ep config/env/defaults, `user` comes from the JWT, and `N` is the next
available integer (see `next_stream_id` in the API reference).

## 3) Consume the stream

Use either `DerivedStreamResult.connect(...)` or `client.consume_stream(...)`
to obtain a `StreamHandle` for an existing topic.

```python
consumer = derived.connect(client, from_beginning=True, poll_interval=1.0)
consumer.start()            # begins background polling
time.sleep(3)
print(consumer.summary())   # counts + retention
df = consumer.dataframe()   # pandas view
consumer.stop()
```

### StreamHandle quick reference

- `.start(from_beginning=False, retention_max_records=None, retention_max_bytes=None, retention_max_age_seconds=None, poll_interval=None)` – configure retention and start polling (stateless consumer, no commits).
- `.stop()` / `.resume(**kwargs)` – pause/resume the background consumer.
- `.records(limit=None)` / `.dataframe(limit=None)` – snapshot the bounded buffer.
- `.summary()` – topic, running flag, retention config, counts, observed columns.
- `.set_retention(max_records=None, max_bytes=None, max_age_seconds=None)` – adjust limits on the fly (defaults: 100k records / ~20MB / 15 minutes).
- `.set_store(path)` – persist consumed records to CSV (appends, auto-creates parent directories).
- `.ingest(records, timestamp=None)` – manually push records (tests/offline demos).

See `docs/streams/consumption.md` for deeper operational notes.

## Current limitations and roadmap

- Derived streams: **Kafka-only** fan-in. Additional handlers (static files,
  RSS, API stream, NetCDF) will reuse the same pattern when implemented.
- Derived topic configuration is fixed to the library defaults (1 partition,
  replication factor 1); per-call overrides are not yet exposed.
- Filters operate on JSON-decoded payloads; ensure Kafka messages are JSON to
  benefit from mapping/comparison/group rules.
