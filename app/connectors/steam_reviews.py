"""Steam Reviews ingestion and post-patch filtering helpers."""

from __future__ import annotations

import copy
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

import httpx

from app.schemas import FeedbackItem

STEAM_REVIEWS_ENDPOINT_TEMPLATE = "https://store.steampowered.com/appreviews/{steam_appid}"
STEAM_REVIEWS_SOURCE = "steam_reviews"
STEAM_REVIEWS_MAX_PAGE_SIZE = 100


class SteamReviewsError(RuntimeError):
    """Raised when Steam Reviews fetching or payload extraction fails."""


class SteamReviewsResponse(Protocol):
    """Minimal response protocol used by real and fake Steam Reviews clients."""

    status_code: int

    def json(self) -> Any:
        """Return decoded JSON response data."""


class SteamReviewsHttpClient(Protocol):
    """Minimal HTTP client protocol compatible with httpx.Client."""

    def get(self, url: str, *, params: dict[str, Any], timeout: float) -> SteamReviewsResponse:
        """Fetch a Steam Reviews response."""


@dataclass(frozen=True)
class SteamReviewPage:
    """One fetched Steam Reviews page and its preserved raw payload."""

    page_number: int
    cursor: str
    next_cursor: str | None
    payload: dict[str, Any]
    reviews: list[dict[str, Any]]


@dataclass(frozen=True)
class SteamReviewsFetchResult:
    """Fetched raw review pages plus normalized post-patch feedback."""

    pages: list[SteamReviewPage]
    feedback_items: list[FeedbackItem]


def fetch_review_pages(
    steam_appid: int,
    *,
    language: str = "english",
    review_type: str = "all",
    review_filter: str = "recent",
    max_pages: int = 5,
    num_per_page: int = STEAM_REVIEWS_MAX_PAGE_SIZE,
    max_reviews: int = 500,
    cursor: str = "*",
    http_client: SteamReviewsHttpClient | None = None,
    timeout_seconds: float = 30.0,
) -> list[SteamReviewPage]:
    """Fetch Steam Reviews pages using cursor pagination."""
    if isinstance(steam_appid, bool) or not isinstance(steam_appid, int) or steam_appid < 1:
        raise ValueError("steam_appid must be a positive integer")

    safe_max_pages = _positive_int("max_pages", max_pages)
    safe_num_per_page = min(_positive_int("num_per_page", num_per_page), STEAM_REVIEWS_MAX_PAGE_SIZE)
    safe_max_reviews = _positive_int("max_reviews", max_reviews)
    safe_cursor = _required_local_string("cursor", cursor)
    endpoint = STEAM_REVIEWS_ENDPOINT_TEMPLATE.format(steam_appid=steam_appid)

    if http_client is not None:
        return _fetch_review_pages_with_client(
            http_client,
            endpoint=endpoint,
            language=language,
            review_type=review_type,
            review_filter=review_filter,
            max_pages=safe_max_pages,
            num_per_page=safe_num_per_page,
            max_reviews=safe_max_reviews,
            cursor=safe_cursor,
            timeout_seconds=timeout_seconds,
        )

    with httpx.Client() as client:
        return _fetch_review_pages_with_client(
            client,
            endpoint=endpoint,
            language=language,
            review_type=review_type,
            review_filter=review_filter,
            max_pages=safe_max_pages,
            num_per_page=safe_num_per_page,
            max_reviews=safe_max_reviews,
            cursor=safe_cursor,
            timeout_seconds=timeout_seconds,
        )


def parse_steam_review_datetime(value: object) -> datetime:
    """Parse a Steam Reviews epoch timestamp as timezone-aware UTC."""
    if isinstance(value, bool):
        raise ValueError("Steam review timestamp must be epoch seconds")

    if isinstance(value, (int, float)):
        timestamp = float(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError("Steam review timestamp must not be empty")
        try:
            timestamp = float(stripped)
        except ValueError as exc:
            raise ValueError("Steam review timestamp must be numeric epoch seconds") from exc
    else:
        raise ValueError("Steam review timestamp must be epoch seconds")

    if not math.isfinite(timestamp) or timestamp < 0:
        raise ValueError("Steam review timestamp must be a non-negative finite timestamp")

    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def normalize_review_to_feedback_item(
    game_id: str,
    review: Mapping[str, Any],
    *,
    patch_event_id: str | None = None,
    raw_oss_key: str | None = None,
) -> FeedbackItem:
    """Normalize one Steam review into a strict FeedbackItem."""
    if not isinstance(review, Mapping):
        raise ValueError("Steam review must be a mapping")

    external_id = _required_review_external_id(review)
    text = _required_review_string(review, "review")
    created_at_source = parse_steam_review_datetime(review.get("timestamp_created"))

    return FeedbackItem.model_validate(
        {
            "game_id": game_id,
            "patch_event_id": patch_event_id,
            "source": STEAM_REVIEWS_SOURCE,
            "external_id": external_id,
            "text": text,
            "created_at_source": created_at_source,
            "url": _optional_direct_review_url(review),
            "language": _optional_string(review, "language"),
            "positive": _optional_bool(review, "voted_up"),
            "helpful_votes": _optional_non_negative_int(review, "votes_up"),
            "playtime_hours": _optional_playtime_hours(review),
            "raw_oss_key": raw_oss_key,
        }
    )


def deduplicate_review_payloads(reviews: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Keep the first review payload for each non-empty Steam recommendation ID."""
    deduplicated: list[dict[str, Any]] = []
    seen_external_ids: set[str] = set()

    for review in reviews:
        if not isinstance(review, Mapping):
            continue
        raw_external_id = review.get("recommendationid")
        if raw_external_id is None:
            continue
        external_id = str(raw_external_id).strip()
        if not external_id or external_id in seen_external_ids:
            continue
        seen_external_ids.add(external_id)
        deduplicated.append(copy.deepcopy(dict(review)))

    return deduplicated


def filter_feedback_after_patch(
    feedback_items: Iterable[FeedbackItem],
    patch_published_at: datetime,
) -> list[FeedbackItem]:
    """Return feedback created at or after the patch timestamp."""
    patch_timestamp = _as_utc_datetime("patch_published_at", patch_published_at)
    filtered_items: list[FeedbackItem] = []

    for feedback_item in feedback_items:
        created_at = _as_utc_datetime("created_at_source", feedback_item.created_at_source)
        if created_at >= patch_timestamp:
            filtered_items.append(feedback_item)

    return filtered_items


def fetch_post_patch_feedback(
    game_id: str,
    steam_appid: int,
    patch_published_at: datetime,
    *,
    patch_event_id: str | None = None,
    language: str = "english",
    review_type: str = "all",
    review_filter: str = "recent",
    max_pages: int = 5,
    num_per_page: int = STEAM_REVIEWS_MAX_PAGE_SIZE,
    max_reviews: int = 500,
    cursor: str = "*",
    http_client: SteamReviewsHttpClient | None = None,
    timeout_seconds: float = 30.0,
) -> SteamReviewsFetchResult:
    """Fetch, deduplicate, normalize, and filter post-patch Steam feedback."""
    pages = fetch_review_pages(
        steam_appid,
        language=language,
        review_type=review_type,
        review_filter=review_filter,
        max_pages=max_pages,
        num_per_page=num_per_page,
        max_reviews=max_reviews,
        cursor=cursor,
        http_client=http_client,
        timeout_seconds=timeout_seconds,
    )
    review_payloads = [review for page in pages for review in page.reviews]
    unique_review_payloads = deduplicate_review_payloads(review_payloads)
    feedback_items = [
        normalize_review_to_feedback_item(
            game_id,
            review,
            patch_event_id=patch_event_id,
        )
        for review in unique_review_payloads
    ]
    return SteamReviewsFetchResult(
        pages=pages,
        feedback_items=filter_feedback_after_patch(feedback_items, patch_published_at),
    )


def _fetch_review_pages_with_client(
    http_client: SteamReviewsHttpClient,
    *,
    endpoint: str,
    language: str,
    review_type: str,
    review_filter: str,
    max_pages: int,
    num_per_page: int,
    max_reviews: int,
    cursor: str,
    timeout_seconds: float,
) -> list[SteamReviewPage]:
    pages: list[SteamReviewPage] = []
    current_cursor = cursor
    collected_reviews = 0

    for page_number in range(1, max_pages + 1):
        remaining_reviews = max_reviews - collected_reviews
        if remaining_reviews < 1:
            break

        params = {
            "json": 1,
            "filter": review_filter,
            "language": language,
            "review_type": review_type,
            "num_per_page": min(num_per_page, remaining_reviews),
            "cursor": current_cursor,
        }
        response = _get_reviews_response(http_client, endpoint, params, timeout_seconds)
        payload, reviews, next_cursor = _extract_review_page(response)
        limited_reviews = reviews[:remaining_reviews]

        pages.append(
            SteamReviewPage(
                page_number=page_number,
                cursor=current_cursor,
                next_cursor=next_cursor,
                payload=payload,
                reviews=limited_reviews,
            )
        )
        collected_reviews += len(limited_reviews)

        if not reviews or collected_reviews >= max_reviews:
            break
        if not next_cursor or next_cursor == current_cursor:
            break
        current_cursor = next_cursor

    return pages


def _get_reviews_response(
    http_client: SteamReviewsHttpClient,
    endpoint: str,
    params: dict[str, Any],
    timeout_seconds: float,
) -> SteamReviewsResponse:
    try:
        return http_client.get(endpoint, params=params, timeout=timeout_seconds)
    except Exception as exc:
        raise SteamReviewsError(f"Steam Reviews API request failed for endpoint {STEAM_REVIEWS_SOURCE}.") from exc


def _extract_review_page(response: SteamReviewsResponse) -> tuple[dict[str, Any], list[dict[str, Any]], str | None]:
    if not 200 <= response.status_code < 300:
        raise SteamReviewsError(
            f"Steam Reviews API failed for endpoint {STEAM_REVIEWS_SOURCE} with status code {response.status_code}."
        )

    try:
        raw_payload = response.json()
    except Exception as exc:
        raise SteamReviewsError(f"Steam Reviews API returned invalid JSON for endpoint {STEAM_REVIEWS_SOURCE}.") from exc

    if not isinstance(raw_payload, Mapping):
        raise SteamReviewsError(f"Steam Reviews API returned malformed payload for endpoint {STEAM_REVIEWS_SOURCE}.")

    payload = copy.deepcopy(dict(raw_payload))
    raw_reviews = payload.get("reviews")
    if not isinstance(raw_reviews, list):
        raise SteamReviewsError(f"Steam Reviews API returned malformed payload for endpoint {STEAM_REVIEWS_SOURCE}.")

    reviews: list[dict[str, Any]] = []
    for review in raw_reviews:
        if not isinstance(review, Mapping):
            raise SteamReviewsError(f"Steam Reviews API returned malformed payload for endpoint {STEAM_REVIEWS_SOURCE}.")
        reviews.append(copy.deepcopy(dict(review)))

    raw_cursor = payload.get("cursor")
    if raw_cursor is None:
        next_cursor = None
    elif isinstance(raw_cursor, str):
        next_cursor = raw_cursor if raw_cursor else None
    else:
        raise SteamReviewsError(f"Steam Reviews API returned malformed payload for endpoint {STEAM_REVIEWS_SOURCE}.")

    return payload, reviews, next_cursor


def _positive_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be a positive integer")
    if value < 1:
        raise ValueError(f"{name} must be greater than 0")
    return value


def _required_local_string(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if not value:
        raise ValueError(f"{name} must not be empty")
    return value


def _required_review_external_id(review: Mapping[str, Any]) -> str:
    raw_external_id = review.get("recommendationid")
    if raw_external_id is None:
        raise ValueError("Steam review must include recommendationid")
    external_id = str(raw_external_id).strip()
    if not external_id:
        raise ValueError("Steam review recommendationid must not be empty")
    return external_id


def _required_review_string(review: Mapping[str, Any], field_name: str) -> str:
    value = review.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Steam review must include non-empty {field_name}")
    return value.strip()


def _optional_direct_review_url(review: Mapping[str, Any]) -> str | None:
    for field_name in ("url", "review_url"):
        value = review.get(field_name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _optional_string(review: Mapping[str, Any], field_name: str) -> str | None:
    value = review.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Steam review {field_name} must be a string")
    stripped = value.strip()
    return stripped or None


def _optional_bool(review: Mapping[str, Any], field_name: str) -> bool | None:
    value = review.get(field_name)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"Steam review {field_name} must be a boolean")
    return value


def _optional_non_negative_int(review: Mapping[str, Any], field_name: str) -> int | None:
    value = review.get(field_name)
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"Steam review {field_name} must be a non-negative integer")
    if isinstance(value, int):
        integer_value = value
    elif isinstance(value, float) and value.is_integer():
        integer_value = int(value)
    elif isinstance(value, str) and value.strip():
        try:
            integer_value = int(value)
        except ValueError as exc:
            raise ValueError(f"Steam review {field_name} must be a non-negative integer") from exc
    else:
        raise ValueError(f"Steam review {field_name} must be a non-negative integer")
    if integer_value < 0:
        raise ValueError(f"Steam review {field_name} must be non-negative")
    return integer_value


def _optional_playtime_hours(review: Mapping[str, Any]) -> float | None:
    author = review.get("author")
    if author is None:
        return None
    if not isinstance(author, Mapping):
        raise ValueError("Steam review author must be a mapping")

    playtime_minutes = author.get("playtime_forever")
    if playtime_minutes is None:
        return None
    return _non_negative_float("author.playtime_forever", playtime_minutes) / 60


def _non_negative_float(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ValueError(f"Steam review {name} must be numeric")
    if isinstance(value, (int, float)):
        numeric_value = float(value)
    elif isinstance(value, str) and value.strip():
        try:
            numeric_value = float(value)
        except ValueError as exc:
            raise ValueError(f"Steam review {name} must be numeric") from exc
    else:
        raise ValueError(f"Steam review {name} must be numeric")
    if not math.isfinite(numeric_value) or numeric_value < 0:
        raise ValueError(f"Steam review {name} must be non-negative")
    return numeric_value


def _as_utc_datetime(name: str, value: datetime) -> datetime:
    if not isinstance(value, datetime):
        raise ValueError(f"{name} must be a datetime")
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
