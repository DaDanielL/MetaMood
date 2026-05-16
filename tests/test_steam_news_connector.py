from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.connectors import (
    PATCH_KEYWORDS,
    STEAM_NEWS_ENDPOINT,
    SteamNewsError,
    clean_news_content,
    detect_latest_patch_event,
    fetch_recent_news,
    is_patch_news_post,
    normalize_news_item_to_patch_event,
    parse_steam_news_datetime,
    select_latest_patch_post,
)
from app.schemas import GameConfig, PatchEvent

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "steam_news_recent.json"


class FakeResponse:
    def __init__(self, payload: Any = None, *, status_code: int = 200, json_error: Exception | None = None) -> None:
        self.status_code = status_code
        self._payload = payload
        self._json_error = json_error

    def json(self) -> Any:
        if self._json_error is not None:
            raise self._json_error
        return self._payload


class FakeHttpClient:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, *, params: dict[str, Any], timeout: float) -> FakeResponse:
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        return self.response
    

class FailingHttpClient:
    def get(self, url, *, params, timeout):
        raise TimeoutError("network timeout")


def test_fetch_recent_news_wraps_request_failures() -> None:
    with pytest.raises(SteamNewsError, match="request failed"):
        fetch_recent_news(553850, http_client=FailingHttpClient())

def test_fetch_recent_news_uses_injected_http_client_and_returns_newsitems() -> None:
    payload = _load_fixture()
    http_client = FakeHttpClient(FakeResponse(payload))

    news_items = fetch_recent_news(553850, count=20, maxlength=0, enddate=1768924800, http_client=http_client)

    assert len(news_items) == 4
    assert news_items[0]["gid"] == "steam-news-community-20260120"
    assert http_client.calls == [
        {
            "url": STEAM_NEWS_ENDPOINT,
            "params": {"appid": 553850, "count": 20, "maxlength": 0, "enddate": 1768924800},
            "timeout": 30.0,
        }
    ]


def test_fetch_recent_news_requires_positive_count() -> None:
    with pytest.raises(ValueError, match="count must be greater than 0"):
        fetch_recent_news(553850, count=0, http_client=FakeHttpClient(FakeResponse(_load_fixture())))


def test_fetch_recent_news_raises_sanitized_error_for_non_success_status() -> None:
    http_client = FakeHttpClient(FakeResponse({}, status_code=503))

    with pytest.raises(SteamNewsError) as exc_info:
        fetch_recent_news(553850, http_client=http_client)

    message = str(exc_info.value)
    assert "steam_news" in message
    assert "503" in message
    assert STEAM_NEWS_ENDPOINT not in message


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"appnews": {}},
        {"appnews": {"newsitems": {}}},
    ],
)
def test_fetch_recent_news_raises_for_malformed_payload(payload: dict[str, Any]) -> None:
    with pytest.raises(SteamNewsError, match="malformed"):
        fetch_recent_news(553850, http_client=FakeHttpClient(FakeResponse(payload)))


def test_fetch_recent_news_raises_for_invalid_json() -> None:
    http_client = FakeHttpClient(FakeResponse(json_error=ValueError("bad json")))

    with pytest.raises(SteamNewsError, match="invalid JSON"):
        fetch_recent_news(553850, http_client=http_client)


@pytest.mark.parametrize("keyword", PATCH_KEYWORDS)
def test_patch_detection_uses_prd_keyword_rules(keyword: str) -> None:
    news_item = {
        "title": "Community Notes",
        "contents": f"The latest {keyword} details are now available.",
    }

    assert is_patch_news_post(news_item) is True


def test_patch_detection_returns_false_for_non_patch_or_malformed_items() -> None:
    assert is_patch_news_post({"title": "Community Spotlight", "contents": "Fan art roundup."}) is False
    assert is_patch_news_post({"title": "Patch Without Content"}) is False
    assert is_patch_news_post("not a mapping") is False


def test_select_latest_patch_post_uses_date_not_api_order() -> None:
    news_items = _load_fixture()["appnews"]["newsitems"]

    selected = select_latest_patch_post(news_items)

    assert selected is not None
    assert selected["gid"] == "steam-news-hotfix-20260118"
    assert selected["title"] == "Hotfix 01.002.105"


def test_select_latest_patch_post_returns_none_without_valid_matches() -> None:
    news_items = [
        {"gid": "community", "title": "Community Spotlight", "date": 1768924800, "contents": "Fan art."},
        {"gid": "bad-date", "title": "Patch Notes", "date": "not-a-date", "contents": "Balance changes."},
    ]

    assert select_latest_patch_post(news_items) is None


@pytest.mark.parametrize("value", [1768737600, 1768737600.0, "1768737600"])
def test_parse_steam_news_datetime_accepts_epoch_seconds(value: int | float | str) -> None:
    parsed = parse_steam_news_datetime(value)

    assert parsed.isoformat() == "2026-01-18T12:00:00+00:00"


@pytest.mark.parametrize("value", ["", "not-a-date", -1, object()])
def test_parse_steam_news_datetime_rejects_invalid_values(value: object) -> None:
    with pytest.raises(ValueError):
        parse_steam_news_datetime(value)


def test_clean_news_content_strips_html_and_bbcode_preserving_visible_text() -> None:
    raw_content = _load_fixture()["appnews"]["newsitems"][1]["contents"]

    cleaned = clean_news_content(raw_content)

    assert "Hotfix Notes" in cleaned
    assert "We fixed a crash on mission extraction." in cleaned
    assert "Balance: Reduced enemy spawn spikes." in cleaned
    assert "Known issues remain under review." in cleaned
    assert "<" not in cleaned
    assert ">" not in cleaned
    assert "[" not in cleaned
    assert "]" not in cleaned


def test_normalize_news_item_to_patch_event_returns_strict_patch_event() -> None:
    news_item = select_latest_patch_post(_load_fixture()["appnews"]["newsitems"])
    assert news_item is not None

    patch_event = normalize_news_item_to_patch_event(
        "helldivers_2",
        news_item,
        raw_oss_key="raw/steam_news/helldivers_2/patch-001/20260118T120000Z.json",
        cleaned_text_oss_key="processed/patch_notes/helldivers_2/patch-001/patch_notes.txt",
    )

    assert isinstance(patch_event, PatchEvent)
    assert patch_event.game_id == "helldivers_2"
    assert patch_event.external_id == "steam-news-hotfix-20260118"
    assert patch_event.source == "steam_news"
    assert patch_event.title == "Hotfix 01.002.105"
    assert patch_event.published_at.isoformat() == "2026-01-18T12:00:00+00:00"
    assert patch_event.url == "https://store.steampowered.com/news/app/553850/view/hotfix-20260118"
    assert patch_event.raw_oss_key == "raw/steam_news/helldivers_2/patch-001/20260118T120000Z.json"
    assert patch_event.cleaned_text_oss_key == "processed/patch_notes/helldivers_2/patch-001/patch_notes.txt"
    assert "Balance: Reduced enemy spawn spikes." in patch_event.content


def test_normalize_news_item_to_patch_event_falls_back_to_id() -> None:
    patch_event = normalize_news_item_to_patch_event(
        "helldivers_2",
        {
            "id": 12345,
            "title": "Patch Notes",
            "date": 1768737600,
            "contents": "Bug fix details.",
        },
    )

    assert patch_event.external_id == "12345"
    assert patch_event.url is None


@pytest.mark.parametrize(
    "news_item",
    [
        {"title": "Patch Notes", "date": 1768737600, "contents": "Bug fix details."},
        {"gid": "steam-news-1", "date": 1768737600, "contents": "Bug fix details."},
        {"gid": "steam-news-1", "title": "Patch Notes", "date": "bad", "contents": "Bug fix details."},
    ],
)
def test_normalize_news_item_to_patch_event_rejects_invalid_items(news_item: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        normalize_news_item_to_patch_event("helldivers_2", news_item)


def test_detect_latest_patch_event_fetches_selects_and_normalizes() -> None:
    game = GameConfig(game_id="helldivers_2", display_name="HELLDIVERS 2", steam_appid=553850)
    http_client = FakeHttpClient(FakeResponse(_load_fixture()))

    patch_event = detect_latest_patch_event(game, http_client=http_client)

    assert patch_event is not None
    assert patch_event.external_id == "steam-news-hotfix-20260118"
    assert patch_event.title == "Hotfix 01.002.105"
    assert patch_event.content
    assert http_client.calls[0]["params"]["appid"] == 553850


def _load_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
