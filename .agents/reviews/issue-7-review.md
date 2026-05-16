# Code Review: Issue #7

**Scope**: Issue #7 / current branch changes for STORY-006 Steam News connector  
**Recommendation**: NEEDS WORK

## Summary

Reviewed the issue #7 implementation for Steam News fetching, patch detection, content cleanup, normalization, fixture tests, implementation report, and archived plan. The implementation matches the story shape well and the automated tests are passing, but one external-boundary error handling gap should be fixed before approval.

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

1. **`app/connectors/steam_news.py:83` and `app/connectors/steam_news.py:87`**
   - Error: HTTP request exceptions from either an injected client or the default `httpx.Client` are not converted into `SteamNewsError`.
   - Likely cause: `_extract_newsitems()` wraps response status and JSON/payload errors, but `http_client.get(...)` and `client.get(...)` are called outside a connector-level exception boundary.
   - Impact: Future services need to catch both `SteamNewsError` and arbitrary transport/client exceptions, and live Steam failures will not follow the project pattern that external boundary errors use small domain-specific error types with endpoint context.
   - Fix: Wrap request failures and raise `SteamNewsError("Steam News API request failed for endpoint steam_news.")` or similar, chaining the original exception. Add a fake-client test that raises a request exception and asserts `SteamNewsError`.

### Suggestions

1. **`app/connectors/steam_news.py:177`**
   - Consider rejecting missing or non-string `contents` in `normalize_news_item_to_patch_event()`, or requiring cleaned content to be non-empty. The normal detect path currently avoids this through `is_patch_news_post()`, but the public normalization helper can still create a `PatchEvent` with empty content when called directly.

## Validation Results

| Check | Status |
|-------|--------|
| Type Check | SKIPPED - no configured typecheck command |
| Syntax Check | PASS - `python -m py_compile app/connectors/steam_news.py tests/test_steam_news_connector.py` |
| Lint | SKIPPED - no configured lint command |
| Focused Tests | PASS - `python -m pytest tests/test_steam_news_connector.py` returned 34 passed |
| Tests | PASS - `python -m pytest` returned 91 passed |
| Build | SKIPPED - no configured build command |

## What's Good

- The connector keeps live HTTP behavior injectable and separates fetching, detection, selection, cleanup, and normalization cleanly.
- Patch keyword coverage mirrors the PRD list, and fixture-backed tests cover happy paths and malformed payloads without live Steam calls.
- The implementation stays within story scope by avoiding route, DB, OSS, and Streamlit changes.

## Recommendation

Fix the request-exception wrapping gap and add the matching test, then re-run the focused connector tests and full pytest suite.

---

# Code Review: Issue #7 Second Pass

**Scope**: Issue #7 / current branch changes for STORY-006 Steam News connector after request-error wrapping update  
**Recommendation**: APPROVE

## Summary

Reviewed the updated Steam News connector, connector exports, fixture data, and connector tests for issue #7. The earlier medium-priority concern has been addressed: request-time failures are now converted to `SteamNewsError` through `_get_news_response()`, and `tests/test_steam_news_connector.py` includes coverage for that path.

## Issues Found

### Critical

None.

### High Priority

None.

### Medium Priority

None.

### Suggestions

None blocking. The existing permissive behavior around empty cleaned `content` in `normalize_news_item_to_patch_event()` remains a product choice; it does not conflict with issue #7 acceptance criteria.

## Validation Results

| Check | Status |
|-------|--------|
| Type Check | SKIPPED - no configured typecheck command |
| Syntax Check | PASS - `python -m py_compile app/connectors/steam_news.py tests/test_steam_news_connector.py` |
| Lint | SKIPPED - no configured lint command |
| Focused Tests | PASS - `python -m pytest tests/test_steam_news_connector.py` returned 35 passed |
| Tests | PASS - `python -m pytest` returned 92 passed |
| Build | SKIPPED - no configured build command |

## What's Good

- Request failures, HTTP status failures, invalid JSON, and malformed payloads all now resolve through the connector-level `SteamNewsError` boundary.
- The connector remains scoped to Steam News fetching, deterministic patch detection, newest-post selection, cleanup, and `PatchEvent` normalization without adding DB, OSS, route, or Streamlit behavior.
- The tests are fixture-backed and cover the new transport failure case without live Steam calls.

## Recommendation

Approve the issue #7 implementation.
