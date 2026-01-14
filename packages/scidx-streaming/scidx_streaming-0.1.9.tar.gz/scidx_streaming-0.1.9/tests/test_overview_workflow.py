"""Live regression test that mirrors the 00_overview notebook."""

from __future__ import annotations

import copy
import contextlib
import io
import sys
from pathlib import Path

import pytest
from ndp_ep import APIClient

# Reuse the exact Keycloak helpers that the notebook imports.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
if str(NOTEBOOKS_DIR) not in sys.path:
    sys.path.insert(0, str(NOTEBOOKS_DIR))

from keycloak_auth import API_URL, get_token  # noqa: E402  (import after path tweak)
from scidx_streaming import StreamingClient  # noqa: E402
from .utils import CoverageMonitor  # noqa: E402


pytestmark = pytest.mark.integration

DATASET_NAME = "overview_test"
SECONDARY_DATASET_NAME = "another_overview_dataset"

DATASET_TEMPLATE = {
    "name": DATASET_NAME,
    "title": "SciDX Overview Dataset",
    "notes": "Seeded by 00_overview.ipynb",
    "owner_org": "example_org_name",
}

SECONDARY_DATASET_TEMPLATE = {
    "name": SECONDARY_DATASET_NAME,
    "title": "SciDX Overview Dataset (alt)",
    "notes": "Supports delete-by-name demo",
    "owner_org": DATASET_TEMPLATE["owner_org"],
}

CSV_METHOD = {
    "type": "csv",
    "name": "csv_daily",
    "description": "Daily CSV snapshot for overview demo",
    "url": "https://example.com/daily.csv",
}

KAFKA_METHOD = {
    "type": "kafka",
    "name": "kafka_gnns",
    "description": "Raw POP topic used in derived streams",
    "host": "broker.example.org",
    "port": 9092,
    "topic": "raw.pop",
}

JSON_METHOD = {
    "type": "json",
    "name": "json_batch",
    "description": "JSON batch endpoint for overview demo",
    "url": "https://example.com/data.json",
}


class _CoverageMonitor(CoverageMonitor):
    def __init__(self) -> None:
        super().__init__(source_dir=PROJECT_ROOT / "scidx_streaming")


def _fresh(payload: dict[str, object]) -> dict[str, object]:
    """Return a deep copy so notebook calls can mutate safely."""

    return copy.deepcopy(payload)


def _cleanup_datasets(ep_client: APIClient, *, verbose: bool) -> None:
    """Run the same cleanup loop as the notebook."""

    for dataset_name in (DATASET_NAME, SECONDARY_DATASET_NAME):
        try:
            ep_client.delete_resource_by_id(dataset_name)
            if verbose:
                print("Deleted existing dataset:", dataset_name)
        except Exception as exc:  # pragma: no cover - depends on live state
            if verbose:
                print("Dataset deletion skipped:", dataset_name, exc)


def test_overview_notebook_flow_live() -> None:
    """Execute the exact workflow from notebooks/00_overview.ipynb."""

    if not API_URL:
        pytest.skip("API_URL is not configured; see notebooks/keycloak_auth.py.")

    coverage_monitor = _CoverageMonitor()

    message = f"[setup] Using API_URL={API_URL}"
    print(message)
    coverage_monitor.snapshot(message)
    token = get_token()
    message = "[setup] Obtained access token from Keycloak"
    print(message)
    coverage_monitor.snapshot(message)
    ndp_ep_client = APIClient(base_url=API_URL, token=token)
    streaming_client = StreamingClient(ndp_ep_client)
    message = "[setup] StreamingClient ready; running pre-test cleanup"
    print(message)

    _cleanup_datasets(ndp_ep_client, verbose=True)
    coverage_monitor.snapshot("[setup] Pre-test cleanup complete")

    try:
        message = f"[register] Registering datasets: {DATASET_NAME}, {SECONDARY_DATASET_NAME}"
        print(message)
        ndp_ep_client.register_general_dataset(_fresh(DATASET_TEMPLATE))
        ndp_ep_client.register_general_dataset(_fresh(SECONDARY_DATASET_TEMPLATE))
        coverage_monitor.snapshot(message)

        message = f"[register] Attaching resources to {DATASET_NAME}"
        print(message)
        streaming_client.register_resource(DATASET_NAME, _fresh(CSV_METHOD))
        streaming_client.register_resource(DATASET_NAME, _fresh(JSON_METHOD))
        streaming_client.register_resource(DATASET_NAME, _fresh(KAFKA_METHOD))
        coverage_monitor.snapshot(message)

        message = f"[register] Attaching resources to {SECONDARY_DATASET_NAME}"
        print(message)
        streaming_client.register_resource(SECONDARY_DATASET_NAME, _fresh(JSON_METHOD))
        coverage_monitor.snapshot(message)

        records = streaming_client.search_resources(terms=[DATASET_NAME])
        print("[search] Discovered resources:", len(records))
        for record in records:
            status = "inactive" if record.metadata.get("inactive") else "active"
            print("-", record.name or record.id, record.type, status)
        assert len(records) == 3
        assert {record.name for record in records} == {"csv_daily", "json_batch", "kafka_gnns"}
        coverage_monitor.snapshot("[search] Resource discovery complete")

        json_record = next(
            (r for r in streaming_client.search_resources(terms=[DATASET_NAME]) if r.type == "json"),
            None,
        )
        assert json_record is not None, "JSON record not found; rerun the registration cell."

        streaming_client.update_resource(json_record.id, {"description": "Updated from overview notebook"})
        streaming_client.deactivate_resource(json_record.id)
        print("[update] Updated + deactivated JSON record:", json_record.id)
        coverage_monitor.snapshot("[update] JSON update + deactivate complete")

        refreshed = streaming_client.search_resources(terms=[DATASET_NAME], include_inactive=True)
        refreshed_json = next((r for r in refreshed if r.id == json_record.id), None)
        assert refreshed_json is not None
        assert refreshed_json.metadata.get("description") == "Updated from overview notebook"
        assert refreshed_json.metadata.get("inactive") is True

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            streaming_client.delete_resource_by_name(JSON_METHOD["name"])
        conflict_message = buffer.getvalue()
        if conflict_message:
            print(conflict_message, end="")
        assert "Multiple resources named" in conflict_message

        records_after_conflict = streaming_client.search_resources(terms=[DATASET_NAME], include_inactive=True)
        assert any(record.name == JSON_METHOD["name"] for record in records_after_conflict)
        print("[delete] Delete-by-name without scope left resource untouched (as expected)")
        coverage_monitor.snapshot("[delete] Verified dataset-scoped delete")

        streaming_client.delete_resource_by_name(JSON_METHOD["name"], dataset_id=DATASET_NAME)
        print(f"Deleted {JSON_METHOD['name']} from dataset {DATASET_NAME} by name.")
        coverage_monitor.snapshot("[delete] Targeted json_batch deletion complete")

        remaining = streaming_client.search_resources(terms=[DATASET_NAME])
        assert {record.name for record in remaining} == {"csv_daily", "kafka_gnns"}

        for resource in remaining:
            streaming_client.delete_resource(resource.id)
            print("Deleted resource:", resource.name or resource.id)
        coverage_monitor.snapshot("[delete] Remaining resources deleted")

        assert len(streaming_client.search_resources(terms=[DATASET_NAME])) == 0
        coverage_monitor.snapshot("[delete] Dataset resources emptied")

    finally:
        message = "[cleanup] Tearing down datasets after test"
        print(message)
        _cleanup_datasets(ndp_ep_client, verbose=True)
        coverage_monitor.snapshot(message)
        coverage_monitor.finalize()
