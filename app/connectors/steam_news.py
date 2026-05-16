"""Steam News ingestion and patch detection helpers."""

from __future__ import annotations

import html
import math
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Any, Protocol

import httpx

from app.schemas import GameConfig, PatchEvent

STEAM_NEWS_ENDPOINT = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
STEAM_NEWS_SOURCE = "steam_news"
PATCH_KEYWORDS: tuple[str, ...] = (
    "patch",
    "hotfix",
    "update",
    "balance",
    "release notes",
    "maintenance",
    "season",
    "major update",
    "minor update",
    "bug fix",
)

_HTML_LINE_BREAK_RE = re.compile(
    r"(?i)<\s*br\s*/?\s*>|</\s*(?:p|div|li|h[1-6]|tr|blockquote)\s*>|<\s*li(?:\s[^>]*)?>"
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_BBCODE_LIST_ITEM_RE = re.compile(r"\[\*\]")
_BBCODE_BLOCK_RE = re.compile(r"\[/?(?:list|quote)(?:=[^\]]*)?\]", re.IGNORECASE)
_BBCODE_URL_RE = re.compile(r"\[/?url(?:=[^\]]*)?\]", re.IGNORECASE)
_BBCODE_TAG_RE = re.compile(r"\[/?[a-z0-9_*]+(?:=[^\]]*)?\]", re.IGNORECASE)
_SPACES_RE = re.compile(r"[ \t\f\v]+")


class SteamNewsError(RuntimeError):
    """Raised when Steam News fetching or payload extraction fails."""


class SteamNewsResponse(Protocol):
    """Minimal response protocol used by real and fake Steam News clients."""

    status_code: int

    def json(self) -> Any:
        """Return decoded JSON response data."""


class SteamNewsHttpClient(Protocol):
    """Minimal HTTP client protocol compatible with httpx.Client."""

    def get(self, url: str, *, params: dict[str, Any], timeout: float) -> SteamNewsResponse:
        """Fetch a Steam News response."""

def _get_news_response(
    http_client: SteamNewsHttpClient,
    params: dict[str, Any],
    timeout_seconds: float,
) -> SteamNewsResponse:
    try:
        return http_client.get(STEAM_NEWS_ENDPOINT, params=params, timeout=timeout_seconds)
    except Exception as exc:
        raise SteamNewsError(f"Steam News API request failed for endpoint {STEAM_NEWS_SOURCE}.") from exc

def fetch_recent_news(
    steam_appid: int,
    *,
    count: int = 20,
    maxlength: int = 0,
    enddate: int | float | str | datetime | None = None,
    http_client: SteamNewsHttpClient | None = None,
    timeout_seconds: float = 30.0,
) -> list[dict[str, Any]]:
    """Fetch recent Steam News items for an app ID."""
    if count < 1:
        raise ValueError("count must be greater than 0")

    params: dict[str, Any] = {
        "appid": steam_appid,
        "count": count,
        "maxlength": maxlength,
    }
    if enddate is not None:
        params["enddate"] = _steam_enddate_value(enddate)

    if http_client is not None:
        response = _get_news_response(http_client, params, timeout_seconds)
        return _extract_newsitems(response)

    with httpx.Client() as client:
        response = _get_news_response(client, params, timeout_seconds)
        return _extract_newsitems(response)


def parse_steam_news_datetime(value: object) -> datetime:
    """Parse a Steam News epoch timestamp as timezone-aware UTC."""
    if isinstance(value, bool):
        raise ValueError("Steam News date must be epoch seconds")

    if isinstance(value, (int, float)):
        timestamp = float(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Steam News date must not be empty")
        try:
            timestamp = float(stripped)
        except ValueError as exc:
            raise ValueError("Steam News date must be numeric epoch seconds") from exc
    else:
        raise ValueError("Steam News date must be epoch seconds")

    if not math.isfinite(timestamp) or timestamp < 0:
        raise ValueError("Steam News date must be a non-negative finite timestamp")

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def is_patch_news_post(news_item: object) -> bool:
    """Return whether a Steam News item looks like a patch or update post."""
    if not isinstance(news_item, Mapping):
        return False

    title = news_item.get("title")
    contents = news_item.get("contents")
    if not isinstance(title, str) or not isinstance(contents, str):
        return False

    searchable_text = f"{title} {contents}".lower()
    if not searchable_text.strip():
        return False

    return any(keyword in searchable_text for keyword in PATCH_KEYWORDS)


def select_latest_patch_post(news_items: list[object]) -> dict[str, Any] | None:
    """Select the newest patch-like Steam News item by parsed date."""
    latest_item: Mapping[str, Any] | None = None
    latest_date: datetime | None = None

    for news_item in news_items:
        if not isinstance(news_item, Mapping) or not is_patch_news_post(news_item):
            continue
        try:
            published_at = parse_steam_news_datetime(news_item.get("date"))
        except ValueError:
            continue
        if latest_date is None or published_at > latest_date:
            latest_item = news_item
            latest_date = published_at

    if latest_item is None:
        return None
    return dict(latest_item)


def clean_news_content(content: object) -> str:
    """Strip Steam HTML and BBCode-like markup while preserving visible text."""
    if not isinstance(content, str):
        return ""

    cleaned = html.unescape(content)
    cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = _HTML_LINE_BREAK_RE.sub("\n", cleaned)
    cleaned = _BBCODE_LIST_ITEM_RE.sub("\n- ", cleaned)
    cleaned = _BBCODE_BLOCK_RE.sub("\n", cleaned)
    cleaned = _BBCODE_URL_RE.sub("", cleaned)
    cleaned = _BBCODE_TAG_RE.sub("", cleaned)
    cleaned = _HTML_TAG_RE.sub(" ", cleaned)
    cleaned = html.unescape(cleaned)

    lines = []
    for line in cleaned.splitlines():
        normalized_line = _SPACES_RE.sub(" ", line).strip()
        if normalized_line:
            lines.append(normalized_line)
    return "\n".join(lines)


def normalize_news_item_to_patch_event(
    game_id: str,
    news_item: Mapping[str, Any],
    *,
    raw_oss_key: str | None = None,
    cleaned_text_oss_key: str | None = None,
) -> PatchEvent:
    """Normalize one Steam News item into a strict PatchEvent."""
    external_id = _required_external_id(news_item)
    title = _required_string(news_item, "title")
    published_at = parse_steam_news_datetime(news_item.get("date"))
    content = clean_news_content(news_item.get("contents", ""))
    raw_url = news_item.get("url")

    return PatchEvent.model_validate(
        {
            "game_id": game_id,
            "external_id": external_id,
            "source": STEAM_NEWS_SOURCE,
            "title": title,
            "published_at": published_at,
            "url": raw_url if isinstance(raw_url, str) and raw_url.strip() else None,
            "raw_oss_key": raw_oss_key,
            "cleaned_text_oss_key": cleaned_text_oss_key,
            "content": content,
        }
    )


def detect_latest_patch_event(
    game: GameConfig,
    *,
    count: int = 20,
    maxlength: int = 0,
    enddate: int | float | str | datetime | None = None,
    http_client: SteamNewsHttpClient | None = None,
    timeout_seconds: float = 30.0,
) -> PatchEvent | None:
    """Fetch Steam News for a game and return the newest detected patch event."""
    news_items = fetch_recent_news(
        game.steam_appid,
        count=count,
        maxlength=maxlength,
        enddate=enddate,
        http_client=http_client,
        timeout_seconds=timeout_seconds,
    )
    latest_patch_post = select_latest_patch_post(news_items)
    if latest_patch_post is None:
        return None
    return normalize_news_item_to_patch_event(game.game_id, latest_patch_post)


def _extract_newsitems(response: SteamNewsResponse) -> list[dict[str, Any]]:
    if not 200 <= response.status_code < 300:
        raise SteamNewsError(
            f"Steam News API failed for endpoint {STEAM_NEWS_SOURCE} with status code {response.status_code}."
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise SteamNewsError(f"Steam News API returned invalid JSON for endpoint {STEAM_NEWS_SOURCE}.") from exc

    if not isinstance(payload, Mapping):
        raise SteamNewsError(f"Steam News API returned malformed payload for endpoint {STEAM_NEWS_SOURCE}.")

    appnews = payload.get("appnews")
    if not isinstance(appnews, Mapping):
        raise SteamNewsError(f"Steam News API returned malformed payload for endpoint {STEAM_NEWS_SOURCE}.")

    news_items = appnews.get("newsitems")
    if not isinstance(news_items, list):
        raise SteamNewsError(f"Steam News API returned malformed payload for endpoint {STEAM_NEWS_SOURCE}.")

    normalized_items = []
    for news_item in news_items:
        if not isinstance(news_item, Mapping):
            raise SteamNewsError(f"Steam News API returned malformed payload for endpoint {STEAM_NEWS_SOURCE}.")
        normalized_items.append(dict(news_item))
    return normalized_items


def _steam_enddate_value(value: int | float | str | datetime) -> int | float | str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.astimezone(timezone.utc).timestamp())
    return value


def _required_external_id(news_item: Mapping[str, Any]) -> str:
    raw_external_id = news_item.get("gid", news_item.get("id"))
    if raw_external_id is None:
        raise ValueError("Steam News item must include gid or id")
    external_id = str(raw_external_id).strip()
    if not external_id:
        raise ValueError("Steam News item gid or id must not be empty")
    return external_id


def _required_string(news_item: Mapping[str, Any], field_name: str) -> str:
    value = news_item.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Steam News item must include non-empty {field_name}")
    return value
