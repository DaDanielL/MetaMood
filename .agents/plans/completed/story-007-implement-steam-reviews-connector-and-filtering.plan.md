# Plan: Implement Steam Reviews Connector and Filtering

## Summary

Add a Steam Reviews connector that fetches review pages with cursor pagination, enforces configured page and review limits, preserves raw page payloads for later OSS storage, normalizes public review records into strict `FeedbackItem` values, deduplicates by Steam recommendation ID, and filters normalized feedback to post-patch items. The implementation should mirror the existing Steam News connector style: injectable HTTP behavior, sanitized connector errors, small pure parsing/normalization helpers, and fixture-based tests that never call live Steam.

## User Story

As a live-ops producer, I want MetaMood to fetch recent reviews after a detected patch date, so that the analysis focuses on post-patch player response.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | Steam ingestion connector, shared connector exports, test fixtures |
| GitHub Issue | #3, https://github.com/DaDanielL/MetaMood/issues/3 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-007` |

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:159
Use snake_case for Python modules, functions, variables, and config keys. Use explicit IDs such as game_id and patch_event_id.
```

Create `app/connectors/steam_reviews.py` with names that parallel the existing connector: `SteamReviewsError`, `SteamReviewsResponse`, `SteamReviewsHttpClient`, `fetch_review_pages`, `normalize_review_to_feedback_item`, and `filter_feedback_after_patch`.

### External Boundary

```text
SOURCE: AGENTS.md:95
Prefer explicit adapters at every external boundary. Steam connectors fetch and normalize public data.
```

Keep Steam API access in `app/connectors/`, not in FastAPI routes or Streamlit. Do not add endpoint orchestration in this story.

### Error Handling

```text
SOURCE: app/connectors/steam_news.py:61
The Steam News connector wraps HTTP failures in a connector-specific RuntimeError and avoids exposing full request URLs.
```

Use `SteamReviewsError` with messages that include endpoint type and status code where useful, but not sensitive or overly specific URLs. Raise `ValueError` for invalid local arguments or malformed individual review records during direct normalization.

### Payload Validation

```text
SOURCE: app/connectors/steam_news.py:239
The connector checks response status, JSON decoding, and expected payload container types before returning copied dictionaries.
```

Validate Steam Reviews response shape: top-level mapping, `reviews` list, and optional `cursor` string. Preserve each raw page payload as a copied dictionary for later storage.

### Type Contracts

```text
SOURCE: app/schemas.py:72
FeedbackItem requires game_id, source, external_id, text, created_at_source, and optional review metadata.
```

Normalize Steam fields into `FeedbackItem`: `recommendationid` -> `external_id`, `review` -> `text`, `timestamp_created` -> UTC `created_at_source`, `voted_up` -> `positive`, `votes_up` -> `helpful_votes`, `author.playtime_forever` minutes -> `playtime_hours`, and `language` -> `language`.

### Storage Boundary

```text
SOURCE: app/storage/keys.py:15
raw_steam_reviews_key already defines the required OSS path for raw review pages.
```

This story should preserve raw page payloads in connector return values. Actual OSS uploads and attaching `raw_oss_key` to persisted records belong to STORY-008.

### Tests

```text
SOURCE: tests/test_steam_news_connector.py:26
Connector tests use fake responses and fake HTTP clients, then assert request params, parsed output, and sanitized failures.
```

Add fixture-driven tests with fake HTTP clients. Do not call live Steam endpoints.

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `app/connectors/steam_reviews.py` | CREATE | Implement Steam Reviews fetching, cursor pagination, raw page preservation, deduplication, normalization, and timestamp filtering helpers. |
| `app/connectors/__init__.py` | UPDATE | Re-export the Steam Reviews connector constants, protocols, errors, and helper functions. |
| `tests/fixtures/steam_reviews_page_1.json` | CREATE | Provide first raw Steam Reviews fixture with cursor and mixed pre/post-patch reviews. |
| `tests/fixtures/steam_reviews_page_2.json` | CREATE | Provide second raw Steam Reviews fixture with next cursor behavior and duplicate review coverage. |
| `tests/test_steam_reviews_connector.py` | CREATE | Cover pagination, limits, raw page preservation, deduplication, normalization, timestamp filtering, and error handling. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add Steam Reviews Connector Skeleton

- **File**: `app/connectors/steam_reviews.py`
- **Action**: CREATE
- **Implement**:
  - Define `STEAM_REVIEWS_ENDPOINT_TEMPLATE = "https://store.steampowered.com/appreviews/{steam_appid}"`.
  - Define `STEAM_REVIEWS_SOURCE = "steam_reviews"`.
  - Define `SteamReviewsError`, `SteamReviewsResponse`, and `SteamReviewsHttpClient` protocols mirroring the Steam News connector.
  - Define a small immutable `SteamReviewPage` dataclass with `page_number`, `cursor`, `next_cursor`, `payload`, and `reviews`.
- **Mirror**: `app/connectors/steam_news.py:42` - connector-specific error and protocol pattern.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 2: Implement Page Fetching and Cursor Pagination

- **File**: `app/connectors/steam_reviews.py`
- **Action**: UPDATE
- **Implement**:
  - Add `fetch_review_pages(...) -> list[SteamReviewPage]`.
  - Accept `steam_appid`, `language`, `review_type`, `review_filter`, `max_pages`, `num_per_page`, `max_reviews`, `cursor="*"`, injectable `http_client`, and `timeout_seconds`.
  - Validate positive `max_pages`, `num_per_page`, and `max_reviews`; cap `num_per_page` at Steam's documented 100 page size.
  - Build params with `json=1`, `filter`, `language`, `review_type`, `num_per_page`, and `cursor`.
  - Stop when any limit is reached, a page returns no reviews, or the next cursor is missing/unchanged.
  - Preserve full raw payload dictionaries on each `SteamReviewPage`.
- **Mirror**: `app/connectors/steam_news.py:71` - injected client path, default `httpx.Client`, and request parameter assertions.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 3: Implement Payload Extraction and Sanitized Failures

- **File**: `app/connectors/steam_reviews.py`
- **Action**: UPDATE
- **Implement**:
  - Add private helpers for request execution and response extraction.
  - Raise `SteamReviewsError` for HTTP exceptions, non-2xx status codes, invalid JSON, and malformed page payloads.
  - Include `steam_reviews` and status code in status failures; avoid including full endpoint URLs.
  - Copy page payloads and review mappings so callers can safely inspect them.
- **Mirror**: `app/connectors/steam_news.py:239` - status, JSON, and malformed payload handling.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 4: Normalize Steam Reviews into FeedbackItem

- **File**: `app/connectors/steam_reviews.py`
- **Action**: UPDATE
- **Implement**:
  - Add `parse_steam_review_datetime(value: object) -> datetime`, following the UTC epoch parsing behavior from Steam News.
  - Add `normalize_review_to_feedback_item(game_id, review, *, patch_event_id=None, raw_oss_key=None) -> FeedbackItem`.
  - Require non-empty `recommendationid` and `review` text.
  - Convert `timestamp_created` to timezone-aware UTC.
  - Map `voted_up`, `votes_up`, `language`, and `author.playtime_forever` minutes to schema fields.
  - Leave `url` as `None` unless Steam provides a direct review URL; do not construct profile URLs from `steamid`.
- **Mirror**: `app/connectors/steam_news.py:186` - normalize raw Steam mapping through Pydantic model validation.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 5: Add Deduplication and Post-Patch Filtering Helpers

- **File**: `app/connectors/steam_reviews.py`
- **Action**: UPDATE
- **Implement**:
  - Add `deduplicate_review_payloads(reviews)` or equivalent helper that keeps the first review for each non-empty `recommendationid`.
  - Add `filter_feedback_after_patch(feedback_items, patch_published_at)` using UTC-aware comparison and including reviews created at or after the patch timestamp.
  - Add a high-level helper such as `fetch_post_patch_feedback(...) -> SteamReviewsFetchResult` that returns raw pages plus normalized, deduplicated, post-patch `FeedbackItem` values.
  - Keep source order stable across pages.
- **Mirror**: `AGENTS.md:181` - deduplicate Steam records by source and external ID.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 6: Export the Connector Boundary

- **File**: `app/connectors/__init__.py`
- **Action**: UPDATE
- **Implement**:
  - Re-export `STEAM_REVIEWS_ENDPOINT_TEMPLATE`, `STEAM_REVIEWS_SOURCE`, `SteamReviewsError`, response/client protocols, page/result dataclasses, and public helper functions.
  - Keep the existing Steam News exports unchanged.
- **Mirror**: `app/connectors/__init__.py:3` - package-level connector re-export style.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 7: Add Steam Reviews Fixtures

- **File**: `tests/fixtures/steam_reviews_page_1.json`
- **Action**: CREATE
- **Implement**:
  - Include a realistic Steam Reviews payload with `cursor`, `reviews`, `recommendationid`, `review`, `timestamp_created`, `voted_up`, `votes_up`, `language`, and nested `author.playtime_forever`.
  - Include both pre-patch and post-patch timestamps.
- **Mirror**: `tests/fixtures/steam_news_recent.json` - local raw API fixture style.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 8: Add Second Fixture for Pagination and Deduplication

- **File**: `tests/fixtures/steam_reviews_page_2.json`
- **Action**: CREATE
- **Implement**:
  - Include a second payload with a different cursor and at least one duplicate `recommendationid` from page 1.
  - Include at least one additional valid post-patch review.
  - Optionally include an empty cursor or repeated cursor scenario in tests through inline fake payloads instead of fixture churn.
- **Mirror**: `tests/test_steam_news_connector.py:57` - assert fake client calls and returned raw records.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

### Task 9: Add Connector Tests

- **File**: `tests/test_steam_reviews_connector.py`
- **Action**: CREATE
- **Implement**:
  - Add `FakeResponse`, sequential `FakeHttpClient`, and failing client classes.
  - Test first cursor is `*`, next cursor comes from page payload, and request params include configured language/filter/type/page size.
  - Test `max_pages`, `num_per_page`, and `max_reviews` limits.
  - Test raw page payloads are preserved.
  - Test deduplication by `recommendationid`.
  - Test normalization into `FeedbackItem`, including `playtime_forever / 60`.
  - Test post-patch filtering with pre-patch items excluded and exact patch timestamp included.
  - Test invalid JSON, malformed payloads, non-2xx status codes, request failures, invalid limits, and invalid review records.
- **Mirror**: `tests/test_steam_news_connector.py:53` - fake client tests for happy path and sanitized errors.
- **Validate**: `python -m pytest tests/test_steam_reviews_connector.py`

---

## Risks

| Risk | Mitigation |
|------|------------|
| Steam cursor can repeat or be missing, causing accidental loops. | Stop pagination when `next_cursor` is missing, empty, or unchanged; always enforce `max_pages`. |
| Review payload fields may be absent or typed unexpectedly. | Validate direct normalization strictly and keep malformed-page errors sanitized; tests should cover missing required fields. |
| Deduplication can reorder player feedback. | Use an insertion-ordered `dict`/set pass that preserves first-seen order across pages. |
| Constructing profile URLs from `steamid` could expose user identity unnecessarily. | Do not synthesize profile URLs; keep `url=None` unless Steam provides a direct review URL. |
| STORY-007 overlaps with STORY-008 persistence requirements. | Return raw page payloads and optional `raw_oss_key` hooks, but do not upload to OSS or write RDS records in this story. |

---

## Validation

Run focused tests while implementing, then the full suite:

```bash
python -m pytest tests/test_steam_reviews_connector.py
python -m pytest
```

## End-to-End Verification

- [ ] Fake two-page Steam Reviews response fetch returns two preserved raw page payloads.
- [ ] Normalized feedback contains only unique `steam_reviews` `FeedbackItem` records.
- [ ] Pre-patch reviews are excluded from the high-level post-patch result.
- [ ] No test performs a live Steam, OSS, RDS, Qwen, or Bailian call.

## Acceptance Criteria

- [ ] All planned tasks completed
- [ ] Relevant tests added or updated
- [ ] Validation commands pass
- [ ] End-to-end verification passes
- [ ] Implementation follows `AGENTS.md`
