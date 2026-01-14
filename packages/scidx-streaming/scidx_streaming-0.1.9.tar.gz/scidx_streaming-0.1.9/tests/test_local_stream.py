from __future__ import annotations

from pathlib import Path

from scidx_streaming.streams.local import LocalStreamHandle, LocalStreamResult


def test_local_stream_result_connects(tmp_path: Path) -> None:
    result = LocalStreamResult(
        streaming_client=None,
        topic="local_test",
        sources=tuple(),
        filters=tuple(),
        source_types=tuple(),
        username=None,
        password=None,
    )
    handle = result.connect(store_path=tmp_path / "data.csv")
    assert isinstance(handle, LocalStreamHandle)
    assert handle.topic == "local_test"


def test_local_stream_handle_ingest_and_store(tmp_path: Path) -> None:
    handle = LocalStreamHandle(topic="local_buffer", sources=tuple(), store_path=tmp_path / "records.csv")
    handle.start()
    handle.ingest([{"value": 1}, {"value": 2}])
    summary = handle.summary()
    handle.stop()

    assert summary["stored_records"] == 2
    saved = tmp_path / "records.csv"
    assert saved.exists()
    contents = saved.read_text().strip().splitlines()
    # header + two rows
    assert len(contents) == 3


def test_local_stream_result_delete_cleans_handles_and_files(tmp_path: Path) -> None:
    result = LocalStreamResult(
        streaming_client=None,
        topic="local_test",
        sources=tuple(),
        filters=tuple(),
        source_types=tuple(),
        username=None,
        password=None,
    )
    store_path = tmp_path / "cleanup.csv"
    handle = result.connect(store_path=store_path)
    handle.start()
    handle.ingest([{"value": 1}])
    handle.stop()
    assert store_path.exists()

    cleanup = result.delete()
    assert cleanup["stopped_handles"] >= 1
    assert store_path.exists()  # delete() no longer removes user files
    assert str(store_path) in cleanup["store_paths"]
