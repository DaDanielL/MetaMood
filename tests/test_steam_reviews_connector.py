from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from app.connectors import (
    STEAM_REVIEWS_ENDPOINT_TEMPLATE,
    STEAM_REVIEWS_SOURCE,
    SteamReviewPage,
    SteamReviewsError,
    deduplicate_review_payloads,
    fetch_post_patch_feedback,
    fetch_review_pages,
    filter_feedback_after_patch,
    normalize_review_to_feedback_item,
    parse_steam_review_datetime,
)
from app.schemas import FeedbackItem

FIXTURE_DIR = Path(__file__).parent / "fixtures"
PATCH_PUBLISHED_AT = datetime(2026, 1, 18, 12, 0, tzinfo=timezone.utc)
VALID_REVIEW_PAYLOAD = {
    "recommendationid": "review-valid",
    "language": "english",
    "review": "A valid review payload.",
    "timestamp_created": 1768737600,
    "voted_up": True,
    "votes_up": 2,
    "author": {"steamid": "76561190000000006", "playtime_forever": 60},
}


class FakeResponse:
    def __init__(self, payload: Any = None, *, status_code: int = 200, json_error: Exception | None = None) -> None:
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self) -> Any:
        if self._json_error is not None:
            raise self._json_error
        return self._payload


class SequentialFakeHttpClient:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, *, params: dict[str, Any], timeout: float) -> FakeResponse:
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        if not self.responses:
            raise AssertionError("No fake response configured for request")
        return self.responses.pop(0)


class FailingHttpClient:
    def get(self, url: str, *, params: dict[str, Any], timeout: float) -> FakeResponse:
        raise TimeoutError("network timeout")


def test_fetch_review_pages_uses_cursor_pagination_and_preserves_raw_payloads() -> None:
    page_1 = _load_fixture("steam_reviews_page_1.json")
    page_2 = _load_fixture("steam_reviews_page_2.json")
    http_client = SequentialFakeHttpClient(FakeResponse(page_1), FakeResponse(page_2))

    pages = fetch_review_pages(
        553850,
        language="english",
        review_type="negative",
        review_filter="recent",
        max_pages=2,
        num_per_page=150,
        http_client=http_client,
    )

    assert len(pages) == 2
    assert all(isinstance(page, SteamReviewPage) for page in pages)
    assert pages[0].page_number == 1
    assert pages[0].cursor == "*"
    assert pages[0].next_cursor == "cursor-page-2"
    assert pages[1].page_number == 2
    assert pages[1].cursor == "cursor-page-2"
    assert pages[1].payload == page_2
    assert pages[0].payload is not page_1
    assert pages[0].reviews[0] is not page_1["reviews"][0]
    assert http_client.calls == [
        {
            "url": STEAM_REVIEWS_ENDPOINT_TEMPLATE.format(steam_appid=553850),
            "params": {
                "json": 1,
                "filter": "recent",
                "language": "english",
                "review_type": "negative",
                "num_per_page": 100,
                "cursor": "*",
            },
            "timeout": 30.0,
        },
        {
            "url": STEAM_REVIEWS_ENDPOINT_TEMPLATE.format(steam_appid=553850),
            "params": {
                "json": 1,
                "filter": "recent",
                "language": "english",
                "review_type": "negative",
                "num_per_page": 100,
                "cursor": "cursor-page-2",
            },
            "timeout": 30.0,
        },
    ]


def test_fetch_review_pages_respects_max_pages() -> None:
    http_client = SequentialFakeHttpClient(
        FakeResponse(_load_fixture("steam_reviews_page_1.json")),
        FakeResponse(_load_fixture("steam_reviews_page_2.json")),
    )

    pages = fetch_review_pages(553850, max_pages=1, http_client=http_client)

    assert len(pages) == 1
    assert len(http_client.calls) == 1


def test_fetch_review_pages_respects_max_reviews() -> None:
    http_client = SequentialFakeHttpClient(FakeResponse(_load_fixture("steam_reviews_page_1.json")))

    pages = fetch_review_pages(553850, max_reviews=2, http_client=http_client)

    assert len(pages) == 1
    assert len(pages[0].reviews) == 2
    assert http_client.calls[0]["params"]["num_per_page"] == 2


def test_fetch_review_pages_stops_on_empty_or_repeated_cursor() -> None:
    repeated_cursor_payload = {"cursor": "*", "reviews": [_valid_review_payload()]}
    http_client = SequentialFakeHttpClient(FakeResponse(repeated_cursor_payload))

    pages = fetch_review_pages(553850, max_pages=5, http_client=http_client)

    assert len(pages) == 1
    assert len(http_client.calls) == 1


def test_fetch_review_pages_stops_on_empty_reviews() -> None:
    http_client = SequentialFakeHttpClient(FakeResponse({"cursor": "cursor-next", "reviews": []}))

    pages = fetch_review_pages(553850, max_pages=5, http_client=http_client)

    assert len(pages) == 1
    assert pages[0].reviews == []
    assert len(http_client.calls) == 1


def test_fetch_review_pages_wraps_request_failures() -> None:
    with pytest.raises(SteamReviewsError, match="request failed"):
        fetch_review_pages(553850, http_client=FailingHttpClient())


def test_fetch_review_pages_raises_sanitized_error_for_non_success_status() -> None:
    http_client = SequentialFakeHttpClient(FakeResponse({}, status_code=503))

    with pytest.raises(SteamReviewsError) as exc_info:
        fetch_review_pages(553850, http_client=http_client)

    message = str(exc_info.value)
    assert STEAM_REVIEWS_SOURCE in message
    assert "503" in message
    assert STEAM_REVIEWS_ENDPOINT_TEMPLATE.format(steam_appid=553850) not in message


def test_fetch_review_pages_raises_for_invalid_json() -> None:
    http_client = SequentialFakeHttpClient(FakeResponse(json_error=ValueError("bad json")))

    with pytest.raises(SteamReviewsError, match="invalid JSON"):
        fetch_review_pages(553850, http_client=http_client)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {},
        {"cursor": "next", "reviews": {}},
        {"cursor": 123, "reviews": []},
        {"cursor": "next", "reviews": ["not a mapping"]},
    ],
)
def test_fetch_review_pages_raises_for_malformed_payload(payload: Any) -> None:
    http_client = SequentialFakeHttpClient(FakeResponse(payload))

    with pytest.raises(SteamReviewsError, match="malformed"):
        fetch_review_pages(553850, http_client=http_client)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"steam_appid": 0},
        {"max_pages": 0},
        {"num_per_page": 0},
        {"max_reviews": 0},
        {"cursor": ""},
    ],
)
def test_fetch_review_pages_rejects_invalid_local_arguments(kwargs: dict[str, Any]) -> None:
    steam_appid = kwargs.pop("steam_appid", 553850)

    with pytest.raises(ValueError):
        fetch_review_pages(steam_appid, **kwargs, http_client=SequentialFakeHttpClient(FakeResponse({})))


@pytest.mark.parametrize("value", [1768737600, 1768737600.0, "1768737600"])
def test_parse_steam_review_datetime_accepts_epoch_seconds(value: int | float | str) -> None:
    parsed = parse_steam_review_datetime(value)

    assert parsed.isoformat() == "2026-01-18T12:00:00+00:00"


@pytest.mark.parametrize("value", ["", "not-a-date", -1, object()])
def test_parse_steam_review_datetime_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        parse_steam_review_datetime(value)


def test_normalize_review_to_feedback_item_returns_strict_feedback_item() -> None:
    review = _load_fixture("steam_reviews_page_1.json")["reviews"][1]

    feedback_item = normalize_review_to_feedback_item(
        "helldivers_2",
        review,
        patch_event_id="patch-001",
        raw_oss_key="raw/steam_reviews/helldivers_2/patch-001/page_1_20260118T120000Z.json",
    )

    assert isinstance(feedback_item, FeedbackItem)
    assert feedback_item.game_id == "helldivers_2"
    assert feedback_item.patch_event_id == "patch-001"
    assert feedback_item.source == "steam_reviews"
    assert feedback_item.external_id == "review-exact-patch"
    assert feedback_item.text == "Right as the patch landed, matchmaking started failing."
    assert feedback_item.created_at_source.isoformat() == "2026-01-18T12:00:00+00:00"
    assert feedback_item.url is None
    assert feedback_item.language == "english"
    assert feedback_item.positive is False
    assert feedback_item.helpful_votes == 8
    assert feedback_item.playtime_hours == 6.0
    assert feedback_item.raw_oss_key == "raw/steam_reviews/helldivers_2/patch-001/page_1_20260118T120000Z.json"


def test_normalize_review_to_feedback_item_uses_direct_review_url_only() -> None:
    review = {**_valid_review_payload(), "review_url": "https://steamcommunity.com/app/553850/recommended/123"}

    feedback_item = normalize_review_to_feedback_item("helldivers_2", review)

    assert feedback_item.url == "https://steamcommunity.com/app/553850/recommended/123"


@pytest.mark.parametrize(
    "review",
    [
        {"review": "Missing ID", "timestamp_created": 1768737600},
        {"recommendationid": " ", "review": "Empty ID", "timestamp_created": 1768737600},
        {"recommendationid": "review-1", "review": " ", "timestamp_created": 1768737600},
        {"recommendationid": "review-1", "review": "Bad date", "timestamp_created": "bad"},
        {**VALID_REVIEW_PAYLOAD, "voted_up": "yes"},
        {**VALID_REVIEW_PAYLOAD, "votes_up": -1},
        {**VALID_REVIEW_PAYLOAD, "language": 123},
        {**VALID_REVIEW_PAYLOAD, "author": "not a mapping"},
        {**VALID_REVIEW_PAYLOAD, "author": {"playtime_forever": -1}},
    ],
)
def test_normalize_review_to_feedback_item_rejects_invalid_records(review: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        normalize_review_to_feedback_item("helldivers_2", review)


def test_deduplicate_review_payloads_keeps_first_recommendationid_in_source_order() -> None:
    page_1_reviews = _load_fixture("steam_reviews_page_1.json")["reviews"]
    page_2_reviews = _load_fixture("steam_reviews_page_2.json")["reviews"]

    deduplicated = deduplicate_review_payloads([*page_1_reviews, *page_2_reviews])

    assert [review["recommendationid"] for review in deduplicated] == [
        "review-pre-patch",
        "review-exact-patch",
        "review-post-bug",
        "review-post-crash",
    ]
    assert deduplicated[2]["review"] == "After the hotfix, extraction crashes every other mission."


def test_filter_feedback_after_patch_excludes_pre_patch_and_includes_exact_timestamp() -> None:
    reviews = _load_fixture("steam_reviews_page_1.json")["reviews"]
    feedback_items = [normalize_review_to_feedback_item("helldivers_2", review) for review in reviews]

    filtered = filter_feedback_after_patch(feedback_items, PATCH_PUBLISHED_AT)

    assert [item.external_id for item in filtered] == ["review-exact-patch", "review-post-bug"]


def test_fetch_post_patch_feedback_returns_pages_unique_feedback_and_filters_pre_patch() -> None:
    http_client = SequentialFakeHttpClient(
        FakeResponse(_load_fixture("steam_reviews_page_1.json")),
        FakeResponse(_load_fixture("steam_reviews_page_2.json")),
    )

    result = fetch_post_patch_feedback(
        "helldivers_2",
        553850,
        PATCH_PUBLISHED_AT,
        patch_event_id="patch-001",
        max_pages=2,
        http_client=http_client,
    )

    assert len(result.pages) == 2
    assert [item.external_id for item in result.feedback_items] == [
        "review-exact-patch",
        "review-post-bug",
        "review-post-crash",
    ]
    assert all(item.source == "steam_reviews" for item in result.feedback_items)
    assert all(item.patch_event_id == "patch-001" for item in result.feedback_items)


def _load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def _valid_review_payload() -> dict[str, Any]:
    return dict(VALID_REVIEW_PAYLOAD)
