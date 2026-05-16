from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.storage.keys import (
    action_board_key,
    community_response_key,
    fine_tuning_classification_dataset_key,
    live_ops_brief_key,
    processed_patch_notes_key,
    processed_rag_doc_key,
    raw_steam_news_key,
    raw_steam_reviews_key,
)


def test_object_key_builders_return_prd_required_paths() -> None:
    timestamp = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)

    assert raw_steam_news_key("helldivers_2", "patch-001", timestamp) == (
        "raw/steam_news/helldivers_2/patch-001/20260115T120000Z.json"
    )
    assert raw_steam_reviews_key("helldivers_2", "patch-001", 2, timestamp) == (
        "raw/steam_reviews/helldivers_2/patch-001/page_2_20260115T120000Z.json"
    )
    assert processed_patch_notes_key("helldivers_2", "patch-001") == (
        "processed/patch_notes/helldivers_2/patch-001/patch_notes.txt"
    )
    assert processed_rag_doc_key("helldivers_2", "patch-001", "known_issues") == (
        "processed/rag_docs/helldivers_2/patch-001/known_issues.txt"
    )
    assert live_ops_brief_key("helldivers_2", "patch-001") == (
        "reports/helldivers_2/patch-001/live_ops_brief.md"
    )
    assert action_board_key("helldivers_2", "patch-001") == (
        "reports/helldivers_2/patch-001/action_board.json"
    )
    assert community_response_key("helldivers_2", "patch-001") == (
        "reports/helldivers_2/patch-001/community_response.md"
    )
    assert fine_tuning_classification_dataset_key("helldivers_2", "patch-001") == (
        "exports/fine_tuning/helldivers_2/patch-001/classification_dataset.jsonl"
    )


def test_timestamp_datetimes_are_normalized_to_utc() -> None:
    timestamp = datetime(2026, 1, 15, 7, 0, tzinfo=timezone(timedelta(hours=-5)))

    assert raw_steam_news_key("helldivers_2", "patch-001", timestamp).endswith("20260115T120000Z.json")


def test_timestamp_strings_are_accepted_when_path_safe() -> None:
    key = raw_steam_news_key("helldivers_2", "patch-001", "20260115T120000Z")

    assert key == "raw/steam_news/helldivers_2/patch-001/20260115T120000Z.json"


@pytest.mark.parametrize("page_number", [0, -1])
def test_review_page_number_must_be_positive(page_number: int) -> None:
    with pytest.raises(ValueError, match="page_number"):
        raw_steam_reviews_key("helldivers_2", "patch-001", page_number, "20260115T120000Z")


@pytest.mark.parametrize(
    "unsafe_segment",
    [
        "",
        " ",
        " helldivers_2",
        "helldivers_2 ",
        "../helldivers_2",
        "helldivers_2/patch",
        "helldivers_2\\patch",
        "helldivers..2",
    ],
)
def test_key_builders_reject_unsafe_segments(unsafe_segment: str) -> None:
    with pytest.raises(ValueError):
        raw_steam_news_key(unsafe_segment, "patch-001", "20260115T120000Z")


def test_rag_doc_name_does_not_double_append_txt_extension() -> None:
    assert processed_rag_doc_key("helldivers_2", "patch-001", "community_guidelines.txt") == (
        "processed/rag_docs/helldivers_2/patch-001/community_guidelines.txt"
    )


@pytest.mark.parametrize("document_name", ["", "known/issues", "known\\issues", "../known_issues"])
def test_rag_doc_name_rejects_unsafe_segments(document_name: str) -> None:
    with pytest.raises(ValueError):
        processed_rag_doc_key("helldivers_2", "patch-001", document_name)
