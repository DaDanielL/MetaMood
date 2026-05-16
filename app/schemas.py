"""Shared Pydantic schemas for MetaMood domain and API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ThemeLabel = Literal[
    "bug",
    "crash",
    "performance",
    "matchmaking",
    "balance",
    "monetization",
    "rewards",
    "progression",
    "new_content",
    "toxicity_safety",
    "localization",
    "praise",
    "other",
]
SentimentLabel = Literal["positive", "negative", "mixed", "neutral"]
ImpactLevel = Literal["low", "medium", "high"]
OwnerTeam = Literal[
    "QA / Engineering",
    "Combat Design",
    "Economy Design",
    "Live Ops",
    "Community",
    "Player Safety",
    "Localization",
    "Marketing",
    "Product Analytics",
    "Unknown",
]
PatchLinkConfidence = Literal["high", "medium", "low", "none"]


class SchemaBase(BaseModel):
    """Base model for strict shared schema validation."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class GameConfig(SchemaBase):
    """Configured Steam game available to MetaMood."""

    game_id: str
    display_name: str
    steam_appid: int = Field(gt=0)
    platform: str = "steam"
    enabled: bool = True


class PatchEvent(SchemaBase):
    """Detected public patch or update event for a configured game."""

    game_id: str
    external_id: str
    source: str
    title: str
    published_at: datetime
    url: str | None = None
    raw_oss_key: str | None = None
    cleaned_text_oss_key: str | None = None
    content: str


class FeedbackItem(SchemaBase):
    """Normalized public player feedback item collected for analysis."""

    game_id: str
    patch_event_id: str | None = None
    source: str
    external_id: str
    text: str
    created_at_source: datetime
    url: str | None = None
    language: str | None = None
    positive: bool | None = None
    helpful_votes: int | None = Field(default=None, ge=0)
    playtime_hours: float | None = Field(default=None, ge=0)
    raw_oss_key: str | None = None


class FeedbackClassification(SchemaBase):
    """Validated Qwen classification output for one feedback item."""

    theme: ThemeLabel
    sentiment: SentimentLabel
    severity: ImpactLevel
    actionability: ImpactLevel
    player_trust_risk: ImpactLevel
    owner_team: OwnerTeam
    confidence: float = Field(ge=0, le=1)
    rationale: str


class RetrievedContext(SchemaBase):
    """Patch or policy context retrieved from the knowledge base."""

    source_title: str
    source_type: str
    content: str
    score: float | None = Field(default=None, ge=0, le=1)
    knowledge_base_id: str | None = None


class IssueCluster(SchemaBase):
    """Grouped player feedback signal with deterministic priority metadata."""

    theme: ThemeLabel
    summary: str
    volume: int = Field(ge=1)
    sentiment: SentimentLabel
    severity: ImpactLevel
    actionability: ImpactLevel
    player_trust_risk: ImpactLevel
    suggested_owner: OwnerTeam
    representative_quotes: list[str]
    urgency_score: float = Field(ge=0)


class PatchLink(SchemaBase):
    """Reasoned connection between an issue cluster and retrieved patch context."""

    issue_cluster_id: str
    retrieved_context: list[RetrievedContext]
    patch_link_confidence: PatchLinkConfidence
    reasoning: str


class LiveOpsReport(SchemaBase):
    """Generated live-ops intelligence report for a patch analysis run."""

    game_id: str
    patch_event_id: str
    title: str
    executive_summary: str
    top_risks: list[dict[str, Any]]
    team_action_board: list[dict[str, Any]]
    patch_impact_graph: list[dict[str, Any]]
    community_response: str
    limitations: list[str]
    report_oss_key: str | None = None


class GameResponse(SchemaBase):
    """Public game metadata returned by the games API."""

    game_id: str
    display_name: str
    steam_appid: int
    enabled: bool
