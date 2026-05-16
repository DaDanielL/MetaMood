# Plan: Implement OSS Storage Client and Object Key Helpers

## Summary

Add the MetaMood storage foundation for Alibaba Cloud OSS by creating deterministic object key builders, a storage client abstraction, an Alibaba OSS-backed implementation, and an in-memory mock client for tests and local development. The implementation should keep all live OSS behavior behind `app/storage/`, read configuration from existing `AppSettings`, return object keys for later RDS persistence, and cover key generation plus mock uploads with default tests that make no live network calls.

## User Story

As a developer, I want an OSS storage adapter and deterministic object key helpers, so that MetaMood can store raw data, processed patch docs, generated reports, and future dataset exports.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | `app/storage`, configuration, dependencies, tests |
| GitHub Issue | #4, https://github.com/DaDanielL/MetaMood/issues/4 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-005` |

---

## Feature Understanding

- **Problem**: Downstream Steam ingestion, RAG document processing, report generation, and future fine-tuning exports need deterministic OSS locations and a mockable upload boundary before they can persist artifacts safely.
- **Story Scope**: Add storage helpers and clients only. Do not wire Steam ingestion, analysis services, report generation, Streamlit, or database repositories in this story.
- **Primary Constraint**: Default tests must not call live OSS or require Alibaba credentials.

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:155
Use snake_case for Python modules, functions, variables, and config keys. Use explicit IDs like game_id, patch_event_id, analysis_run_id, and report_id.
```

```text
SOURCE: AGENTS.md:164
Keep storage-specific code in app/storage/. Do not place OSS behavior in API routes, services, or database modules.
```

```text
SOURCE: app/config.py:25
AppSettings is a Pydantic BaseModel with snake_case fields and defaults derived from environment variables in load_app_settings().
```

### Object Key Contracts

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:401
Required keys:
raw/steam_news/{game_id}/{patch_id}/{timestamp}.json
raw/steam_reviews/{game_id}/{patch_id}/page_{page_number}_{timestamp}.json
processed/patch_notes/{game_id}/{patch_id}/patch_notes.txt
processed/rag_docs/{game_id}/{patch_id}/{document_name}.txt
reports/{game_id}/{patch_id}/live_ops_brief.md
reports/{game_id}/{patch_id}/action_board.json
reports/{game_id}/{patch_id}/community_response.md
exports/fine_tuning/{game_id}/{patch_id}/classification_dataset.jsonl
```

```text
SOURCE: app/schemas.py:58
PatchEvent, FeedbackItem, and LiveOpsReport already expose OSS key fields that future persistence code will fill.
```

### Error Handling

```text
SOURCE: app/config.py:21
Define domain-specific RuntimeError subclasses for configuration failures, and wrap low-level validation or IO failures with actionable messages.
```

```text
SOURCE: AGENTS.md:199
OSS failures should mark analysis as partial failure later; for this story, storage clients should raise clear storage errors without logging credentials.
```

### Tests

```text
SOURCE: tests/test_config.py:71
Use pytest monkeypatch for environment-driven settings tests and explicitly clear credential variables when verifying safe defaults.
```

```text
SOURCE: tests/test_db_session.py:16
Test factory functions by overriding settings through environment variables rather than relying on live infrastructure.
```

```text
SOURCE: tests/test_schemas.py:136
Favor focused assertions that validate rejection of unsafe or unexpected inputs.
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | UPDATE | Add Alibaba Cloud OSS SDK dependency for the real OSS client wrapper. |
| `app/storage/keys.py` | CREATE | Provide deterministic object key builders and object-key segment validation. |
| `app/storage/oss_client.py` | CREATE | Define storage errors, upload result type, client protocol, Alibaba OSS client, mock client, upload helpers, and a factory. |
| `app/storage/__init__.py` | UPDATE | Export storage clients, errors, upload result type, and key builder functions. |
| `tests/test_storage_keys.py` | CREATE | Cover all required object key builders, timestamp normalization, page number validation, and unsafe segment rejection. |
| `tests/test_storage_oss_client.py` | CREATE | Cover mock uploads, JSON/text/Markdown/JSONL serialization, factory behavior, and live-client configuration validation without network calls. |

No database migrations or API route changes are expected for this story.

---

## Design Notes

### Object Key Builders

Create `app/storage/keys.py` with small single-purpose functions:

- `raw_steam_news_key(game_id, patch_id, timestamp)`
- `raw_steam_reviews_key(game_id, patch_id, page_number, timestamp)`
- `processed_patch_notes_key(game_id, patch_id)`
- `processed_rag_doc_key(game_id, patch_id, document_name)`
- `live_ops_brief_key(game_id, patch_id)`
- `action_board_key(game_id, patch_id)`
- `community_response_key(game_id, patch_id)`
- `fine_tuning_classification_dataset_key(game_id, patch_id)`

Implement helper behavior:

- Normalize `datetime` timestamps to UTC, compact and filesystem-safe, such as `20260115T120000Z`.
- Accept already-normalized timestamp strings only if non-empty and path-safe.
- Validate path segments as non-empty strings with no `/`, `\`, `..`, or leading/trailing whitespace.
- Validate `page_number >= 1`.
- For RAG docs, accept a logical `document_name` without `.txt` and append `.txt`; if `.txt` is already supplied, avoid double extension.

### Storage Client

Create `app/storage/oss_client.py` with:

- `StorageError(RuntimeError)` for upload failures.
- `StorageConfigError(StorageError)` for missing config or missing SDK dependency.
- `UploadedObject` dataclass with `key`, `content_type`, and `size_bytes`.
- `StorageClient` protocol with `upload_bytes(object_key, data, content_type) -> UploadedObject`.
- `AlibabaOssStorageClient` that reads `oss_endpoint`, `oss_bucket_name`, `alibaba_cloud_access_key_id`, and `alibaba_cloud_access_key_secret` from `AppSettings` unless explicit values are passed.
- `MockOssStorageClient` storing uploaded objects in memory for tests and development.
- `create_storage_client(settings=None)` returning `MockOssStorageClient` when `settings.use_mock_oss` is true, otherwise `AlibabaOssStorageClient`.

Upload helper methods should live on a shared base/mixin or be implemented consistently on the protocol-facing classes:

- `upload_json(object_key, payload)`
- `upload_text(object_key, text)`
- `upload_markdown(object_key, markdown)`
- `upload_jsonl(object_key, rows)`

Serialization rules:

- Encode text as UTF-8 bytes.
- Use deterministic JSON with `sort_keys=True`.
- JSONL should write one compact JSON object per row and end with a newline when rows are present.
- Use explicit content types: `application/json`, `text/plain; charset=utf-8`, `text/markdown; charset=utf-8`, and `application/x-ndjson`.

### Dependency Approach

Add the Alibaba Cloud OSS Python SDK package to `requirements.txt` as `oss2` with a conservative bounded range. Import it lazily inside `AlibabaOssStorageClient` so tests can import `app.storage` without making live calls or requiring credentials at import time.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Default test suite accidentally touches live OSS. | Keep all live SDK construction behind explicit `AlibabaOssStorageClient` initialization and test only mock/factory behavior with `USE_MOCK_OSS=true` or missing config checks. |
| Secrets leak through exceptions or repr output. | Error messages should name missing setting names, not values. Do not include access key values, bucket credentials, or signed URLs. |
| Object keys become inconsistent across stories. | Centralize all key builders in `app/storage/keys.py` and export them from `app/storage/__init__.py`. |
| Path traversal or slash-containing IDs create unexpected OSS hierarchy. | Validate each object key segment and reject unsafe values early. |
| SDK dependency import breaks local tests before install. | Use lazy import and make dependency absence a `StorageConfigError` only when constructing the real client. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add OSS SDK Dependency

- **File**: `requirements.txt`
- **Action**: UPDATE
- **Implement**: Add the Alibaba Cloud OSS Python SDK package (`oss2`) with a bounded version range consistent with the rest of the file.
- **Mirror**: `requirements.txt:1` - one dependency per line with lower and upper bounds.
- **Validate**: `python -m pytest`

### Task 2: Create Deterministic Object Key Builders

- **File**: `app/storage/keys.py`
- **Action**: CREATE
- **Implement**: Add the required key builder functions, timestamp formatter, page-number validation, and path-segment validation described in Design Notes.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:401` - exact required path prefixes and filenames.
- **Validate**: `python -m pytest tests/test_storage_keys.py`

### Task 3: Define Storage Types and Upload Helpers

- **File**: `app/storage/oss_client.py`
- **Action**: CREATE
- **Implement**: Add `StorageError`, `StorageConfigError`, `UploadedObject`, `StorageClient`, and shared helper behavior for JSON, text, Markdown, and JSONL uploads.
- **Mirror**: `app/config.py:21` - domain-specific runtime errors with concise messages.
- **Validate**: `python -m pytest tests/test_storage_oss_client.py`

### Task 4: Implement the Alibaba OSS Client Wrapper

- **File**: `app/storage/oss_client.py`
- **Action**: UPDATE
- **Implement**: Add `AlibabaOssStorageClient` that reads from `load_app_settings()` by default, validates required OSS settings, lazily imports `oss2`, constructs an OSS bucket client, uploads bytes with metadata/content type, catches SDK exceptions, and raises `StorageError` without exposing secrets.
- **Mirror**: `app/db/session.py:17` - factory-style helpers read explicit arguments first and fall back to `load_app_settings()`.
- **Validate**: `python -m pytest tests/test_storage_oss_client.py`

### Task 5: Implement the Mock OSS Client

- **File**: `app/storage/oss_client.py`
- **Action**: UPDATE
- **Implement**: Add `MockOssStorageClient` with in-memory object storage keyed by object key. Store bytes, content type, and size; return `UploadedObject` from every upload.
- **Mirror**: `tests/test_db_session.py:16` - keep infrastructure tests local and deterministic.
- **Validate**: `python -m pytest tests/test_storage_oss_client.py`

### Task 6: Add Storage Client Factory

- **File**: `app/storage/oss_client.py`
- **Action**: UPDATE
- **Implement**: Add `create_storage_client(settings=None)` that returns the mock client when `use_mock_oss` is true, otherwise returns the real Alibaba client. Ensure this factory does not log or print config values.
- **Mirror**: `app/config.py:65` - settings are loaded once through `load_app_settings()` when no explicit settings are supplied.
- **Validate**: `python -m pytest tests/test_storage_oss_client.py`

### Task 7: Export Storage API

- **File**: `app/storage/__init__.py`
- **Action**: UPDATE
- **Implement**: Export the key builders, client classes, error classes, `UploadedObject`, and `create_storage_client` through `__all__`.
- **Mirror**: `app/__init__.py:6` - explicit `__all__` exports for public package names.
- **Validate**: `python -m pytest tests/test_storage_keys.py tests/test_storage_oss_client.py`

### Task 8: Add Object Key Tests

- **File**: `tests/test_storage_keys.py`
- **Action**: CREATE
- **Implement**: Test every PRD-required key shape, UTC timestamp normalization, page number rejection, unsafe segment rejection, and `.txt` handling for RAG document names.
- **Mirror**: `tests/test_schemas.py:73` - use pytest parametrization for invalid values.
- **Validate**: `python -m pytest tests/test_storage_keys.py`

### Task 9: Add Storage Client Tests

- **File**: `tests/test_storage_oss_client.py`
- **Action**: CREATE
- **Implement**: Test mock upload behavior for bytes, JSON, text, Markdown, and JSONL; assert content types and stored bytes; assert factory returns mock when `USE_MOCK_OSS=true`; assert missing real OSS config raises `StorageConfigError` without credential values.
- **Mirror**: `tests/test_config.py:71` - use `monkeypatch` to control environment-driven settings safely.
- **Validate**: `python -m pytest tests/test_storage_oss_client.py`

### Task 10: Run Full Validation

- **File**: N/A
- **Action**: VERIFY
- **Implement**: Run the full test suite and inspect git status for only expected files.
- **Mirror**: `AGENTS.md:230` - default tests must not call live external services.
- **Validate**: `python -m pytest`

---

## Validation

Run the focused checks during implementation, then the full suite:

```bash
python -m pytest tests/test_storage_keys.py
python -m pytest tests/test_storage_oss_client.py
python -m pytest
```

No lint, typecheck, or build command is currently configured.

## End-to-End Verification

- [ ] With `USE_MOCK_OSS=true`, `create_storage_client()` returns `MockOssStorageClient`.
- [ ] Uploading JSON, text, Markdown, and JSONL through the mock client returns the requested object key and records expected bytes/content type in memory.
- [ ] Every key builder returns exactly the PRD-required path form for representative `game_id`, `patch_id`, timestamp, page number, and document name inputs.
- [ ] Constructing the real OSS client with missing config raises `StorageConfigError` and does not expose credential values.

## Acceptance Criteria

- [ ] Object key builders exist for raw Steam News, raw Steam Reviews, processed patch notes, RAG docs, reports, and fine-tuning exports.
- [ ] OSS client wrapper reads credentials and bucket config from environment-backed settings.
- [ ] Mock OSS client supports tests and development without live OSS calls.
- [ ] Upload helpers support JSON, text, Markdown, and JSONL content.
- [ ] Tests cover object key generation and mock uploads.
- [ ] Full `python -m pytest` passes.
- [ ] Implementation follows `AGENTS.md`.
