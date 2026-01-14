# Stream Consumption Guide

This guide explains how to use `StreamHandle` to consume derived topics in a
resource-friendly way.

## Quick start

```python
from scidx_streaming import StreamingClient

client = StreamingClient(ep_client)
handle = client.consume_stream("derived.population", store_path="artifacts/population.csv")

# Start from the latest offsets (default) and persist to disk
handle.start(poll_interval=1.0)

# Use the buffered data
print(handle.summary())
df = handle.dataframe()

# When you are finished with the topic
handle.stop()
```

Host/port are pulled from the `StreamingClient` setup, but you can override
them via `consume_stream(..., host="broker", port=9092)` when needed.

Set `from_beginning=True` on `start()` to rewind and stream from the earliest
available offset without committing anything to Kafka.

`store_path` on `consume_stream` or `set_store(path)` on the handle will
append every consumed record to CSV. Parent directories are created
automatically and the header is written once per file.

## Buffering & retention

- In-memory buffer backed by a deque (oldest → newest).
- Triple retention: **100,000 records**, **~20MB**, or **15 minutes**, whichever
  limit is hit first. Tune with
  `set_retention(max_records=..., max_bytes=..., max_age_seconds=...)`.
- `records()` and `dataframe()` read only from the buffer. If you need to keep
  everything, persist the data elsewhere (e.g., write to disk or a database)
  inside your consumption loop.

## Offsets & state

- Stateless by default: `group_id=None`, `enable_auto_commit=False`.
- `start(from_beginning=True)` uses `auto_offset_reset="earliest"`; otherwise
  the consumer begins at `latest`.
- No offsets are written back to Kafka, so you can restart or resume without
  affecting other consumers.

## Managing resources

- Use `start()` / `stop()` / `resume()` to control when the background poller
  runs. The consumer thread wakes up promptly when `stop()` is called.
- Toggle persistence at any time with `set_store("/tmp/records.csv")`; pass
  `store_path="...csv"` directly to `consume_stream` or
  `derived.connect(store_path=...)` to configure it up front.
- Manual ingestion via `ingest([...])` is available for offline notebooks and
  tests when you want the same buffer behaviour without a Kafka broker.

## API reference

- `start(from_beginning=False, retention_max_records=None, retention_max_bytes=None, retention_max_age_seconds=None, poll_interval=None)` – configure retention and start polling.
- `stop()` / `resume(**kwargs)` – pause/resume the background consumer.
- `records(limit=None)` / `dataframe(limit=None)` – buffered rows as Python dicts or a pandas `DataFrame`.
- `summary()` – counters, column names, running flag, and retention configuration.
- `set_retention(max_records=..., max_bytes=..., max_age_seconds=...)` – adjust limits at runtime.
- `set_store(path_or_none)` – append consumed records to CSV (creates parent directories).
- `ingest(records, timestamp=None)` – manually push records into the buffer (offline/testing helper).
