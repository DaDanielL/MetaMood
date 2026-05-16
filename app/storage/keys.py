"""Deterministic OSS object key builders for MetaMood artifacts."""

from __future__ import annotations

from datetime import datetime, timezone

TimestampInput = datetime | str


def raw_steam_news_key(game_id: str, patch_id: str, timestamp: TimestampInput) -> str:
    """Build the raw Steam News response object key."""
    return f"raw/steam_news/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/{_timestamp(timestamp)}.json"


def raw_steam_reviews_key(game_id: str, patch_id: str, page_number: int, timestamp: TimestampInput) -> str:
    """Build the raw Steam Reviews page response object key."""
    page = _page_number(page_number)
    return (
        f"raw/steam_reviews/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}"
        f"/page_{page}_{_timestamp(timestamp)}.json"
    )


def processed_patch_notes_key(game_id: str, patch_id: str) -> str:
    """Build the cleaned patch notes object key."""
    return f"processed/patch_notes/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/patch_notes.txt"


def processed_rag_doc_key(game_id: str, patch_id: str, document_name: str) -> str:
    """Build a processed RAG document object key."""
    safe_name = _segment("document_name", document_name)
    if not safe_name.endswith(".txt"):
        safe_name = f"{safe_name}.txt"
    return f"processed/rag_docs/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/{safe_name}"


def live_ops_brief_key(game_id: str, patch_id: str) -> str:
    """Build the generated live-ops brief object key."""
    return f"reports/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/live_ops_brief.md"


def action_board_key(game_id: str, patch_id: str) -> str:
    """Build the generated team action board object key."""
    return f"reports/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/action_board.json"


def community_response_key(game_id: str, patch_id: str) -> str:
    """Build the generated community response draft object key."""
    return f"reports/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}/community_response.md"


def fine_tuning_classification_dataset_key(game_id: str, patch_id: str) -> str:
    """Build the future classification fine-tuning dataset export object key."""
    return (
        f"exports/fine_tuning/{_segment('game_id', game_id)}/{_segment('patch_id', patch_id)}"
        "/classification_dataset.jsonl"
    )


def _timestamp(value: TimestampInput) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return _segment("timestamp", value)


def _segment(name: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string")
    if value == "":
        raise ValueError(f"{name} must not be empty")
    if value != value.strip():
        raise ValueError(f"{name} must not include leading or trailing whitespace")
    if "/" in value or "\\" in value:
        raise ValueError(f"{name} must not contain path separators")
    if ".." in value:
        raise ValueError(f"{name} must not contain '..'")
    return value


def _page_number(value: int) -> int:
    if not isinstance(value, int):
        raise ValueError("page_number must be an integer")
    if value < 1:
        raise ValueError("page_number must be greater than or equal to 1")
    return value
