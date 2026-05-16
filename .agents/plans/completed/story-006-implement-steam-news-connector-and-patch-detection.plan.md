# Plan: Implement Steam News Connector and Patch Detection

## Summary

Add the first Steam ingestion connector under `app/connectors/` so MetaMood can fetch recent Steam News posts for a configured app ID, identify likely patch/update posts with the PRD keyword rules, select the newest matching post, clean Steam HTML/BBCode-like content, and normalize the result into the existing strict `PatchEvent` schema. The implementation should keep live HTTP behavior injectable and isolated from parsing/normalization so default tests use fixtures and never call Steam.

## User Story

As a live-ops producer, I want MetaMood to detect the latest Steam update for a selected game, so that analysis starts from the correct patch context.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | `app/connectors`, `app/schemas`, tests, fixtures |
| GitHub Issue | #7, https://github.com/DaDanielL/MetaMood/issues/7 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-006` |
| Branch At Planning | `main` |
| Working Tree At Planning | Clean |

---

## Feature Understanding

- **Problem**: Downstream review ingestion and analysis need a reliable detected patch event before they can collect post-patch feedback or generate patch-linked reasoning.
- **Story Scope**: Implement Steam News fetching, patch keyword detection, newest patch selection, content cleanup, date parsing, and `PatchEvent` normalization.
- **Out of Scope**: Do not persist patch events to RDS or upload raw/cleaned artifacts to OSS in this story. PRD section 7.2 mentions storage, but issue #7 and `STORY-006` narrow this pass to connector and normalization behavior; later ingestion orchestration can use existing storage and DB layers.
- **Primary Constraint**: Default tests must use fixtures and fake HTTP clients only. No live Steam calls.

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:155
Use snake_case for Python modules, functions, variables, and config keys. Use explicit IDs like game_id, patch_event_id, analysis_run_id, and report_id.
```

```text
SOURCE: AGENTS.md:164
External ingestion belongs in app/connectors/. Keep route, storage, and DB behavior out of the connector module.
```

```text
SOURCE: app/connectors/__init__.py:1
The package currently marks the external ingestion connector boundary and is the right place to export the Steam News connector surface.
```

### Contracts

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:331
Steam News input parameters are steam_appid, count, maxlength, and optional enddate. The connector must fetch recent posts and detect likely patch/update posts.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:342
PATCH_KEYWORDS must include patch, hotfix, update, balance, release notes, maintenance, season, major update, minor update, and bug fix.
```

```text
SOURCE: app/schemas.py:42
SchemaBase forbids extra fields and strips strings, so normalized connector output should be validated through PatchEvent instead of returning loose dicts.
```

```text
SOURCE: app/schemas.py:58
PatchEvent requires game_id, external_id, source, title, published_at, and content, with optional URL and future OSS key fields.
```

### Error Handling

```text
SOURCE: AGENTS.md:199
Steam errors should include endpoint type and status code, not sensitive URLs.
```

```text
SOURCE: app/config.py:21
Use small domain-specific RuntimeError subclasses with concise messages when boundary operations fail.
```

```text
SOURCE: app/api/routes_games.py:14
Boundary code catches domain errors and translates them at the outer layer. The connector should raise connector errors, not HTTPException.
```

### Tests

```text
SOURCE: .agents/stories/metamood-mvp.stories.md:287
Default tests must use fixtures and make no live Steam calls. Keep network and normalization logic separable for testability.
```

```text
SOURCE: tests/test_storage_oss_client.py:20
Use in-memory fake clients and focused assertions for external-boundary behavior.
```

```text
SOURCE: tests/test_storage_keys.py:19
Use deterministic fixtures and date assertions for generated artifact/path behavior.
```

```text
SOURCE: tests/test_schemas.py:19
Validate domain examples through Pydantic models and assert parsed datetime fields are real datetime objects.
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `app/connectors/steam_news.py` | CREATE | Implement Steam News HTTP boundary, patch detection, content cleanup, date parsing, newest-post selection, and `PatchEvent` normalization. |
| `app/connectors/__init__.py` | UPDATE | Export the public Steam News connector types/functions for later services. |
| `tests/fixtures/steam_news_recent.json` | CREATE | Provide representative Steam News API response data with patch and non-patch posts. |
| `tests/test_steam_news_connector.py` | CREATE | Cover fake HTTP fetching, error handling, keyword detection, newest selection, date parsing, cleanup, and `PatchEvent` normalization. |

No dependency, API route, database model, migration, OSS client, or Streamlit changes are expected.

---

## Design Notes

### Connector API

Create `app/connectors/steam_news.py` with a small sync API compatible with `httpx.Client` and simple fake clients:

- `PATCH_KEYWORDS: tuple[str, ...]`
- `STEAM_NEWS_ENDPOINT = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"`
- `SteamNewsError(RuntimeError)`
- `SteamNewsResponse(Protocol)` with `status_code` and `json()`
- `SteamNewsHttpClient(Protocol)` with `get(url, params=..., timeout=...)`
- `fetch_recent_news(steam_appid, count=20, maxlength=0, enddate=None, http_client=None, timeout_seconds=30.0) -> list[dict[str, Any]]`
- `is_patch_news_post(news_item) -> bool`
- `select_latest_patch_post(news_items) -> dict[str, Any] | None`
- `parse_steam_news_datetime(value) -> datetime`
- `clean_news_content(content) -> str`
- `normalize_news_item_to_patch_event(game_id, news_item, raw_oss_key=None, cleaned_text_oss_key=None) -> PatchEvent`
- `detect_latest_patch_event(game, count=20, maxlength=0, enddate=None, http_client=None) -> PatchEvent | None`

Use `GameConfig` or a plain `game_id`/`steam_appid` pair at the public boundary only if necessary. Prefer accepting `GameConfig` for the high-level helper because it already carries `game_id` and `steam_appid`.

### Fetching Behavior

- Use `httpx.Client` internally only when `http_client` is not supplied.
- Query `appid`, `count`, `maxlength`, and optional `enddate`.
- Require `count` to be positive and default to `20`, satisfying the PRD requirement to fetch the most recent 10-20 posts.
- Interpret non-2xx responses as `SteamNewsError("Steam News API failed for endpoint steam_news with status code {status_code}.")`.
- Wrap malformed JSON or missing `appnews.newsitems` as `SteamNewsError` with endpoint context and no raw URL.
- Do not store raw responses or cleaned text in this connector; leave optional OSS key fields as arguments for future orchestration.

### Patch Detection and Selection

- Search title and content together, case-insensitively, using the exact PRD keyword list.
- Return `False` for missing title/content or non-mapping items.
- Select the newest matching post by parsed `date`, not by API order.
- Ignore or reject items with missing/invalid dates consistently. Recommended: `select_latest_patch_post` should skip invalid-dated matches, while `normalize_news_item_to_patch_event` should raise `ValueError` for invalid selected items so tests can pinpoint bad normalization input.

### Date Parsing

- Steam News usually returns epoch seconds in `date`.
- Accept `int`, `float`, and numeric strings.
- Return timezone-aware UTC `datetime`.
- Reject empty, negative, non-numeric, or otherwise invalid values with `ValueError`.

### Content Cleaning

- Use standard-library parsing helpers: `html.unescape`, regex for BBCode tags, and `html.parser` or conservative tag stripping for HTML.
- Convert common separators (`<br>`, paragraph/list endings, BBCode list markers) into readable whitespace/newlines before final normalization.
- Remove tags like `[b]`, `[/b]`, `[url=...]`, `[/url]`, `[list]`, `[/list]`, and `[*]` while preserving the visible text.
- Collapse repeated spaces and blank lines. The output should be readable plain text and non-empty when source content has visible text.

### Normalization

Map Steam fields into `PatchEvent`:

- `game_id`: configured game ID
- `external_id`: Steam `gid` when present, otherwise a stable string form of `id`
- `source`: `"steam_news"`
- `title`: Steam `title`
- `published_at`: parsed `date`
- `url`: Steam `url` when provided
- `content`: cleaned `contents`
- `raw_oss_key`: optional passthrough
- `cleaned_text_oss_key`: optional passthrough

Validate by constructing `PatchEvent.model_validate(...)` or `PatchEvent(...)`.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Tests accidentally make live Steam calls. | Require injectable `http_client`; tests use fake clients and fixture JSON only. Do not instantiate the default `httpx.Client` in tests. |
| Steam payload shape differs from fixtures. | Keep payload extraction defensive and raise `SteamNewsError` when `appnews.newsitems` is absent or not a list. |
| Keyword matching creates false positives. | Keep the MVP PRD keyword list deterministic and transparent; later stories can refine scoring if needed. |
| HTML/BBCode cleanup removes meaningful patch text. | Preserve visible text first, strip markup second, and add tests for links, bold tags, line breaks, and list markers. |
| Invalid dates crash latest-selection unexpectedly. | Add dedicated date parsing tests and define skip-vs-raise behavior separately for selection and normalization. |
| Story scope creeps into persistence. | Do not update `app/storage`, `app/db`, API routes, or services in this plan. Future orchestration stories can combine connector output with OSS/RDS. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add Fixture Data

- **File**: `tests/fixtures/steam_news_recent.json`
- **Action**: CREATE
- **Implement**: Add a compact Steam News-like JSON response with at least four items: newest non-patch community post, older patch post, newest patch/hotfix/update post, and non-patch announcement. Include `gid`, `title`, `url`, `date`, and `contents` with HTML/BBCode-like markup.
- **Mirror**: `.agents/stories/metamood-mvp.stories.md:287` - fixture-backed tests only, no live Steam calls.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 2: Create Connector Error and HTTP Fetch Boundary

- **File**: `app/connectors/steam_news.py`
- **Action**: CREATE
- **Implement**: Add endpoint constants, `SteamNewsError`, minimal response/client protocols, and `fetch_recent_news()` with positive-count validation, optional `enddate`, injectable client support, `httpx.Client` fallback, response status handling, JSON parsing, and `appnews.newsitems` extraction.
- **Mirror**: `app/storage/oss_client.py:44` - protocol-based external boundary with a real implementation hidden behind a small public surface.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 3: Implement Date Parsing and Patch Keyword Detection

- **File**: `app/connectors/steam_news.py`
- **Action**: UPDATE
- **Implement**: Add `PATCH_KEYWORDS`, `parse_steam_news_datetime()`, and `is_patch_news_post()`. Match title plus content case-insensitively against the PRD keywords and return timezone-aware UTC datetimes.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:342` - exact keyword list.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 4: Implement Latest Patch Selection

- **File**: `app/connectors/steam_news.py`
- **Action**: UPDATE
- **Implement**: Add `select_latest_patch_post()` that filters with `is_patch_news_post()`, parses dates, skips invalid-dated matches, and returns the newest matching mapping or `None` when no match exists.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:359` - newest matching post selection.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 5: Implement Content Cleanup

- **File**: `app/connectors/steam_news.py`
- **Action**: UPDATE
- **Implement**: Add `clean_news_content()` using standard-library HTML unescaping and conservative HTML/BBCode stripping. Preserve readable visible text, line breaks, list item separation, and link text.
- **Mirror**: `.agents/stories/metamood-mvp.stories.md:278` - clean HTML/BBCode-like content into readable plain text.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 6: Normalize to PatchEvent

- **File**: `app/connectors/steam_news.py`
- **Action**: UPDATE
- **Implement**: Add `normalize_news_item_to_patch_event()` and `detect_latest_patch_event()`. Map Steam fields into `PatchEvent`, set source to `"steam_news"`, use cleaned contents, parse `date`, and support optional `raw_oss_key` and `cleaned_text_oss_key` passthroughs.
- **Mirror**: `app/schemas.py:58` - strict `PatchEvent` contract.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 7: Export Connector Surface

- **File**: `app/connectors/__init__.py`
- **Action**: UPDATE
- **Implement**: Export the connector error, keyword list, and public helper functions needed by future services. Keep exports explicit with `__all__`.
- **Mirror**: `app/storage/__init__.py:1` - package boundary exports for adapter modules.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 8: Add Connector Tests

- **File**: `tests/test_steam_news_connector.py`
- **Action**: CREATE
- **Implement**: Add tests for fixture-backed fetch behavior, non-2xx errors, malformed payloads, keyword matching, newest selection by date, no-match behavior, date parsing, content cleanup, normalization into `PatchEvent`, optional OSS key passthrough, and the high-level `detect_latest_patch_event()` helper using a fake HTTP client.
- **Mirror**: `tests/test_storage_oss_client.py:20` - fake external client and direct metadata assertions.
- **Validate**: `python -m pytest tests/test_steam_news_connector.py`

### Task 9: Run Full Validation

- **File**: N/A
- **Action**: VERIFY
- **Implement**: Run the full test suite to ensure existing health, game config, schema, storage, and DB behavior is unchanged.
- **Mirror**: `AGENTS.md:235` - default tests must not call live external services.
- **Validate**: `python -m pytest`

---

## Validation

Use the project commands documented in `AGENTS.md` and `README.md`:

```bash
python -m pytest tests/test_steam_news_connector.py
python -m pytest
```

There is currently no configured lint, typecheck, or build command.

## End-to-End Verification

- [ ] Run `python -m pytest tests/test_steam_news_connector.py` and confirm all Steam News connector tests pass without network access.
- [ ] Run `python -m pytest` and confirm the existing API/config/schema/storage/DB tests still pass.
- [ ] Confirm `detect_latest_patch_event()` returns a `PatchEvent` whose title and `external_id` match the newest patch-like fixture post, not the newest non-patch post.
- [ ] Confirm cleaned patch content contains visible patch-note text and no HTML or BBCode tags.

## Acceptance Criteria

- [ ] Fetch recent Steam News posts for a configured app ID using injectable HTTP client behavior.
- [ ] Detect likely patch/update posts using PRD keyword rules.
- [ ] Select the newest matching post.
- [ ] Normalize the result into `PatchEvent`.
- [ ] Clean HTML/BBCode-like content into readable plain text.
- [ ] Add fixture-based tests for detection, normalization, and date parsing.
- [ ] Default validation makes no live Steam, Qwen, OSS, RDS, or Bailian calls.
- [ ] Implementation follows `AGENTS.md`.
