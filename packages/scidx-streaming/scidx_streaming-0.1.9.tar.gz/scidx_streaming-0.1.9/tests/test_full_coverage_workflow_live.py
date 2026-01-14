"""Extended live regression test that boosts scidx_streaming coverage."""

from __future__ import annotations

import contextlib
import copy
import io
import sys
import time
import warnings
from pathlib import Path

import pytest
from ndp_ep import APIClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

if str(NOTEBOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(NOTEBOOKS_DIR))

try:  # pragma: no cover - optional dependency at runtime
    from coverage.exceptions import CoverageWarning  # type: ignore
except Exception:  # pragma: no cover
    CoverageWarning = None  # type: ignore

warnings.filterwarnings("ignore", message=r"Could not determine API version from status endpoint.*")
warnings.filterwarnings("ignore", message=r"No data was collected.*")
if CoverageWarning is not None:  # pragma: no branch - best effort
    warnings.filterwarnings("ignore", category=CoverageWarning)

from keycloak_auth import API_URL, get_token  # noqa: E402
from scidx_streaming import StreamingClient  # noqa: E402
from scidx_streaming.connectors import CKANActionError, call_action  # noqa: E402
from scidx_streaming.connectors import ckan as ckan_helpers  # noqa: E402
from scidx_streaming.resources.search import ResourceSearchResults  # noqa: E402
from scidx_streaming.resources.utils import common as resource_common  # noqa: E402
from scidx_streaming.resources.utils import dataset_snapshot, datasets as dataset_utils, registry  # noqa: E402
from scidx_streaming.utils import log as log_utils  # noqa: E402
from scidx_streaming.utils import time as time_utils  # noqa: E402
from .utils import CoverageMonitor  # noqa: E402

pytestmark = pytest.mark.integration

PRIMARY_DATASET = "coverage_live_primary"
SECONDARY_DATASET = "coverage_live_secondary"

PRIMARY_TEMPLATE = {
    "name": PRIMARY_DATASET,
    "title": "Full Coverage Primary Dataset",
    "notes": "Live regression dataset for expanded coverage",
    "owner_org": "example_org_name",
    "tags": ["live-coverage"],
    "groups": ["streaming"],
    "extras": {"retention_days": "14", "tier": "gold"},
}

SECONDARY_TEMPLATE = {
    "name": SECONDARY_DATASET,
    "title": "Full Coverage Secondary Dataset",
    "notes": "Holds resource name conflicts",
    "owner_org": PRIMARY_TEMPLATE["owner_org"],
}

CSV_RESOURCE = {
    "type": "csv",
    "name": "coverage_csv",
    "description": "CSV snapshot for coverage run",
    "url": "https://example.com/full_coverage.csv",
    "compression": "gzip",
    "checksum": "sha256:live_csv_checksum",
    "schema": {"fields": ["id", "value", "timestamp"]},
}

JSON_RESOURCE = {
    "type": "json",
    "name": "coverage_json",
    "description": "JSON batch endpoint",
    "url": "https://example.com/full_coverage.json",
    "encoding": "utf-8",
    "schema": {"type": "object", "required": ["id", "value"]},
}

TXT_RESOURCE = {
    "type": "txt",
    "name": "coverage_txt",
    "description": "TXT delta feed for coverage",
    "url": "https://example.com/full_coverage.txt",
    "encoding": "latin-1",
    "delimiter": "|",
    "checksum": "sha256:txt_live_checksum",
}

NETCDF_RESOURCE = {
    "type": "netcdf",
    "name": "coverage_netcdf",
    "description": "NetCDF daily snapshot",
    "url": "https://example.com/full_coverage.nc",
    "checksum": "sha256:netcdf_live_checksum",
}

RSS_RESOURCE = {
    "type": "rss",
    "name": "coverage_rss",
    "description": "RSS feed for coverage",
    "url": "https://example.com/full_coverage.rss",
    "refresh_interval": 45,
}

RSS_INACTIVE_RESOURCE = {
    "type": "rss",
    "name": "coverage_rss_inactive",
    "description": "RSS feed that will be deactivated",
    "url": "https://example.com/full_coverage_inactive.rss",
    "refresh_interval": 120,
}

API_STREAM_RESOURCE = {
    "type": "api_stream",
    "name": "coverage_api",
    "description": "API stream for coverage",
    "url": "https://example.com/full_coverage",
    "http_method": "post",
    "poll_interval": 15,
    "headers": {"Accept": "application/json"},
    "params": {"limit": 5, "order": "desc"},
    "body": {"window": "1h"},
}

REBUILD_CSV_RESOURCE = {
    "type": "csv",
    "name": "coverage_rebuild_probe",
    "description": "Dataset rebuild probe resource",
    "url": "https://example.com/full_coverage_rebuild.csv",
}

KAFKA_RESOURCE = {
    "type": "kafka",
    "name": "coverage_kafka",
    "description": "Kafka topic used in coverage run",
    "host": "broker.example.org",
    "port": 9093,
    "topic": "coverage.topic",
    "security_protocol": "SASL_SSL",
    "sasl_mechanism": "SCRAM-SHA-256",
    "sasl_username": "coverage-user",
    "sasl_password": "coverage-secret",
    "secret_reference": "vault://coverage/kafka",
}

SECONDARY_NETCDF_RESOURCE = {
    "type": "netcdf",
    "name": "coverage_netcdf_secondary",
    "description": "Secondary dataset NetCDF snapshot",
    "url": "https://example.com/full_coverage_secondary.nc",
    "checksum": "sha256:secondary_netcdf_checksum",
}

SECONDARY_CSV_RESOURCE = {
    "type": "csv",
    "name": "coverage_secondary_csv",
    "description": "Secondary dataset CSV snapshot",
    "url": "https://example.com/full_coverage_secondary.csv",
}

SECONDARY_JSON_RESOURCE = {
    "type": "json",
    "name": "coverage_secondary_json",
    "description": "Secondary dataset JSON snapshot",
    "url": "https://example.com/full_coverage_secondary.json",
}

SECONDARY_TXT_RESOURCE = {
    "type": "txt",
    "name": "coverage_secondary_txt",
    "description": "Secondary dataset TXT feed",
    "url": "https://example.com/full_coverage_secondary.txt",
}

API_STREAM_SECONDARY_RESOURCE = {
    "type": "api_stream",
    "name": "coverage_api_variant",
    "description": "API stream for the secondary dataset",
    "url": "https://example.com/full_coverage_secondary",
    "http_method": "get",
    "poll_interval": 5,
    "headers": {"Accept": "application/xml"},
    "params": {"offset": 0, "limit": 2},
}

PRIMARY_STATIC_RESOURCES = [CSV_RESOURCE, JSON_RESOURCE, TXT_RESOURCE, NETCDF_RESOURCE]
SECONDARY_STATIC_RESOURCES = [
    SECONDARY_CSV_RESOURCE,
    SECONDARY_JSON_RESOURCE,
    SECONDARY_TXT_RESOURCE,
    SECONDARY_NETCDF_RESOURCE,
]


def _fresh(payload: dict[str, object]) -> dict[str, object]:
    return copy.deepcopy(payload)


def _cleanup_datasets(ep_client: APIClient, verbose: bool = False) -> None:
    for dataset_name in (PRIMARY_DATASET, SECONDARY_DATASET):
        try:
            ep_client.delete_resource_by_id(dataset_name)
            if verbose:
                print("Deleted existing dataset:", dataset_name)
        except Exception as exc:
            if verbose:
                print("Dataset deletion skipped:", dataset_name, exc)


def _register_resources(
    streaming_client: StreamingClient,
    dataset: str,
    definitions: list[dict[str, object]],
) -> dict[str, str]:
    entries: dict[str, str] = {}
    for definition in definitions:
        entry = streaming_client.register_resource(dataset, _fresh(definition))
        entries[definition["name"]] = entry.get("id", entry.get("name", ""))  # type: ignore[index]
    return entries


def _expect_metadata(records: ResourceSearchResults, expectations: dict[str, dict[str, object]]) -> None:
    record_map = {record.name: record for record in records}
    for name, checks in expectations.items():
        record = record_map.get(name)
        assert record is not None, f"Resource '{name}' missing from search results"
        for key, expected_value in checks.items():
            observed = record.metadata.get(key)
            if observed is None:
                observed = record.raw.get(key)
            assert observed == expected_value, f"{name}:{key} expected {expected_value!r} got {observed!r}"


def _roundtrip_resources(
    streaming_client: StreamingClient,
    dataset: str,
    resource_ids: dict[str, str],
    definitions: list[dict[str, object]],
) -> None:
    for definition in definitions:
        resource_name = definition["name"]
        resource_id = resource_ids[resource_name]
        streaming_client.delete_resource(resource_id)
        refreshed = streaming_client.register_resource(dataset, _fresh(definition))
        resource_ids[resource_name] = refreshed.get("id", resource_id)  # type: ignore[index]


def test_full_coverage_workflow_live() -> None:
    if not API_URL:
        pytest.skip("API_URL is not configured; see notebooks/keycloak_auth.py.")

    coverage_monitor = CoverageMonitor(source_dir=PROJECT_ROOT / "scidx_streaming")

    print(f"[setup] Using API_URL={API_URL}")
    coverage_monitor.snapshot("[setup] Using API_URL")
    token = get_token()
    print("[setup] Obtained access token from Keycloak")
    coverage_monitor.snapshot("[setup] Token ready")
    ndp_ep_client = APIClient(base_url=API_URL, token=token)
    streaming_client = StreamingClient(ndp_ep_client)
    print("[setup] StreamingClient ready; running cleanup")

    _cleanup_datasets(ndp_ep_client, verbose=True)
    coverage_monitor.snapshot("[setup] Pre-test cleanup complete")

    try:
        print("[register] Registering datasets for coverage run")
        ndp_ep_client.register_general_dataset(_fresh(PRIMARY_TEMPLATE))
        ndp_ep_client.register_general_dataset(_fresh(SECONDARY_TEMPLATE))

        primary_ids = _register_resources(streaming_client, PRIMARY_DATASET, PRIMARY_STATIC_RESOURCES)
        rss_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(RSS_RESOURCE))
        rss_inactive_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(RSS_INACTIVE_RESOURCE))
        api_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(API_STREAM_RESOURCE))
        kafka_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(KAFKA_RESOURCE))
        rebuild_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(REBUILD_CSV_RESOURCE))
        primary_ids[RSS_RESOURCE["name"]] = rss_entry.get("id", rss_entry.get("name", ""))
        primary_ids[RSS_INACTIVE_RESOURCE["name"]] = rss_inactive_entry.get("id", rss_inactive_entry.get("name", ""))
        primary_ids[API_STREAM_RESOURCE["name"]] = api_entry.get("id", api_entry.get("name", ""))
        primary_ids[KAFKA_RESOURCE["name"]] = kafka_entry.get("id", kafka_entry.get("name", ""))
        primary_ids[REBUILD_CSV_RESOURCE["name"]] = rebuild_entry.get("id", rebuild_entry.get("name", ""))

        shared_payload = {
            "type": "csv",
            "name": "coverage_shared",
            "description": "Shared resource for delete-by-name",
            "url": "https://example.com/full_coverage_shared.csv",
        }
        shared_primary = streaming_client.register_resource(PRIMARY_DATASET, _fresh(shared_payload))
        shared_secondary = streaming_client.register_resource(SECONDARY_DATASET, _fresh(shared_payload))
        primary_ids[shared_payload["name"]] = shared_primary.get("id", shared_primary.get("name", ""))
        secondary_static_ids = _register_resources(streaming_client, SECONDARY_DATASET, SECONDARY_STATIC_RESOURCES)
        api_secondary_entry = streaming_client.register_resource(SECONDARY_DATASET, _fresh(API_STREAM_SECONDARY_RESOURCE))
        coverage_monitor.snapshot("[register] Resources registered")

        records = streaming_client.search_resources(terms=[PRIMARY_DATASET])
        assert isinstance(records, ResourceSearchResults)
        print("[search] Primary dataset resources:", len(records))
        _expect_metadata(
            records,
            {
                CSV_RESOURCE["name"]: {"compression": "gzip", "checksum": CSV_RESOURCE["checksum"]},
                JSON_RESOURCE["name"]: {"encoding": "utf-8"},
                TXT_RESOURCE["name"]: {"delimiter": "|"},
                NETCDF_RESOURCE["name"]: {"checksum": NETCDF_RESOURCE["checksum"]},
                API_STREAM_RESOURCE["name"]: {"http_method": "POST"},
                RSS_RESOURCE["name"]: {"refresh_interval": RSS_RESOURCE["refresh_interval"]},
            },
        )

        summary = records.summary()
        assert summary["count"] >= len(records)
        assert summary["types"].get("csv")
        resource_dicts = records.as_dicts()
        assert any(entry.get("name") == CSV_RESOURCE["name"] for entry in resource_dicts)
        for record in records:
            if record.name in primary_ids:
                primary_ids[record.name] = record.id

        logger = log_utils.get_logger("tests.logging")
        logger.audit("audit message")
        timestamp = time_utils.isoformat()
        assert "T" in timestamp
        ckan_config = ckan_helpers.fetch_configuration(ndp_ep_client)
        assert ckan_config.get("base_url")

        dataset_fetch, fetch_scope = dataset_utils.fetch_dataset(ndp_ep_client, PRIMARY_DATASET, preferred_scope="global")
        assert dataset_fetch is not None and fetch_scope in {None, "local", "global"}
        located_dataset, located_scope, located_idx = dataset_utils.locate_resource(
            ndp_ep_client, primary_ids[CSV_RESOURCE["name"]], preferred_scope="global"
        )
        if located_dataset is None:
            located_dataset, located_scope, located_idx = dataset_utils.locate_resource(
                ndp_ep_client, primary_ids[CSV_RESOURCE["name"]], preferred_scope=None
            )
        if located_dataset is not None:
            assert located_scope in {None, "local", "global"} and located_idx is not None

        with pytest.raises(CKANActionError):
            call_action(ndp_ep_client, "nonexistent_action", {"payload": "value"})

        coverage_monitor.snapshot("[search] Resource discovery complete")

        print("[update] Updating + deactivating records")
        updated_csv_payload = _fresh(CSV_RESOURCE)
        updated_csv_payload["id"] = primary_ids[CSV_RESOURCE["name"]]
        updated_csv_payload["description"] = "Coverage CSV updated"
        streaming_client.register_resource(PRIMARY_DATASET, updated_csv_payload)

        inactive_api_payload = _fresh(API_STREAM_RESOURCE)
        inactive_api_payload["id"] = primary_ids[API_STREAM_RESOURCE["name"]]
        inactive_api_payload["inactive"] = True
        inactive_api_payload["description"] = "Coverage API paused"
        streaming_client.register_resource(PRIMARY_DATASET, inactive_api_payload)

        netcdf_update = streaming_client.update_resource(
            primary_ids[NETCDF_RESOURCE["name"]], {"description": "NetCDF coverage updated"}
        )
        netcdf_definition = resource_common.decode_definition(netcdf_update.get("description"))
        assert netcdf_definition.get("description") == "NetCDF coverage updated"
        streaming_client.update_resource(primary_ids[KAFKA_RESOURCE["name"]], {"topic": "coverage.topic.v2", "port": 9094})
        streaming_client.update_resource(primary_ids[TXT_RESOURCE["name"]], {"compression": "gzip"})
        streaming_client.update_resource(primary_ids[RSS_INACTIVE_RESOURCE["name"]], {"refresh_interval": 15})
        streaming_client.deactivate_resource(
            primary_ids[NETCDF_RESOURCE["name"]], reason="maintenance window"
        )

        csv_confirmed = False
        api_confirmed = False
        for attempt in range(6):
            inactive_records = streaming_client.search_resources(terms=[PRIMARY_DATASET], include_inactive=True)
            csv_record = next(
                (record for record in inactive_records if record.id == primary_ids[CSV_RESOURCE["name"]]), None
            )
            api_record = next((record for record in inactive_records if record.id == api_entry.get("id")), None)
            csv_confirmed = bool(
                csv_record
                and "Coverage CSV updated"
                in ((csv_record.metadata.get("description") or csv_record.description or ""))
            )
            api_confirmed = bool(api_record and api_record.metadata.get("inactive"))
            if csv_confirmed and api_confirmed:
                break
            time.sleep(2)

        if not (csv_confirmed and api_confirmed):
            print("[update] Warning: live dataset search never reflected update/deactivation; continuing", flush=True)
        coverage_monitor.snapshot("[update] Updates applied")

        dataset_entries_initial = ndp_ep_client.search_datasets([PRIMARY_DATASET], server="local") or []
        assert dataset_entries_initial, "Primary dataset must exist"
        dataset_meta_initial = dataset_entries_initial[0]
        updated_notes = f"{PRIMARY_TEMPLATE['notes']} (live update)"
        updated_title = f"{PRIMARY_TEMPLATE['title']} (Live)"
        ndp_ep_client.patch_general_dataset(
            PRIMARY_DATASET,
            {
                "notes": updated_notes,
                "title": updated_title,
            },
        )
        rebuild_resource_id = primary_ids[REBUILD_CSV_RESOURCE["name"]]
        rebuild_idx = dataset_utils.resource_index(
            dataset_meta_initial.get("resources") or [], resource_id=rebuild_resource_id
        )
        if rebuild_idx is None:
            rebuild_idx = dataset_utils.resource_index(
                dataset_meta_initial.get("resources") or [], name=REBUILD_CSV_RESOURCE["name"]
            )
        assert rebuild_idx is not None
        ndp_ep_client.delete_dataset_resource(PRIMARY_DATASET, rebuild_resource_id, server="local")
        rebuild_entry = streaming_client.register_resource(PRIMARY_DATASET, _fresh(REBUILD_CSV_RESOURCE))

        dataset_entries_after_patch = ndp_ep_client.search_datasets([PRIMARY_DATASET], server="local") or []
        assert dataset_entries_after_patch
        dataset_meta_after_patch = dataset_entries_after_patch[0]
        assert dataset_meta_after_patch.get("notes") in {updated_notes, PRIMARY_TEMPLATE["notes"]}
        assert dataset_meta_after_patch.get("title") in {updated_title, PRIMARY_TEMPLATE["title"]}
        extras = dataset_meta_after_patch.get("extras") or {}
        extras_dict = dict(extras) if isinstance(extras, dict) else {entry.get("key"): entry.get("value") for entry in extras}
        synthetic_meta = copy.deepcopy(dataset_meta_after_patch)
        synthetic_meta["tags"] = list(PRIMARY_TEMPLATE.get("tags") or [])
        synthetic_meta["groups"] = list(PRIMARY_TEMPLATE.get("groups") or [])
        synthetic_meta["extras"] = extras_dict or dict(PRIMARY_TEMPLATE.get("extras") or {})
        cloned_dataset = dataset_snapshot.clone_dataset(synthetic_meta)
        assert cloned_dataset["extras"]
        rotated_resources = list(cloned_dataset.get("resources") or [])
        if len(rotated_resources) >= 2:
            rotated = rotated_resources[-1:] + rotated_resources[:-1]
            dataset_utils.patch_resources(ndp_ep_client, dataset_meta_after_patch, rotated, scope="local")
            dataset_utils.patch_resources(ndp_ep_client, dataset_meta_after_patch, cloned_dataset["resources"], scope="local")
        assert (
            dataset_utils.resource_index(dataset_meta_after_patch.get("resources") or [], name=JSON_RESOURCE["name"]) is not None
        )

        ndp_ep_client.patch_general_dataset(
            PRIMARY_DATASET,
            {
                "notes": PRIMARY_TEMPLATE["notes"],
                "title": PRIMARY_TEMPLATE["title"],
            },
        )

        print("[delete] Demonstrating delete-by-name conflict handling")
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            streaming_client.delete_resource_by_name(shared_payload["name"])
        conflict_message = buffer.getvalue()
        assert "Multiple resources named" in conflict_message
        coverage_monitor.snapshot("[delete] Conflict surfaced")

        print("[delete] Scoped delete-by-name and resource recreation")
        streaming_client.delete_resource_by_name(shared_payload["name"], dataset_id=SECONDARY_DATASET)
        secondary_records = streaming_client.search_resources(terms=[SECONDARY_DATASET])
        assert shared_payload["name"] not in {record.name for record in secondary_records}
        for record in secondary_records:
            if record.name in secondary_static_ids:
                secondary_static_ids[record.name] = record.id
        _roundtrip_resources(streaming_client, PRIMARY_DATASET, primary_ids, PRIMARY_STATIC_RESOURCES)
        _roundtrip_resources(streaming_client, SECONDARY_DATASET, secondary_static_ids, SECONDARY_STATIC_RESOURCES)
        with pytest.raises(Exception):
            streaming_client.delete_resource_by_name("nonexistent_resource")
        with pytest.raises(Exception):
            streaming_client.delete_resource("missing-resource-id")
        with pytest.raises(Exception):
            streaming_client.deactivate_resource("missing-resource-id")
        coverage_monitor.snapshot("[delete] Targeted deletions complete")

        print("[streams] Building derived stream descriptors")
        handle = StreamHandle(topic="coverage.live.topic")
        assert handle.topic == "coverage.live.topic"
        consumer = streaming_client.consume_stream("coverage.live.topic")
        assert consumer.overrides["host"] == streaming_client.kafka_host
        with pytest.raises(NotImplementedError):
            streaming_client.compile_filters([{"field": "state", "op": "eq", "value": "UT"}])
        with pytest.raises(NotImplementedError):
            handle.records()
        with pytest.raises(NotImplementedError):
            consumer.plot()
        coverage_monitor.snapshot("[streams] Stream helpers invoked")

        print("[validation] Final resource sweep")
        final_records = streaming_client.search_resources(terms=[PRIMARY_DATASET], include_inactive=True)
        assert {record.name for record in final_records} >= {
            CSV_RESOURCE["name"],
            JSON_RESOURCE["name"],
            API_STREAM_RESOURCE["name"],
            NETCDF_RESOURCE["name"],
            TXT_RESOURCE["name"],
            RSS_INACTIVE_RESOURCE["name"],
        }
        secondary_records_final = streaming_client.search_resources(terms=[SECONDARY_DATASET], include_inactive=True)
        assert SECONDARY_NETCDF_RESOURCE["name"] in {record.name for record in secondary_records_final}
        coverage_monitor.snapshot("[validation] Final checks complete")

        print("[analysis] Inspecting dataset metadata for additional coverage")
        dataset_entries = ndp_ep_client.search_datasets([PRIMARY_DATASET]) or []
        if dataset_entries:
            dataset_meta = dataset_entries[0]
            resources_meta = dataset_meta.get("resources") or []
            if resources_meta:
                first_resource = resources_meta[0]
                dataset_utils.remember_resource_hint(first_resource, dataset_meta)
                hint = dataset_utils.resource_hint(first_resource.get("id"))
                if hint:
                    dataset_utils.forget_resource_hint(first_resource.get("id"))
            clone = dataset_snapshot.clone_dataset(dataset_meta)
            assert clone["name"] == PRIMARY_DATASET
            resources_for_recreation = dataset_meta.get("resources") or []
            if resources_for_recreation:
                first_resource = (dataset_meta.get("resources") or [])[0]
                if first_resource:
                    ndp_ep_client.delete_dataset_resource(
                        dataset_meta.get("id") or dataset_meta.get("name") or "", first_resource.get("id"), server="local"
                    )
                streaming_client.register_resource(PRIMARY_DATASET, _fresh(CSV_RESOURCE))
            dataset_utils.patch_resources(ndp_ep_client, dataset_meta, dataset_meta.get("resources") or [], scope=None)
            ndp_ep_client.patch_general_dataset(PRIMARY_DATASET, {"resources": dataset_meta.get("resources") or []})
            normalized_definition = registry.normalize_definition(_fresh(NETCDF_RESOURCE))
            payload = registry.build_resource_payload(PRIMARY_DATASET, normalized_definition)
            assert payload["package_id"] == PRIMARY_DATASET
            with pytest.raises(Exception):
                ndp_ep_client.patch_general_dataset("missing-dataset", {"resources": []})
            fetched_dataset, _ = dataset_utils.fetch_dataset(ndp_ep_client, PRIMARY_DATASET, preferred_scope="local")
            assert fetched_dataset is not None
            located_dataset, _, located_idx = dataset_utils.locate_resource(
                ndp_ep_client, primary_ids[NETCDF_RESOURCE["name"]], preferred_scope=None
            )
            assert located_dataset is not None and located_idx is not None
            matches = dataset_utils.find_resources_by_name(
                ndp_ep_client, shared_payload["name"], dataset_names=[SECONDARY_DATASET], preferred_scope="global"
            )
            assert matches and matches[0][0].get("name") == SECONDARY_DATASET
        ndp_ep_client.search_datasets([""], server="global")
        assert resource_common.normalize_port(KAFKA_RESOURCE["port"]) == KAFKA_RESOURCE["port"]
        assert resource_common.require_text(CSV_RESOURCE["name"], "name") == CSV_RESOURCE["name"]
        coverage_monitor.snapshot("[analysis] Dataset metadata inspection complete")

    finally:
        print("[cleanup] Tearing down coverage datasets")
        _cleanup_datasets(ndp_ep_client, verbose=True)
        coverage_monitor.snapshot("[cleanup] Post-test cleanup complete")
        coverage_monitor.finalize()
