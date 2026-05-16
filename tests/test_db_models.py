from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    FeedbackClassificationRecord,
    FeedbackItemRecord,
    Game,
    IssueClusterRecord,
    LiveOpsReportRecord,
    ModelRun,
    PatchEventRecord,
    PatchLinkRecord,
)
from app.db.session import create_all_tables, create_database_engine, create_session_factory, session_scope


def test_create_all_tables_creates_core_database_schema() -> None:
    engine = _create_sqlite_schema()

    table_names = set(inspect(engine).get_table_names())

    assert {
        "games",
        "patch_events",
        "feedback_items",
        "feedback_classifications",
        "issue_clusters",
        "patch_links",
        "live_ops_reports",
        "model_runs",
    }.issubset(table_names)
    assert _has_unique_constraint(engine, "patch_events", "uq_patch_events_source_external_id")
    assert _has_unique_constraint(engine, "feedback_items", "uq_feedback_items_source_external_id")


def test_database_models_persist_and_read_core_analysis_graph() -> None:
    engine = _create_sqlite_schema()
    session_factory = create_session_factory(engine)

    with session_scope(session_factory) as session:
        session.add_all(_valid_analysis_graph())

    with session_scope(session_factory) as session:
        game = session.get(Game, "helldivers_2")
        report = session.get(LiveOpsReportRecord, "report-001")
        model_run = session.get(ModelRun, "model-run-001")
        cluster = session.get(IssueClusterRecord, "cluster-001")
        feedback_item = session.execute(select(FeedbackItemRecord)).scalar_one()

        assert game is not None
        assert game.display_name == "HELLDIVERS 2"
        assert game.patch_events[0].title == "Patch 01.000.400"
        assert feedback_item.classifications[0].theme == "balance"
        assert model_run is not None
        assert model_run.response_metadata == {"tokens": 128}
        assert cluster is not None
        assert cluster.representative_quotes == ["The weapon feels too strong now."]
        assert cluster.patch_links[0].retrieved_context[0]["source_title"] == "Patch 01.000.400"
        assert report is not None
        assert report.team_action_board[0]["owner_team"] == "Combat Design"
        assert report.patch_event.title == "Patch 01.000.400"


def test_patch_events_prevent_duplicate_source_external_id() -> None:
    engine = _create_sqlite_schema()
    session_factory = create_session_factory(engine)

    with session_scope(session_factory) as session:
        session.add(_valid_game())

    session = session_factory()
    try:
        session.add(
            _valid_patch_event(
                patch_event_id="patch-001",
                source="steam_news",
                external_id="steam-news-123",
            )
        )
        session.commit()
        session.add(
            _valid_patch_event(
                patch_event_id="patch-duplicate",
                source="steam_news",
                external_id="steam-news-123",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    finally:
        session.close()


def test_feedback_items_prevent_duplicate_source_external_id() -> None:
    engine = _create_sqlite_schema()
    session_factory = create_session_factory(engine)

    with session_scope(session_factory) as session:
        session.add(_valid_game())
        session.add(_valid_patch_event())

    session = session_factory()
    try:
        session.add(
            _valid_feedback_item(
                feedback_item_id="feedback-001",
                source="steam_reviews",
                external_id="review-123",
            )
        )
        session.commit()
        session.add(
            _valid_feedback_item(
                feedback_item_id="feedback-duplicate",
                source="steam_reviews",
                external_id="review-123",
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    finally:
        session.close()


def _create_sqlite_schema() -> Engine:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")
    create_all_tables(engine)
    return engine


def _has_unique_constraint(engine: Engine, table_name: str, constraint_name: str) -> bool:
    constraints = inspect(engine).get_unique_constraints(table_name)
    return any(constraint["name"] == constraint_name for constraint in constraints)


def _valid_analysis_graph() -> list[object]:
    return [
        _valid_game(),
        _valid_patch_event(),
        _valid_feedback_item(),
        ModelRun(
            model_run_id="model-run-001",
            analysis_run_id="analysis-run-001",
            task="classify_feedback",
            model_name="qwen-plus",
            prompt_version="classify_feedback_v1",
            status="succeeded",
            latency_ms=1420,
            request_metadata={"feedback_items": 1},
            response_metadata={"tokens": 128},
        ),
        FeedbackClassificationRecord(
            feedback_classification_id="classification-001",
            feedback_item_id="feedback-001",
            model_run_id="model-run-001",
            theme="balance",
            sentiment="negative",
            severity="high",
            actionability="medium",
            player_trust_risk="low",
            owner_team="Combat Design",
            confidence=0.82,
            rationale="The player complains that a weapon is overpowered in ranked gameplay.",
        ),
        IssueClusterRecord(
            issue_cluster_id="cluster-001",
            analysis_run_id="analysis-run-001",
            game_id="helldivers_2",
            patch_event_id="patch-001",
            theme="balance",
            summary="Players say the updated weapon is overperforming after the patch.",
            volume=18,
            sentiment="negative",
            severity="high",
            actionability="medium",
            player_trust_risk="low",
            suggested_owner="Combat Design",
            representative_quotes=["The weapon feels too strong now."],
            urgency_score=7.5,
        ),
        PatchLinkRecord(
            patch_link_id="patch-link-001",
            issue_cluster_id="cluster-001",
            model_run_id="model-run-001",
            retrieved_context=[
                {
                    "source_title": "Patch 01.000.400",
                    "source_type": "patch_notes",
                    "content": "Adjusted weapon damage values for the latest balance pass.",
                    "score": 0.91,
                    "knowledge_base_id": "kb-123",
                }
            ],
            patch_link_confidence="high",
            reasoning="The complaint references a weapon changed in the latest patch notes.",
        ),
        LiveOpsReportRecord(
            report_id="report-001",
            analysis_run_id="analysis-run-001",
            game_id="helldivers_2",
            patch_event_id="patch-001",
            title="Patch 01.000.400 Live-Ops Brief",
            executive_summary="Players are reacting negatively to the weapon balance changes.",
            top_risks=[{"theme": "balance", "severity": "high"}],
            team_action_board=[{"owner_team": "Combat Design", "recommended_action": "Review telemetry."}],
            patch_impact_graph=[{"patch_change": "Adjusted weapon damage.", "player_reaction": "Overpowered."}],
            community_response="We are reviewing balance feedback and will share updates when available.",
            limitations=["Analysis is based on public Steam reviews only."],
            report_oss_key="reports/helldivers_2/patch-001/live_ops_brief.md",
        ),
    ]


def _valid_game() -> Game:
    return Game(
        game_id="helldivers_2",
        display_name="HELLDIVERS 2",
        steam_appid=553850,
        platform="steam",
        enabled=True,
    )


def _valid_patch_event(
    patch_event_id: str = "patch-001",
    source: str = "steam_news",
    external_id: str = "steam-news-123",
) -> PatchEventRecord:
    return PatchEventRecord(
        patch_event_id=patch_event_id,
        game_id="helldivers_2",
        source=source,
        external_id=external_id,
        title="Patch 01.000.400",
        published_at=datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc),
        url="https://store.steampowered.com/news/app/553850/view/123",
        raw_oss_key="raw/steam/news/553850/123.json",
        cleaned_text_oss_key="processed/patches/helldivers_2/patch-001.txt",
        content="Adjusted weapon damage and fixed crashes.",
    )


def _valid_feedback_item(
    feedback_item_id: str = "feedback-001",
    source: str = "steam_reviews",
    external_id: str = "review-123",
) -> FeedbackItemRecord:
    return FeedbackItemRecord(
        feedback_item_id=feedback_item_id,
        game_id="helldivers_2",
        patch_event_id="patch-001",
        source=source,
        external_id=external_id,
        text="The updated weapon feels too strong in every match.",
        created_at_source=datetime(2026, 1, 16, 9, 30, tzinfo=timezone.utc),
        url="https://steamcommunity.com/profiles/example/recommended/553850/",
        language="english",
        positive=False,
        helpful_votes=12,
        playtime_hours=84.5,
        raw_oss_key="raw/steam/reviews/553850/review-123.json",
    )
