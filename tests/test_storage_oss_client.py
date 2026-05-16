from __future__ import annotations

import pytest

from app.config import AppSettings
from app.storage import (
    AlibabaOssStorageClient,
    MockOssStorageClient,
    StorageConfigError,
    create_storage_client,
)
from app.storage.oss_client import (
    CONTENT_TYPE_JSON,
    CONTENT_TYPE_JSONL,
    CONTENT_TYPE_MARKDOWN,
    CONTENT_TYPE_TEXT,
)


def test_mock_upload_bytes_records_data_and_metadata() -> None:
    client = MockOssStorageClient()

    uploaded = client.upload_bytes("raw/steam_news/game/patch/20260115T120000Z.json", b"{}", CONTENT_TYPE_JSON)

    assert uploaded.key == "raw/steam_news/game/patch/20260115T120000Z.json"
    assert uploaded.content_type == CONTENT_TYPE_JSON
    assert uploaded.size_bytes == 2
    stored = client.objects[uploaded.key]
    assert stored.data == b"{}"
    assert stored.content_type == CONTENT_TYPE_JSON
    assert stored.size_bytes == 2


def test_upload_json_uses_deterministic_serialization() -> None:
    client = MockOssStorageClient()

    uploaded = client.upload_json("reports/game/patch/action_board.json", {"b": 2, "a": 1})

    assert uploaded.content_type == CONTENT_TYPE_JSON
    assert client.objects[uploaded.key].data == b'{"a":1,"b":2}'


def test_upload_text_and_markdown_use_utf8_content_types() -> None:
    client = MockOssStorageClient()

    text_upload = client.upload_text("processed/patch_notes/game/patch/patch_notes.txt", "Patch notes")
    markdown_upload = client.upload_markdown("reports/game/patch/live_ops_brief.md", "# Brief")

    assert text_upload.content_type == CONTENT_TYPE_TEXT
    assert markdown_upload.content_type == CONTENT_TYPE_MARKDOWN
    assert client.objects[text_upload.key].data == b"Patch notes"
    assert client.objects[markdown_upload.key].data == b"# Brief"


def test_upload_jsonl_writes_compact_sorted_rows_with_trailing_newline() -> None:
    client = MockOssStorageClient()

    uploaded = client.upload_jsonl("exports/fine_tuning/game/patch/classification_dataset.jsonl", [{"b": 2, "a": 1}])

    assert uploaded.content_type == CONTENT_TYPE_JSONL
    assert client.objects[uploaded.key].data == b'{"a":1,"b":2}\n'


def test_upload_jsonl_empty_rows_write_empty_object() -> None:
    client = MockOssStorageClient()

    uploaded = client.upload_jsonl("exports/fine_tuning/game/patch/classification_dataset.jsonl", [])

    assert uploaded.size_bytes == 0
    assert client.objects[uploaded.key].data == b""


def test_create_storage_client_returns_mock_for_mock_oss_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("USE_MOCK_OSS", "true")

    client = create_storage_client()

    assert isinstance(client, MockOssStorageClient)


def test_real_client_missing_config_raises_without_secret_values() -> None:
    settings = AppSettings(
        alibaba_cloud_access_key_id="AK_TEST_SHOULD_NOT_LEAK",
        alibaba_cloud_access_key_secret="SECRET_TEST_SHOULD_NOT_LEAK",
        oss_endpoint="",
        oss_bucket_name="",
        use_mock_oss=False,
    )

    with pytest.raises(StorageConfigError) as exc_info:
        AlibabaOssStorageClient(settings=settings)

    message = str(exc_info.value)
    assert "OSS_ENDPOINT" in message
    assert "OSS_BUCKET_NAME" in message
    assert "AK_TEST_SHOULD_NOT_LEAK" not in message
    assert "SECRET_TEST_SHOULD_NOT_LEAK" not in message


def test_factory_with_real_client_missing_config_raises_config_error() -> None:
    settings = AppSettings(use_mock_oss=False)

    with pytest.raises(StorageConfigError, match="Missing required OSS configuration"):
        create_storage_client(settings=settings)
