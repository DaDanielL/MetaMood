"""External ingestion connector boundaries."""

from app.connectors.steam_news import (
    PATCH_KEYWORDS,
    STEAM_NEWS_ENDPOINT,
    SteamNewsError,
    SteamNewsHttpClient,
    SteamNewsResponse,
    clean_news_content,
    detect_latest_patch_event,
    fetch_recent_news,
    is_patch_news_post,
    normalize_news_item_to_patch_event,
    parse_steam_news_datetime,
    select_latest_patch_post,
)

__all__ = [
    "PATCH_KEYWORDS",
    "STEAM_NEWS_ENDPOINT",
    "SteamNewsError",
    "SteamNewsHttpClient",
    "SteamNewsResponse",
    "clean_news_content",
    "detect_latest_patch_event",
    "fetch_recent_news",
    "is_patch_news_post",
    "normalize_news_item_to_patch_event",
    "parse_steam_news_datetime",
    "select_latest_patch_post",
]
