"""SQLAlchemy ORM models for MetaMood structured records."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp for ORM defaults."""
    return datetime.now(timezone.utc)


class Game(Base):
    """Configured Steam game persisted for analysis runs."""

    __tablename__ = "games"

    game_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    steam_appid: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="steam")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    patch_events: Mapped[list[PatchEventRecord]] = relationship(back_populates="game")
    feedback_items: Mapped[list[FeedbackItemRecord]] = relationship(back_populates="game")
    issue_clusters: Mapped[list[IssueClusterRecord]] = relationship(back_populates="game")
    live_ops_reports: Mapped[list[LiveOpsReportRecord]] = relationship(back_populates="game")


class PatchEventRecord(Base):
    """Detected public patch or update event."""

    __tablename__ = "patch_events"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_patch_events_source_external_id"),
        Index("ix_patch_events_game_id_published_at", "game_id", "published_at"),
    )

    patch_event_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1000))
    raw_oss_key: Mapped[str | None] = mapped_column(String(1000))
    cleaned_text_oss_key: Mapped[str | None] = mapped_column(String(1000))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    game: Mapped[Game] = relationship(back_populates="patch_events")
    feedback_items: Mapped[list[FeedbackItemRecord]] = relationship(back_populates="patch_event")
    issue_clusters: Mapped[list[IssueClusterRecord]] = relationship(back_populates="patch_event")
    live_ops_reports: Mapped[list[LiveOpsReportRecord]] = relationship(back_populates="patch_event")


class FeedbackItemRecord(Base):
    """Normalized public player feedback item."""

    __tablename__ = "feedback_items"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_feedback_items_source_external_id"),
        Index("ix_feedback_items_game_id_created_at_source", "game_id", "created_at_source"),
    )

    feedback_item_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"), nullable=False, index=True)
    patch_event_id: Mapped[str | None] = mapped_column(ForeignKey("patch_events.patch_event_id"), index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at_source: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[str | None] = mapped_column(String(1000))
    language: Mapped[str | None] = mapped_column(String(50))
    positive: Mapped[bool | None] = mapped_column(Boolean)
    helpful_votes: Mapped[int | None] = mapped_column(Integer)
    playtime_hours: Mapped[float | None] = mapped_column(Float)
    raw_oss_key: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    game: Mapped[Game] = relationship(back_populates="feedback_items")
    patch_event: Mapped[PatchEventRecord | None] = relationship(back_populates="feedback_items")
    classifications: Mapped[list[FeedbackClassificationRecord]] = relationship(back_populates="feedback_item")


class ModelRun(Base):
    """Qwen or AI model execution metadata."""

    __tablename__ = "model_runs"

    model_run_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    analysis_run_id: Mapped[str | None] = mapped_column(String(100), index=True)
    task: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100))
    prompt_version: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_message: Mapped[str | None] = mapped_column(Text)
    error_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    request_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    response_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    feedback_classifications: Mapped[list[FeedbackClassificationRecord]] = relationship(back_populates="model_run")
    patch_links: Mapped[list[PatchLinkRecord]] = relationship(back_populates="model_run")


class FeedbackClassificationRecord(Base):
    """Validated classification result for one feedback item."""

    __tablename__ = "feedback_classifications"

    feedback_classification_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    feedback_item_id: Mapped[str] = mapped_column(
        ForeignKey("feedback_items.feedback_item_id"),
        nullable=False,
        index=True,
    )
    model_run_id: Mapped[str | None] = mapped_column(ForeignKey("model_runs.model_run_id"), index=True)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    sentiment: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    actionability: Mapped[str] = mapped_column(String(50), nullable=False)
    player_trust_risk: Mapped[str] = mapped_column(String(50), nullable=False)
    owner_team: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    feedback_item: Mapped[FeedbackItemRecord] = relationship(back_populates="classifications")
    model_run: Mapped[ModelRun | None] = relationship(back_populates="feedback_classifications")


class IssueClusterRecord(Base):
    """Grouped player feedback signal with priority metadata."""

    __tablename__ = "issue_clusters"
    __table_args__ = (Index("ix_issue_clusters_analysis_run_game", "analysis_run_id", "game_id"),)

    issue_cluster_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    analysis_run_id: Mapped[str | None] = mapped_column(String(100), index=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"), nullable=False, index=True)
    patch_event_id: Mapped[str | None] = mapped_column(ForeignKey("patch_events.patch_event_id"), index=True)
    theme: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False)
    actionability: Mapped[str] = mapped_column(String(50), nullable=False)
    player_trust_risk: Mapped[str] = mapped_column(String(50), nullable=False)
    suggested_owner: Mapped[str] = mapped_column(String(100), nullable=False)
    representative_quotes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    urgency_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    game: Mapped[Game] = relationship(back_populates="issue_clusters")
    patch_event: Mapped[PatchEventRecord | None] = relationship(back_populates="issue_clusters")
    patch_links: Mapped[list[PatchLinkRecord]] = relationship(back_populates="issue_cluster")


class PatchLinkRecord(Base):
    """RAG-supported connection between an issue cluster and patch context."""

    __tablename__ = "patch_links"

    patch_link_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    issue_cluster_id: Mapped[str] = mapped_column(
        ForeignKey("issue_clusters.issue_cluster_id"),
        nullable=False,
        index=True,
    )
    model_run_id: Mapped[str | None] = mapped_column(ForeignKey("model_runs.model_run_id"), index=True)
    retrieved_context: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    patch_link_confidence: Mapped[str] = mapped_column(String(20), nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

    issue_cluster: Mapped[IssueClusterRecord] = relationship(back_populates="patch_links")
    model_run: Mapped[ModelRun | None] = relationship(back_populates="patch_links")


class LiveOpsReportRecord(Base):
    """Generated live-ops intelligence report metadata and structured sections."""

    __tablename__ = "live_ops_reports"
    __table_args__ = (Index("ix_live_ops_reports_analysis_run_game", "analysis_run_id", "game_id"),)

    report_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    analysis_run_id: Mapped[str | None] = mapped_column(String(100), index=True)
    game_id: Mapped[str] = mapped_column(ForeignKey("games.game_id"), nullable=False, index=True)
    patch_event_id: Mapped[str] = mapped_column(ForeignKey("patch_events.patch_event_id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    top_risks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    team_action_board: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    patch_impact_graph: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    community_response: Mapped[str] = mapped_column(Text, nullable=False)
    limitations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    report_oss_key: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    game: Mapped[Game] = relationship(back_populates="live_ops_reports")
    patch_event: Mapped[PatchEventRecord] = relationship(back_populates="live_ops_reports")
