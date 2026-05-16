# Plan: Define Core Pydantic Schemas

## Summary

Implement STORY-003 by expanding `app/schemas.py` from a single API response model into the shared MetaMood domain contract module. Add Pydantic schemas for configured games, patch events, Steam feedback items, Qwen feedback classification output, retrieved RAG context, issue clusters, patch links, and live-ops reports. Keep the implementation narrow: no database models, no service orchestration, no live external calls. Move the existing `GameConfig` definition into `app/schemas.py` and import it from `app/config.py` so catalog loading and future services share the same model.

## User Story

As a developer, I want typed domain schemas for MetaMood entities, so that ingestion, analysis, RAG, and reporting share clear contracts.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | Pydantic schemas, configuration loader, tests |
| GitHub Issue | #5, https://github.com/DaDanielL/MetaMood/issues/5 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-003` |
| Current Branch | `main` |
| Working Tree | Clean at planning time |

---

## Feature Understanding

- **Problem**: The current scaffold only has `GameResponse` plus a catalog-local `GameConfig`; future ingestion, RAG, classification, clustering, patch-linking, persistence, and reporting stories need stable typed contracts.
- **Scope**: Add schema definitions and schema validation tests only. Do not add SQLAlchemy models, repositories, Qwen clients, RAG clients, Steam connectors, report generation, or API endpoints.
- **Issue Acceptance Criteria**:
  - Add schemas for `GameConfig`, `PatchEvent`, `FeedbackItem`, `FeedbackClassification`, `RetrievedContext`, `IssueCluster`, `PatchLink`, and `LiveOpsReport`.
  - Use strict enums or literals for classification labels where specified.
  - Validate confidence and score fields with appropriate numeric constraints.
  - Add schema tests for valid and invalid examples.

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:157
Use snake_case for Python modules, functions, variables, and config keys.
Use PascalCase for Pydantic and SQLAlchemy model classes.
Use explicit IDs in domain names: game_id, patch_event_id, analysis_run_id, report_id.
```

### File Organization

```text
SOURCE: AGENTS.md:164
app/api/ contains routes only; app/db, app/llm, app/rag, app/analysis, app/reports, and app/services are reserved for later implementation boundaries.
For this story, keep shared schemas in app/schemas.py per the story technical note.
```

### API and Schema Contracts

```text
SOURCE: app/schemas.py:1
The current schema module is small and already used by API routes:
"""Shared API response schemas."""
class GameResponse(BaseModel): ...
```

```text
SOURCE: app/api/routes_games.py:11
Routes declare explicit Pydantic response models:
@router.get("/games", response_model=list[GameResponse])
```

### Existing Config Model Pattern

```text
SOURCE: app/config.py:57
GameConfig currently lives inside config loading:
class GameConfig(BaseModel):
    game_id: str
    display_name: str
    steam_appid: int
    platform: str = "steam"
    enabled: bool = True
```

Move this model to `app/schemas.py` and import it into `app/config.py`. This keeps `GameCatalog` in the config module while making `GameConfig` available to API routes, services, connectors, and tests.

### Error Handling

```text
SOURCE: app/config.py:111
Config loaders wrap IO/YAML/Pydantic validation failures in ConfigError.
Schema validation itself should use Pydantic's ValidationError directly in tests; no new app error type is needed for this story.
```

### Classification Labels

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:543
FeedbackClassification should validate the required Qwen output shape:
theme, sentiment, severity, actionability, player_trust_risk, owner_team, confidence, rationale.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:558
Theme labels are explicitly specified:
bug, crash, performance, matchmaking, balance, monetization, rewards, progression, new_content, toxicity_safety, localization, praise, other.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:576
Owner teams are explicitly specified:
QA / Engineering, Combat Design, Economy Design, Live Ops, Community, Player Safety, Localization, Marketing, Product Analytics, Unknown.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:1206
PatchLink uses strict patch-link confidence:
Literal["high", "medium", "low", "none"].
```

For sentiment, severity, actionability, and player trust risk, use narrow MVP literals derived from the required output example and surrounding PRD language:

- `SentimentLabel = Literal["positive", "negative", "mixed", "neutral"]`
- `ImpactLevel = Literal["low", "medium", "high"]`

### Tests

```text
SOURCE: tests/test_config.py:8
Tests instantiate Pydantic-backed loaders with valid examples, then assert fields.
```

```text
SOURCE: tests/test_config.py:55
Invalid examples use pytest.raises around validation failures.
```

```text
SOURCE: tests/test_games.py:32
API contract tests inspect OpenAPI schema when response models change.
For STORY-003, add direct schema tests instead of adding new endpoints.
```

### Validation

```text
SOURCE: AGENTS.md:235
Default tests must not call live Qwen, OSS, RDS, Bailian Knowledge Base, or Steam endpoints.
```

```text
SOURCE: AGENTS.md:257
Run before reporting implementation complete:
python -m pytest
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `app/schemas.py` | UPDATE | Add shared domain schemas, strict label aliases, numeric constraints, and keep `GameResponse`. |
| `app/config.py` | UPDATE | Remove local `GameConfig` definition and import the shared `GameConfig` from `app.schemas`; keep `GameCatalog` and config loading behavior stable. |
| `tests/test_schemas.py` | CREATE | Add valid and invalid examples for all new schemas, label literals, and numeric bounds. |
| `tests/test_config.py` | UPDATE | If needed, adjust imports/expectations after moving `GameConfig`; existing catalog tests should continue to pass. |

No dependency, migration, API route, or documentation change is required for this story unless implementation reveals a broken public import.

---

## Implementation Design

### Shared Schema Base

In `app/schemas.py`, add a small internal base model:

```python
from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

Use it for new domain schemas and `GameResponse`. `extra="forbid"` is especially important for Qwen output validation so unexpected fields are rejected instead of silently accepted.

### Label Aliases

Define aliases near the top of `app/schemas.py`:

- `ThemeLabel`
- `SentimentLabel`
- `ImpactLevel`
- `OwnerTeam`
- `PatchLinkConfidence`

Prefer `typing.Literal` aliases over enum classes for now because the PRD examples are literal JSON values and future OpenAPI/Pydantic output should stay simple.

### Numeric Constraints

Use `Field` constraints:

- `steam_appid: int = Field(gt=0)`
- `helpful_votes: int | None = Field(default=None, ge=0)`
- `playtime_hours: float | None = Field(default=None, ge=0)`
- `confidence: float = Field(ge=0, le=1)`
- `score: float | None = Field(default=None, ge=0, le=1)`
- `volume: int = Field(ge=1)`
- `urgency_score: float = Field(ge=0)`

Keep datetime fields as `datetime` and let Pydantic parse ISO strings.

### Domain Schemas

Add or move these models into `app/schemas.py`:

- `GameConfig`: PRD fields already used by `config/games.yaml`.
- `PatchEvent`: PRD appendix fields.
- `FeedbackItem`: PRD appendix fields with non-negative vote/playtime constraints.
- `FeedbackClassification`: Qwen output shape from PRD section 7.8.
- `RetrievedContext`: PRD appendix fields with relevance score bounds.
- `IssueCluster`: PRD appendix fields using classification label aliases and urgency constraints.
- `PatchLink`: PRD appendix fields using `PatchLinkConfidence`.
- `LiveOpsReport`: PRD appendix fields; keep `top_risks`, `team_action_board`, and `patch_impact_graph` as `list[dict[str, Any]]` until report sub-shapes are specified by later stories.
- `GameResponse`: preserve current public `/games` contract.

### Config Reuse

Update `app/config.py`:

- Remove `GameConfig` class definition.
- Add `from app.schemas import GameConfig`.
- Leave `GameCatalog`, `load_game_catalog`, `load_enabled_games`, and `game_to_public_payload` behavior unchanged.

This should preserve `app.config.GameConfig` as an imported module name for any existing consumers while eliminating duplicate model definitions.

### Tests

Create `tests/test_schemas.py` with focused tests:

1. Valid examples instantiate every required schema.
2. `FeedbackClassification` accepts valid PRD-like output.
3. Invalid theme/owner/patch confidence values raise `ValidationError`.
4. Confidence and RAG score reject values below 0 or above 1.
5. Non-negative constraints reject negative helpful votes, playtime, volume, and urgency score where applicable.
6. Extra fields are rejected for LLM-facing schemas.
7. Datetime strings parse for `PatchEvent` and `FeedbackItem`.

Keep existing `/games` and config tests passing; they exercise that moving `GameConfig` did not break catalog loading or the public games API.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Duplicating `GameConfig` in both `app/config.py` and `app/schemas.py` creates divergent contracts. | Move the model into `app/schemas.py` and import it from `app/config.py`. |
| Strict `extra="forbid"` could surprise current API response code. | Verify `game_to_public_payload()` returns exactly the fields expected by `GameResponse`; existing tests cover this. |
| PRD fully specifies some labels but only implies others. | Use exact literals for specified theme, owner team, and patch-link confidence. Use conservative MVP literals for sentiment and impact levels and document them in tests. |
| Adding nested report sub-schemas too early overbuilds STORY-003. | Keep report board/graph/risk rows as `dict[str, Any]` until report generation stories define stable shapes. |
| Pydantic constraints might reject real future RAG scores if a provider returns scores outside 0-1. | Use 0-1 bounds now because issue #5 explicitly asks for score constraints; adjust later if the Bailian adapter has a different scale. |
| Moving `GameConfig` could break direct imports from `app.config`. | Import `GameConfig` at module scope in `app/config.py` so `from app.config import GameConfig` still works. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Expand Shared Schema Module

- **File**: `app/schemas.py`
- **Action**: UPDATE
- **Implement**: Add `SchemaBase`, label aliases, constrained numeric fields, and schemas for `GameConfig`, `PatchEvent`, `FeedbackItem`, `FeedbackClassification`, `RetrievedContext`, `IssueCluster`, `PatchLink`, and `LiveOpsReport`. Preserve `GameResponse` and update it to inherit from the shared base.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:1150` for appendix schemas; `.agents/PRDs/metamood-mvp.prd.md:543` for `FeedbackClassification`; `app/schemas.py:6` for current response-schema placement.
- **Validate**: `python -m pytest tests/test_schemas.py`

### Task 2: Reuse GameConfig in Config Loading

- **File**: `app/config.py`
- **Action**: UPDATE
- **Implement**: Import `GameConfig` from `app.schemas`, remove the local `GameConfig` class, and keep `GameCatalog` plus loader functions unchanged.
- **Mirror**: `app/config.py:67` for `GameCatalog` and `app/config.py:111` for existing catalog validation flow.
- **Validate**: `python -m pytest tests/test_config.py tests/test_games.py`

### Task 3: Add Schema Validation Tests

- **File**: `tests/test_schemas.py`
- **Action**: CREATE
- **Implement**: Add valid examples for all new domain schemas and invalid examples for strict labels, confidence bounds, score bounds, non-negative numeric fields, and extra fields.
- **Mirror**: `tests/test_config.py:8` for valid model assertions and `tests/test_config.py:55` for `pytest.raises` validation style.
- **Validate**: `python -m pytest tests/test_schemas.py`

### Task 4: Run Full Backend Test Suite

- **File**: N/A
- **Action**: VALIDATE
- **Implement**: Run the full test suite to ensure schema changes do not break existing health, config, or games behavior.
- **Mirror**: `AGENTS.md:257` validation requirement.
- **Validate**: `python -m pytest`

---

## Validation

Run the exact available backend validation command:

```bash
python -m pytest
```

Optional targeted checks while implementing:

```bash
python -m pytest tests/test_schemas.py
python -m pytest tests/test_config.py tests/test_games.py
```

No typecheck, lint, or build command is currently configured.

## End-to-End Verification

- [ ] `python -m pytest` passes with existing health/config/games tests and new schema tests.
- [ ] `GET /games` still returns the same public response shape through `GameResponse`.
- [ ] `FeedbackClassification.model_validate(...)` accepts the PRD example output.
- [ ] Invalid classification labels and confidence/score bounds raise Pydantic `ValidationError`.

## Acceptance Criteria

- [ ] Schemas added for `GameConfig`, `PatchEvent`, `FeedbackItem`, `FeedbackClassification`, `RetrievedContext`, `IssueCluster`, `PatchLink`, and `LiveOpsReport`.
- [ ] Strict literals are used for PRD-specified labels and patch-link confidence.
- [ ] Confidence and score fields have numeric bounds.
- [ ] Valid and invalid schema tests are added.
- [ ] Existing config and `/games` behavior remains stable.
- [ ] Validation commands pass.
- [ ] Implementation follows `AGENTS.md`.
