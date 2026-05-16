"""OSS storage clients and upload helpers."""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, Protocol

from app.config import AppSettings, load_app_settings

CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_JSONL = "application/x-ndjson"
CONTENT_TYPE_MARKDOWN = "text/markdown; charset=utf-8"
CONTENT_TYPE_TEXT = "text/plain; charset=utf-8"


class StorageError(RuntimeError):
    """Raised when object storage operations fail."""


class StorageConfigError(StorageError):
    """Raised when object storage configuration is missing or invalid."""


@dataclass(frozen=True)
class UploadedObject:
    """Metadata returned after an object upload."""

    key: str
    content_type: str
    size_bytes: int


@dataclass(frozen=True)
class MockStoredObject:
    """In-memory object data held by the mock storage client."""

    data: bytes
    content_type: str
    size_bytes: int


class StorageClient(Protocol):
    """Protocol implemented by OSS-backed and mock storage clients."""

    def upload_bytes(self, object_key: str, data: bytes, content_type: str) -> UploadedObject:
        """Upload raw bytes to object storage."""

    def upload_json(self, object_key: str, payload: Any) -> UploadedObject:
        """Upload a JSON-serialized payload."""

    def upload_text(self, object_key: str, text: str) -> UploadedObject:
        """Upload plain UTF-8 text."""

    def upload_markdown(self, object_key: str, markdown: str) -> UploadedObject:
        """Upload UTF-8 Markdown."""

    def upload_jsonl(self, object_key: str, rows: Iterable[Any]) -> UploadedObject:
        """Upload newline-delimited JSON rows."""


class StorageUploadMixin:
    """Shared serialization helpers for storage clients."""

    def upload_json(self, object_key: str, payload: Any) -> UploadedObject:
        return self.upload_bytes(object_key, _json_bytes(payload), CONTENT_TYPE_JSON)

    def upload_text(self, object_key: str, text: str) -> UploadedObject:
        return self.upload_bytes(object_key, _text_bytes(text), CONTENT_TYPE_TEXT)

    def upload_markdown(self, object_key: str, markdown: str) -> UploadedObject:
        return self.upload_bytes(object_key, _text_bytes(markdown), CONTENT_TYPE_MARKDOWN)

    def upload_jsonl(self, object_key: str, rows: Iterable[Any]) -> UploadedObject:
        return self.upload_bytes(object_key, _jsonl_bytes(rows), CONTENT_TYPE_JSONL)


class AlibabaOssStorageClient(StorageUploadMixin):
    """Alibaba Cloud OSS-backed storage client."""

    def __init__(
        self,
        settings: AppSettings | None = None,
        *,
        endpoint: str | None = None,
        bucket_name: str | None = None,
        access_key_id: str | None = None,
        access_key_secret: str | None = None,
    ) -> None:
        settings = settings or load_app_settings()
        resolved_endpoint = endpoint if endpoint is not None else settings.oss_endpoint
        resolved_bucket_name = bucket_name if bucket_name is not None else settings.oss_bucket_name
        resolved_access_key_id = access_key_id if access_key_id is not None else settings.alibaba_cloud_access_key_id
        resolved_access_key_secret = (
            access_key_secret if access_key_secret is not None else settings.alibaba_cloud_access_key_secret
        )

        _validate_oss_config(
            endpoint=resolved_endpoint,
            bucket_name=resolved_bucket_name,
            access_key_id=resolved_access_key_id,
            access_key_secret=resolved_access_key_secret,
        )

        try:
            import oss2
        except ImportError as exc:
            raise StorageConfigError("Alibaba OSS SDK dependency 'oss2' is not installed.") from exc

        auth = oss2.Auth(resolved_access_key_id, resolved_access_key_secret)
        self._bucket = oss2.Bucket(auth, resolved_endpoint, resolved_bucket_name)

    def upload_bytes(self, object_key: str, data: bytes, content_type: str) -> UploadedObject:
        safe_key = _validate_object_key(object_key)
        payload = _validate_bytes(data)
        safe_content_type = _validate_content_type(content_type)
        try:
            self._bucket.put_object(safe_key, payload, headers={"Content-Type": safe_content_type})
        except Exception as exc:
            raise StorageError(f"Failed to upload object to OSS at key {safe_key!r}.") from exc
        return UploadedObject(key=safe_key, content_type=safe_content_type, size_bytes=len(payload))


class MockOssStorageClient(StorageUploadMixin):
    """In-memory storage client for tests and local development."""

    def __init__(self) -> None:
        self.objects: dict[str, MockStoredObject] = {}

    def upload_bytes(self, object_key: str, data: bytes, content_type: str) -> UploadedObject:
        safe_key = _validate_object_key(object_key)
        payload = _validate_bytes(data)
        safe_content_type = _validate_content_type(content_type)
        stored_object = MockStoredObject(data=payload, content_type=safe_content_type, size_bytes=len(payload))
        self.objects[safe_key] = stored_object
        return UploadedObject(key=safe_key, content_type=safe_content_type, size_bytes=stored_object.size_bytes)


def create_storage_client(settings: AppSettings | None = None) -> StorageClient:
    """Create the configured storage client."""
    resolved_settings = settings or load_app_settings()
    if resolved_settings.use_mock_oss:
        return MockOssStorageClient()
    return AlibabaOssStorageClient(settings=resolved_settings)


def _validate_oss_config(
    *,
    endpoint: str,
    bucket_name: str,
    access_key_id: str,
    access_key_secret: str,
) -> None:
    missing = []
    if not endpoint:
        missing.append("OSS_ENDPOINT")
    if not bucket_name:
        missing.append("OSS_BUCKET_NAME")
    if not access_key_id:
        missing.append("ALIBABA_CLOUD_ACCESS_KEY_ID")
    if not access_key_secret:
        missing.append("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    if missing:
        joined = ", ".join(missing)
        raise StorageConfigError(f"Missing required OSS configuration: {joined}.")


def _validate_object_key(value: str) -> str:
    if not isinstance(value, str):
        raise StorageError("object_key must be a string")
    if value == "":
        raise StorageError("object_key must not be empty")
    if value != value.strip():
        raise StorageError("object_key must not include leading or trailing whitespace")
    if "\\" in value:
        raise StorageError("object_key must not contain backslashes")
    if value.startswith("/"):
        raise StorageError("object_key must not start with a slash")
    return value


def _validate_bytes(value: bytes) -> bytes:
    if not isinstance(value, bytes):
        raise StorageError("data must be bytes")
    return value


def _validate_content_type(value: str) -> str:
    if not isinstance(value, str):
        raise StorageError("content_type must be a string")
    if value == "":
        raise StorageError("content_type must not be empty")
    if value != value.strip():
        raise StorageError("content_type must not include leading or trailing whitespace")
    return value


def _json_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _text_bytes(text: str) -> bytes:
    if not isinstance(text, str):
        raise StorageError("text content must be a string")
    return text.encode("utf-8")


def _jsonl_bytes(rows: Iterable[Any]) -> bytes:
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    if not lines:
        return b""
    return ("\n".join(lines) + "\n").encode("utf-8")
