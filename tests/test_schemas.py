from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas import (
    FeedbackClassification,
    FeedbackItem,
    GameConfig,
    GameResponse,
    IssueCluster,
    LiveOpsReport,
    PatchEvent,
    PatchLink,
    RetrievedContext,
)


def test_core_domain_schemas_accept_valid_examples() -> None:
    game = GameConfig.model_validate(
        {
            "game_id": "helldivers_2",
            "display_name": "HELLDIVERS 2",
            "steam_appid": 553850,
        }
    )
    patch_event = PatchEvent.model_validate(_valid_patch_event())
    feedback_item = FeedbackItem.model_validate(_valid_feedback_item())
    classification = FeedbackClassification.model_validate(_valid_classification())
    retrieved_context = RetrievedContext.model_validate(_valid_retrieved_context())
    issue_cluster = IssueCluster.model_validate(_valid_issue_cluster())
    patch_link = PatchLink.model_validate(
        {
            "issue_cluster_id": "cluster-001",
            "retrieved_context": [_valid_retrieved_context()],
            "patch_link_confidence": "high",
            "reasoning": "The complaint references a weapon changed in the latest patch notes.",
        }
    )
    report = LiveOpsReport.model_validate(
        {
            "game_id": "helldivers_2",
            "patch_event_id": "patch-001",
            "title": "Patch 01.000.400 Live-Ops Brief",
            "executive_summary": "Players are reacting negatively to the weapon balance changes.",
            "top_risks": [{"theme": "balance", "severity": "high"}],
            "team_action_board": [{"owner_team": "Combat Design", "recommended_action": "Review telemetry."}],
            "patch_impact_graph": [{"patch_change": "Adjusted weapon damage.", "player_reaction": "Overpowered."}],
            "community_response": "We are reviewing balance feedback and will share updates when available.",
            "limitations": ["Analysis is based on public Steam reviews only."],
        }
    )
    response = GameResponse.model_validate(
        {
            "game_id": game.game_id,
            "display_name": game.display_name,
            "steam_appid": game.steam_appid,
            "enabled": game.enabled,
        }
    )

    assert game.platform == "steam"
    assert isinstance(patch_event.published_at, datetime)
    assert isinstance(feedback_item.created_at_source, datetime)
    assert classification.theme == "balance"
    assert retrieved_context.score == 0.91
    assert issue_cluster.volume == 18
    assert patch_link.retrieved_context[0].source_title == "Patch 01.000.400"
    assert report.report_oss_key is None
    assert response.enabled is True


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("theme", "weapon_balance_problem"),
        ("sentiment", "angry"),
        ("severity", "urgent"),
        ("actionability", "unclear"),
        ("player_trust_risk", "severe"),
        ("owner_team", "Design"),
    ],
)
def test_feedback_classification_rejects_invalid_labels(field_name: str, invalid_value: str) -> None:
    payload = _valid_classification()
    payload[field_name] = invalid_value

    with pytest.raises(ValidationError):
        FeedbackClassification.model_validate(payload)


def test_patch_link_rejects_invalid_confidence_label() -> None:
    with pytest.raises(ValidationError):
        PatchLink.model_validate(
            {
                "issue_cluster_id": "cluster-001",
                "retrieved_context": [_valid_retrieved_context()],
                "patch_link_confidence": "certain",
                "reasoning": "The evidence is overstated.",
            }
        )


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_feedback_classification_rejects_confidence_outside_zero_to_one(confidence: float) -> None:
    payload = _valid_classification()
    payload["confidence"] = confidence

    with pytest.raises(ValidationError):
        FeedbackClassification.model_validate(payload)


@pytest.mark.parametrize("score", [-0.01, 1.01])
def test_retrieved_context_rejects_score_outside_zero_to_one(score: float) -> None:
    payload = _valid_retrieved_context()
    payload["score"] = score

    with pytest.raises(ValidationError):
        RetrievedContext.model_validate(payload)


def test_numeric_fields_reject_negative_or_zero_values() -> None:
    invalid_examples = [
        (GameConfig, {"game_id": "bad_app", "display_name": "Bad App", "steam_appid": 0}),
        (FeedbackItem, {**_valid_feedback_item(), "helpful_votes": -1}),
        (FeedbackItem, {**_valid_feedback_item(), "playtime_hours": -0.5}),
        (IssueCluster, {**_valid_issue_cluster(), "volume": 0}),
        (IssueCluster, {**_valid_issue_cluster(), "urgency_score": -0.1}),
    ]

    for model_class, payload in invalid_examples:
        with pytest.raises(ValidationError):
            model_class.model_validate(payload)


def test_schema_models_reject_extra_fields() -> None:
    payload = _valid_classification()
    payload["unexpected"] = "free-form Qwen drift"

    with pytest.raises(ValidationError):
        FeedbackClassification.model_validate(payload)


def _valid_patch_event() -> dict[str, object]:
    return {
        "game_id": "helldivers_2",
        "external_id": "steam-news-123",
        "source": "steam_news",
        "title": "Patch 01.000.400",
        "published_at": "2026-01-15T12:00:00+00:00",
        "url": "https://store.steampowered.com/news/app/553850/view/123",
        "raw_oss_key": "raw/steam/news/553850/123.json",
        "cleaned_text_oss_key": "processed/patches/helldivers_2/patch-001.txt",
        "content": "Adjusted weapon damage and fixed crashes.",
    }


def _valid_feedback_item() -> dict[str, object]:
    return {
        "game_id": "helldivers_2",
        "patch_event_id": "patch-001",
        "source": "steam_reviews",
        "external_id": "review-123",
        "text": "The updated weapon feels too strong in every match.",
        "created_at_source": "2026-01-16T09:30:00+00:00",
        "url": "https://steamcommunity.com/profiles/example/recommended/553850/",
        "language": "english",
        "positive": False,
        "helpful_votes": 12,
        "playtime_hours": 84.5,
        "raw_oss_key": "raw/steam/reviews/553850/review-123.json",
    }


def _valid_classification() -> dict[str, object]:
    return {
        "theme": "balance",
        "sentiment": "negative",
        "severity": "high",
        "actionability": "medium",
        "player_trust_risk": "low",
        "owner_team": "Combat Design",
        "confidence": 0.82,
        "rationale": "The player complains that a weapon is overpowered in ranked gameplay.",
    }


def _valid_retrieved_context() -> dict[str, object]:
    return {
        "source_title": "Patch 01.000.400",
        "source_type": "patch_notes",
        "content": "Adjusted weapon damage values for the latest balance pass.",
        "score": 0.91,
        "knowledge_base_id": "kb-123",
    }


def _valid_issue_cluster() -> dict[str, object]:
    return {
        "theme": "balance",
        "summary": "Players say the updated weapon is overperforming after the patch.",
        "volume": 18,
        "sentiment": "negative",
        "severity": "high",
        "actionability": "medium",
        "player_trust_risk": "low",
        "suggested_owner": "Combat Design",
        "representative_quotes": ["The weapon feels too strong now."],
        "urgency_score": 7.5,
    }
