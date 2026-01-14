# SciDX Streaming API Reference

This reference covers **all** functions and classes in the library: public
surface for users and internal helpers for maintainers. Each entry states
inputs, behaviour, outputs, options, and a minimal example where applicable.
This structure is meant to stay compatible with future UML generation
(py2puml-friendly).

Conventions:

- Parameters marked `*` are keyword-only.
- `server` refers to ndp_ep scope (`"local"`/`"global"`).
- Errors are raised as `ValueError`/`RuntimeError`/`CKANActionError` unless
  noted.

## StreamingClient facade (`scidx_streaming.client`)

### Constructor

`StreamingClient(ep_client, *, kafka_host=None, kafka_port=None)`

- **Inputs**: authenticated `ndp_ep.APIClient`; optional Kafka overrides.
- **Behaviour**: validates `ep_client`, decodes `user_id` from JWT, derives
  topic prefix/stream limits, probes CKAN connectivity, resolves Kafka endpoint
  (ndp_ep config or overrides), builds admin client, fetches cluster metadata
  when possible.
- **Outputs**: instance with `ep_client`, `kafka_host`, `kafka_port`,
  `kafka_bootstrap`, `kafka_connection`, `kafka_cluster_info`, `ckan_status`,
  `user_id`, `kafka_prefix`, `max_streams`.
- **Internal helper**: `_decode_user_id(token)` best-effort JWT decode.

### Resource lifecycle (provider-facing)

All methods delegate to `scidx_streaming.resources.*` and return CKAN resource
entries unless stated.

- `register_resource(dataset_id, resource_payload, *, server=None)` – normalize
  payload and upsert on dataset. Creates a new entry when name/ID is new.
- `update_resource(resource_id, updates, *, server=None)` – merge updates into
  stored definition and re-normalize.
- `deactivate_resource(resource_id, *, reason=None, server=None)` –
  soft-delete; sets `inactive=True` and preserves record.
- `delete_resource(resource, *, dataset_id=None, server=None)` – delete by id
  or name. If treated as a name and multiple matches exist, prints the matches
  and asks for `dataset_id` or an explicit id.

Example:

```python
client.register_resource(
    dataset_id="weather",
    resource_payload={"type": "csv", "name": "csv_daily", "description": "...", "url": "https://.../daily.csv"},
)
```

### Discovery

- `search_resources(terms=None, *, types=None, server=None, include_inactive=False)`
  → `ResourceSearchResults`. See details under Discovery.

### Filters

- `compile_filters(filter_definitions)` → `CompiledFilters`. Validates and
  normalizes mapping/comparison/group rules before attaching them to streams
  or local fan-in.

### Streams

- `create_stream(*, resource_ids, filters=None, description=None, server=None, username=None, password=None, use_kafka=True)`
  → `DerivedStreamResult` (Kafka) or `LocalStreamResult` (local-only).
  - **Source support**: Kafka resources only (fan-in). Other resource types
    can be registered/discovered but cannot yet power derived streams.
  - `use_kafka=True` allocates/creates a Kafka topic using defaults, registers
    the derived resource in CKAN (public by default), and starts an async
    `DerivedProducer` (fan-in from sources).
  - `use_kafka=False` skips Kafka/CKAN and returns a local fan-in handle for
    in-process consumption only (same buffer API as `StreamHandle`).
  - `username`/`password` are forwarded to source handlers (Kafka today).
- `consume_stream(topic, *, host=None, port=None, from_beginning=None, retention_max_records=None, retention_max_bytes=None, retention_max_age_seconds=None, poll_interval=None, store_path=None)`
  → `StreamHandle`.
  - Resolves host/port from client if unspecified, configures retention/poll
    interval overrides. `store_path` appends consumed rows to CSV and
    auto-creates parent directories.

Example:

```python
derived = client.create_stream(resource_ids=["raw.kafka.pop"], description="Population stream")
handle = client.consume_stream(derived.topic).start(from_beginning=True)
print(handle.summary())
handle.stop()
```

## Resource lifecycle modules (`scidx_streaming.resources.*`)

### `register_resource(ep_client, dataset_id, resource_payload, *, server=None)`

- **Inputs**: dataset id/slug, resource payload (type/name/description +
  type-specific fields such as host/port/topic for Kafka or url for static
  files/feeds).
- **Behaviour**: normalize via `registry.normalize_definition`, fetch dataset,
  build resource entry, upsert into dataset resources (by id/name), patch CKAN,
  re-fetch authoritative entry.
- **Returns**: CKAN resource mapping (with IDs).

### `update_resource(ep_client, resource_id, updates, *, server=None)`

- **Behaviour**: locate resource, merge stored definition with updates, rebuild
  entry, patch CKAN.
- **Returns**: updated CKAN resource entry.

### `deactivate_resource(ep_client, resource_id, *, reason=None, server=None)`

- **Behaviour**: wrapper over `update_resource` with `inactive=True` and
  `preserve_record=True`; adds `deactivation_reason` when provided.

### `delete_resource(ep_client, resource_id, *, server=None)`

- **Behaviour**: locate resource (with cached hints), recreate dataset without
  the resource via delete + re-register; clears cached hints.
- **Returns**: `None`.

### `delete_resource_by_name(ep_client, resource_name, *, dataset_id=None, server=None)`

- **Behaviour**: find matches by name (optionally dataset-scoped); on
  ambiguity, prints conflict summary and aborts; otherwise delegates to dataset
  recreation. Used internally when the client-level delete receives a name.

## Discovery (`scidx_streaming.resources.search`)

- `search_resources(ep_client, *, terms=None, types=None, server=None, include_inactive=False)`
  – search datasets via `ep_client.search_datasets`, filter for serialized
  streaming definitions, normalize to `ResourceRecord`.
  - Respects scope order: preferred scope → `local` → `global`.
  - Filters by type list and `include_inactive`.
- `ResourceSearchResults` (Sequence):
  - `.ids()` – list of resource ids.
  - `.summary()` – `{"count": int, "types": {...}, "ids": [...]}`.
  - `.as_dicts()` – raw CKAN payloads.
- Internal validators: `_is_valid_definition`, `_is_serialized_definition`,
  `_is_active`.

Example:

```python
results = client.search_resources(terms=["weather"], types=["kafka"])
print(results.summary())
```

## Filters (`scidx_streaming.data_cleaning.filters`)

- `compile_filters(filter_definitions)` – normalize/validate mapping,
  comparison, and group rules into immutable tuples. Operators: `eq/neq/gt/gte/lt/lte/in/nin/between`.
- `explain_filter(filter_definition)` – human-readable rendering of one rule.
- `compile_filters_with_descriptions(filter_definitions)` – compile and fill
  missing `description` fields automatically.

Filters are applied to JSON-decoded payloads before records are forwarded to
derived Kafka topics or local buffers.

## Streams & derived topics (`scidx_streaming.streams.*`)

### High-level objects

- `StreamBlueprint(resource_ids, filters=(), description=None)` – immutable
  description of a desired stream. `.connect(topic, **overrides)` returns a
  `StreamHandle` bound to the topic.
- `create_stream_blueprint(resource_ids, filters=None, description=None)` –
  convenience factory.
- `DerivedStreamResult` / `LocalStreamResult` (from `create_stream`):
  - Fields: `topic`, `sources`, `filters`, `source_types`; Kafka mode also
    includes `resource`, `dataset_id`, `created_topic`, `producer`.
  - `.connect(streaming_client, host=None, port=None, store_path=None, **overrides)` –
    build a `StreamHandle` (Kafka) or `LocalStreamHandle` (local fan-in).

### Stream creation flow (`streams.creation.common`)

- `create_stream(...)` – orchestrates derived stream creation (see
  `StreamingClient.create_stream`). Validates source types; when `use_kafka`
  is enabled it creates a Kafka topic + CKAN entry and starts
  `DerivedProducer`, otherwise it returns a local fan-in result.
- Internal: `_start_producer(producer)` best-effort event-loop launcher.

### Kafka-specific creation (`streams.creation.types.kafka`)

- `create_kafka_stream(streaming_client, *, sources, filters=None, server=None, description=None)`
  → `KafkaDerivedResult` (`topic`, `resource`, `dataset_id`, `sources`,
  `filters`, `created_topic`).
- `_ensure_topic(streaming_client, topic, partitions, replication_factor)` –
  create topic if absent; returns `True` when created.
- `_build_kafka_definition(...)` – build CKAN payload with sources + filters.

### Creation utilities (`streams.creation.base`)

- `resolve_sources(streaming_client, resource_ids, *, server=None)` – locate
  CKAN resources and return `SourceResource` objects.
- `derive_prefix(ep_client, *, override=None, default="derived_stream_")` –
  resolve topic prefix (override → env → ndp_ep config → default).
- `derive_max_streams(ep_client, *, override=None, default=10)` – resolve
  allowed concurrent streams.
- `clean_user_id(user_id)` – Kafka-safe user token.
- `topic_prefix(prefix, user_id)` – combine prefix and user id.
- `list_topics(streaming_client)` – list Kafka topics (empty tuple on failure).
- `next_stream_id(existing_topics, topic_base, max_streams)` – find next free
  numeric suffix or raise if exhausted.
- `register_derived_resource(streaming_client, dataset_id, definition, *, server=None)` –
  register CKAN entry for derived topic.
- `mark_resource_inactive(streaming_client, resource_id, *, reason=None, server=None)` –
  convenience wrapper around `deactivate_resource`.

### Derived producer runtime (`streams.runtime.producer`)

- `DerivedProducer.run()` – async: start Kafka producer, launch source-specific
  ingestion tasks, monitor for failures, mark resource inactive on stop/error.
- `DerivedProducer.stop()` – async: cancel tasks, stop producer, mark inactive.
- Internals: `_handler_for_source`, `_consume_kafka_source`, `_forward_message`,
  `_shutdown_producer`, `_mark_inactive`.

### Kafka source handler (`streams.runtime.handlers.kafka`)

- `consume_kafka_source(source, stop_event, username, password, forward_message, mark_inactive)` –
  consume from Kafka source definition and forward bytes to derived producer;
  tries multiple auth modes.
- Internals: `_build_attempts(...)` (ordered auth attempts),
  `_is_auth_error(exc)`.

### Stream consumption runtime (`streams.consumer`)

- `StreamHandle(topic, blueprint=None, overrides=None, consumer_factory=None, store_path=None)`
  - `.start(from_beginning=None, retention_max_records=None, retention_max_bytes=None, retention_max_age_seconds=None, poll_interval=None)` – configure retention, build consumer, begin background polling.
  - `.stop()` / `.resume(**kwargs)` – control background thread and consumer.
  - `.records(limit=50)` – list of buffered records.
  - `.dataframe(limit=None)` – pandas DataFrame view of buffer.
  - `.summary()` – counts, columns, retention, running flag.
  - `.ingest(records, timestamp=None)` – inject records manually (tests/offline).
  - `.set_retention(max_records=None, max_bytes=None, max_age_seconds=None)` –
    adjust buffer policy.
  - `.set_store(path)` – enable CSV persistence of consumed records.
- Internal helpers:
  - `_Buffer.configure/add/snapshot/summary/_evict` – bounded buffer logic.
  - `_normalize(value)` / `_estimate_size(payload)` – decode Kafka values and
    size estimates for retention.

## Connectors

### CKAN (`scidx_streaming.connectors.ckan`)

- `check_connection(ep_client)` – ensure `base_url`/`token`/`session` exist.
- `fetch_configuration(ep_client)` – read CKAN configuration if exposed.
- `call_action(ep_client, action, payload, *, server=None)` – POST to CKAN
  action endpoint using ndp_ep session, raise `CKANActionError` on failure.
- `normalize_payload(base)` – recursively ensure JSON-serializable payloads.

### Kafka (`scidx_streaming.connectors.kafka`)

- `resolve_connection(ep_client, *, host=None, port=None)` → `KafkaEndpoint`
  (`host`, `port`, `.bootstrap`).
- `connect(endpoint, *, client_id="scidx-streaming", security_config=None, request_timeout_ms=5000)` →
  `KafkaConnection` with admin client.
- `disconnect(connection)` – close admin.
- `describe_cluster(connection)` → `KafkaClusterInfo` (`topic_count`, `topics`,
  `broker_count`, `controller_id`, `cluster_id`).

## Resource utilities (`scidx_streaming.resources.utils.*`)

### Common helpers

- `clean_text(value)`, `require_text(value, field)`, `normalize_port(value)`,
  `as_mapping(value)`, `uuid_name()`, `clean_payload(values)`,
  `encode_definition(definition)`, `decode_definition(raw)`,
  `load_definition_from_resource(resource)`, `resource_state(definition)`.

### Registry (`resources.utils.registry`)

- `_normalize_static(payload, resource_type)`, `_normalize_single(fn)` – internal adapters.
- `normalize_definition(raw_definition)` – validate/normalize resource payload.
- `merge_definitions(stored, updates)` – merge + normalize.
- `build_resource_payload(dataset_id, definition, *, existing_id=None)` – CKAN
  payload for dataset registration.
- `build_dataset_resource_entry(definition, *, resource_id=None)` – CKAN
  resource entry (dataset `resources` list).
- Constants: `SUPPORTED_RESOURCE_TYPES`, `URL_BACKED_RESOURCE_TYPES`.

### Dataset lookups (`resources.utils.datasets`)

- `fetch_dataset(ep_client, dataset_ref, *, preferred_scope)` – find dataset by
  id/slug across scopes.
- `locate_resource(ep_client, resource_id, *, preferred_scope)` – find dataset
  + index for resource id.
- `find_resources_by_name(ep_client, resource_name, *, dataset_names=None, preferred_scope=None)` –
  list matches by name.
- `patch_resources(ep_client, dataset, resources, scope)` – call
  `patch_general_dataset`.
- `resource_index(resources, *, resource_id=None, name=None)` – locate resource
  index in dataset list.
- `remember_resource_hint(resource, dataset)`, `resource_hint(resource_id)`,
- `forget_resource_hint(resource_id)` – cache for cross-scope lookups.
- Internals: `_iter_datasets(...)`, `_remember_dataset(...)`.

### Dataset snapshots/recreate

- `clone_dataset(dataset, *, skip_resource_index=None)` – copy metadata +
  resources, optionally omitting one resource; validates name/title/owner_org.
- `recreate_dataset_without_resource(ep_client, dataset, scope, skip_index)` –
  delete dataset then re-register without the target resource.
- Internals: `_compact_named_entries(...)`, `_normalize_extras(...)`,
  `_clone_resources(...)`, `_sanitize_resource_entry(...)`, `_delete_dataset`,
  `_register_dataset`.

### Resource type normalizers (`resources.utils.types.*`)

- Kafka: `normalize(payload)`, `resource_extras(definition)`, `build_url(definition)`.
- Static files (csv/txt/json/netcdf): `normalize(payload, resource_type)`,
  `resource_extras`, `build_url`.
- API stream: `normalize(payload)`, `resource_extras`, `build_url`.
- RSS: `normalize(payload)`, `resource_extras`, `build_url`.

## Logging & time utilities (`scidx_streaming.utils`)

- `configure_logging(level=None)` – one-time logger config (env overrides,
  JSON/standard formatter, file sink support).
- `get_logger(name)` – namespaced logger ensuring configuration.
- `_coerce_level(level)` – internal resolver (supports ints/env strings).
- `now_utc()` – timezone-aware UTC datetime.
- `isoformat(ts=None)` – ISO-8601 string (UTC) for provided/now timestamp.

## Testing-friendly examples

- **Register + search**:

```python
client.register_resource(DATASET_ID, {"type": "kafka", "name": "raw_pop", "description": "...", "host": "...", "port": 9092, "topic": "raw.pop"})
resources = client.search_resources(terms=[DATASET_ID], types=["kafka"])
print(resources.ids())
```

- **Create + consume derived stream** (Kafka source):

```python
compiled = client.compile_filters([
    {"type": "mapping", "column": "STATE", "action": "rename", "new_name": "state"},
    {"type": "comparison", "column": "state", "op": "eq", "value": "UT"},
])
derived = client.create_stream(resource_ids=["raw_pop"], filters=compiled, description="UT filter")
handle = derived.connect(client).start(from_beginning=True, poll_interval=1.0)
time.sleep(3)
print(handle.summary())
handle.stop()
```

Keep code examples minimal and runnable; extend them in notebook-specific docs
when more detail is needed.
