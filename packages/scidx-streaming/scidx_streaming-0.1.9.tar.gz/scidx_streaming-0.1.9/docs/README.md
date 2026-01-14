# SciDX Streaming Documentation Hub

Use this directory as the central hub for the streaming library. The layout is
flat at the top (this page) with folders for each topic so we can keep adding
detail without clutter.

## Start here

| Topic | Path | Description |
| --- | --- | --- |
| Product / architecture overview | `overview/overview.md` | Personas, high-level workflow, and the catalog/Kafka split. |
| API reference | `api/api_reference.md` | Full function/class reference with signatures, behaviour, and examples. |
| Resource lifecycle | `resources/resources.md` | Dataset metadata, payload schemas, register/update/deactivate/delete flows. |
| Discovery & search | `discovery/discovery.md` | `search_resources` usage, scope nuances, and filtering tips. |
| Filters | `filters/filters.md` | Filter DSL (mapping / comparison / group), compilation API, best practices. |
| Streams | `streams/streams.md` | Kafka-only stream creation today; roadmap for other source types. |
| Stream consumption runtime | `streams/consumption.md` | StreamHandle buffering/retention/start-stop details. |

## Notebook index

| Notebook | Purpose |
| --- | --- |
| `notebooks/test/00_overview.ipynb` | Regression-friendly walkthrough of the registration + discovery lifecycle. |
| `notebooks/test/03_create_stream.ipynb` | Minimal derived-stream creation with filters (Kafka only). |
| `notebooks/test/04_consumption.ipynb` | Consumer buffer/retention/persistence demo. |
| `notebooks/simulated_drone_demo/00_start_simulation.ipynb` → `04_cleanup.ipynb` | End-to-end drone scenario: resource management, Kafka-derived streams with filters, sharing/consumption. |

## How to use this structure

1. Read `overview/overview.md` (or the `00_overview` notebook) to align on the
   mental model.
2. Jump into a topic folder (resources, discovery, filters, streams) for
   implementation details.
3. Use `api/api_reference.md` when you need exact signatures/behaviour.
4. Reference the notebooks while onboarding—they mirror production APIs and
   include textual diagram prompts for slide decks.

## Getting help from the code

- In IPython/Jupyter: `client.register_resource?` or `client.create_stream??` to
  see docstrings/source.
- In a REPL: `help(client.register_resource)` or `help(StreamingClient.create_stream)`.
- Module view: `python -m pydoc scidx_streaming.client`.
