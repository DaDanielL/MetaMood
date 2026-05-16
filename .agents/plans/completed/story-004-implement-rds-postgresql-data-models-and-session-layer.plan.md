# Plan: Implement RDS PostgreSQL Data Models and Session Layer

## Summary

Implement STORY-004 by adding SQLAlchemy 2.x dependencies, RDS-compatible ORM models for the eight core MetaMood tables, and explicit database engine/session/table-creation helpers configured from `DATABASE_URL`. Keep the story focused on the database foundation: no repositories, no ingestion persistence orchestration, no live RDS calls, and no API route changes. Validate the layer with SQLite-backed pytest coverage for schema creation, insert/read behavior, session configuration, relationships, JSON fields, and duplicate Steam record constraints.

## User Story

As a developer, I want SQLAlchemy models and database session management, so that MetaMood can persist structured game, patch, feedback, analysis, report, and model-run records.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | Dependencies, database models, database session helpers, tests |
| GitHub Issue | #6, https://github.com/DaDanielL/MetaMood/issues/6 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-004` |
| Current Branch | `main` |
| Working Tree | Clean at planning time |

---

## Feature Understanding

- **Problem**: MetaMood has Pydantic domain schemas and app settings, but no SQLAlchemy models or session layer for the structured RDS records needed by later ingestion, classification, clustering, RAG, and reporting stories.
- **Scope**: Add database dependencies, ORM models, deterministic table creation, engine/session helpers, package exports, and local database tests only.
- **Out of Scope**: Repositories, Alembic migrations, live RDS connectivity tests, ingestion persistence workflows, Qwen clients, OSS clients, API endpoints, and Streamlit changes.
- **Issue Acceptance Criteria**:
  - Add SQLAlchemy models for all core PRD tables.
  - Add database session configuration from `DATABASE_URL`.
  - Add deterministic table creation or Alembic migration support.
  - Add unique constraints to prevent duplicate Steam records by source/external ID.
  - Add tests that create the schema and verify basic insert/read behavior without live RDS.

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:155
Use snake_case for Python modules, functions, variables, and config keys.
Use PascalCase for Pydantic and SQLAlchemy model classes.
Use explicit IDs in domain names: game_id, patch_event_id, analysis_run_id, report_id.
```

### File Organization

```text
SOURCE: AGENTS.md:164
app/db/ is the home for SQLAlchemy models, sessions, and repositories.
Keep API handlers thin and keep persistence out of Streamlit.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:243
Recommended database files are app/db/models.py, app/db/session.py, and app/db/repositories.py.
For this story, create models.py and session.py; leave repositories for later persistence stories.
```

### Configuration

```text
SOURCE: app/config.py:25
AppSettings is a typed Pydantic settings object.
```

```text
SOURCE: app/config.py:43
database_url defaults to postgresql+psycopg2://user:password@host:5432/metamood.
```

```text
SOURCE: app/config.py:65
load_app_settings() reads .env when present and then environment variables.
Database helpers should reuse this instead of reading os.environ directly.
```

### Domain Contracts

```text
SOURCE: app/schemas.py:48
GameConfig fields: game_id, display_name, steam_appid, platform, enabled.
```

```text
SOURCE: app/schemas.py:58
PatchEvent fields: game_id, external_id, source, title, published_at, url, raw_oss_key, cleaned_text_oss_key, content.
```

```text
SOURCE: app/schemas.py:72
FeedbackItem fields: game_id, patch_event_id, source, external_id, text, created_at_source, url, language, positive, helpful_votes, playtime_hours, raw_oss_key.
```

```text
SOURCE: app/schemas.py:89
FeedbackClassification, IssueCluster, PatchLink, and LiveOpsReport define the field vocabulary future database records should mirror.
```

### Database Requirements

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:422
Required tables: games, patch_events, feedback_items, feedback_classifications, issue_clusters, patch_links, live_ops_reports, model_runs.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:437
Acceptance criteria include SQLAlchemy models, deterministic table creation, DATABASE_URL loading, source/external ID uniqueness, and SQLite/local test database usage.
```

```text
SOURCE: AGENTS.md:176
OSS stores full raw artifacts and generated files.
RDS stores queryable structured records and OSS object keys.
Deduplicate Steam records by source and external ID.
```

### Error Handling

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:842
RDS failures should roll back transactions and stop report generation if required records cannot be saved.
```

For this foundation story, implement session helpers that make transaction boundaries explicit. Do not add orchestration-level error handling until repositories/services exist.

### Tests

```text
SOURCE: tests/test_config.py:71
Config tests use monkeypatch to override environment variables without credentials.
```

```text
SOURCE: tests/test_schemas.py:19
Schema tests build valid domain examples directly and assert important parsed fields.
```

```text
SOURCE: AGENTS.md:235
Default tests must not call live Qwen, OSS, RDS, Bailian Knowledge Base, or Steam endpoints.
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | UPDATE | Add SQLAlchemy and a PostgreSQL driver matching the default `postgresql+psycopg2` URL. |
| `app/db/base.py` | CREATE | Define the shared SQLAlchemy declarative `Base`. |
| `app/db/models.py` | CREATE | Define ORM models for all eight core PRD tables, relationships, JSON columns, timestamps, and unique constraints. |
| `app/db/session.py` | CREATE | Define engine, session factory, session context, and deterministic table creation helpers using `DATABASE_URL`. |
| `app/db/__init__.py` | UPDATE | Export database base, models, and session helpers for future repository/service layers. |
| `tests/test_db_models.py` | CREATE | Verify SQLite schema creation, insert/read behavior, relationships, JSON persistence, and duplicate source/external ID constraints. |
| `tests/test_db_session.py` | CREATE | Verify engine/session helpers read `DATABASE_URL`, create tables deterministically, and commit/rollback session behavior locally. |

No `.env.example` change is required because `DATABASE_URL` already exists at `.env.example:22`.

---

## Data Model Design

### Shared Model Conventions

- Use SQLAlchemy 2.x typed declarative models with `Mapped[...]` and `mapped_column(...)`.
- Use `DateTime(timezone=True)` for timestamps and a Python UTC default helper for `created_at` / `updated_at`.
- Use `Text` for review text, patch content, rationales, summaries, generated report bodies, and error messages.
- Use SQLAlchemy `JSON` for list/dict payloads: `representative_quotes`, `retrieved_context`, `top_risks`, `team_action_board`, `patch_impact_graph`, `limitations`, and model run metadata.
- Keep raw payload bodies out of relational rows; store `raw_oss_key`, `cleaned_text_oss_key`, and `report_oss_key`.
- Use nullable foreign keys where later stories may create records in stages.
- Prefer string IDs such as `patch_event_id`, `feedback_item_id`, `issue_cluster_id`, `patch_link_id`, `report_id`, and `model_run_id`. Tests can provide deterministic IDs; later repositories can own ID generation.

### Tables and Core Columns

| Table | Model | Key Columns |
|-------|-------|-------------|
| `games` | `Game` | `game_id` PK, `display_name`, `steam_appid`, `platform`, `enabled`, timestamps. |
| `patch_events` | `PatchEventRecord` | `patch_event_id` PK, `game_id` FK, `source`, `external_id`, `title`, `published_at`, `url`, OSS keys, `content`, timestamps. |
| `feedback_items` | `FeedbackItemRecord` | `feedback_item_id` PK, `game_id` FK, nullable `patch_event_id` FK, `source`, `external_id`, `text`, `created_at_source`, metadata fields, `raw_oss_key`, timestamps. |
| `model_runs` | `ModelRun` | `model_run_id` PK, nullable `analysis_run_id`, `task`, `model_name`, `prompt_version`, `status`, `latency_ms`, `error_message`, `error_metadata`, request/response metadata, timestamps. |
| `feedback_classifications` | `FeedbackClassificationRecord` | `feedback_classification_id` PK, `feedback_item_id` FK, nullable `model_run_id` FK, label fields, `confidence`, `rationale`, timestamp. |
| `issue_clusters` | `IssueClusterRecord` | `issue_cluster_id` PK, nullable `analysis_run_id`, `game_id` FK, nullable `patch_event_id` FK, label fields, `summary`, `volume`, `representative_quotes`, `urgency_score`, timestamp. |
| `patch_links` | `PatchLinkRecord` | `patch_link_id` PK, `issue_cluster_id` FK, nullable `model_run_id` FK, `retrieved_context`, `patch_link_confidence`, `reasoning`, timestamp. |
| `live_ops_reports` | `LiveOpsReportRecord` | `report_id` PK, nullable `analysis_run_id`, `game_id` FK, `patch_event_id` FK, report body fields, JSON sections, `report_oss_key`, timestamp. |

### Constraints and Relationships

- `games.steam_appid` should be unique because one configured Steam app maps to one MetaMood game.
- `patch_events` should include `UniqueConstraint("source", "external_id", name="uq_patch_events_source_external_id")`.
- `feedback_items` should include `UniqueConstraint("source", "external_id", name="uq_feedback_items_source_external_id")`.
- Add indexes for likely lookup columns: `game_id`, `patch_event_id`, `analysis_run_id`, and model run `status` where useful.
- Relationships should support the basic graph used by later stories:
  - `Game.patch_events`, `Game.feedback_items`, `Game.issue_clusters`, `Game.live_ops_reports`.
  - `PatchEventRecord.feedback_items`, `PatchEventRecord.issue_clusters`, `PatchEventRecord.live_ops_reports`.
  - `FeedbackItemRecord.classifications`.
  - `IssueClusterRecord.patch_links`.
  - `ModelRun.feedback_classifications`, `ModelRun.patch_links`.

---

## Session and Table Creation Design

Create `app/db/session.py` with small explicit helpers:

```python
def create_database_engine(database_url: str | None = None, **engine_kwargs: Any) -> Engine:
    settings = load_app_settings() if database_url is None else None
    url = database_url or settings.database_url
    return create_engine(url, pool_pre_ping=True, future=True, **engine_kwargs)
```

```python
def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
```

```python
@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

```python
def create_all_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
```

Avoid creating a global engine at import time. This keeps tests credential-free, avoids accidental live connections, and lets later FastAPI dependencies decide lifecycle behavior.

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add SQLAlchemy dependencies

- **File**: `requirements.txt`
- **Action**: UPDATE
- **Implement**: Add `SQLAlchemy>=2.0,<3.0` and `psycopg2-binary>=2.9,<3.0`. Keep existing dependency style and ordering simple.
- **Mirror**: `requirements.txt:1` - one pinned range per line.
- **Validate**: `python -m pytest`

### Task 2: Add shared SQLAlchemy base

- **File**: `app/db/base.py`
- **Action**: CREATE
- **Implement**: Add a SQLAlchemy 2.x `DeclarativeBase` subclass named `Base`.
- **Mirror**: `app/db/__init__.py:1` - keep DB code under the reserved database boundary.
- **Validate**: `python -m pytest tests/test_db_models.py`

### Task 3: Add core ORM models

- **File**: `app/db/models.py`
- **Action**: CREATE
- **Implement**: Add `Game`, `PatchEventRecord`, `FeedbackItemRecord`, `FeedbackClassificationRecord`, `IssueClusterRecord`, `PatchLinkRecord`, `LiveOpsReportRecord`, and `ModelRun` with fields matching the Pydantic/domain contracts and table design above.
- **Mirror**: `app/schemas.py:48` through `app/schemas.py:148` - preserve domain field names where practical.
- **Validate**: `python -m pytest tests/test_db_models.py`

### Task 4: Add uniqueness and relationship behavior

- **File**: `app/db/models.py`
- **Action**: UPDATE
- **Implement**: Add unique constraints for `patch_events(source, external_id)` and `feedback_items(source, external_id)`, unique `games.steam_appid`, foreign keys, relationship definitions, indexes, and created/updated timestamp columns.
- **Mirror**: `AGENTS.md:176` - deduplicate Steam records by source/external ID and store OSS keys instead of raw payload bodies.
- **Validate**: `python -m pytest tests/test_db_models.py`

### Task 5: Add session and table creation helpers

- **File**: `app/db/session.py`
- **Action**: CREATE
- **Implement**: Add `create_database_engine`, `create_session_factory`, `session_scope`, and `create_all_tables`. Read `DATABASE_URL` through `load_app_settings()` only when a URL is not passed explicitly.
- **Mirror**: `app/config.py:65` - reuse typed settings loading and environment override behavior.
- **Validate**: `python -m pytest tests/test_db_session.py`

### Task 6: Export database package API

- **File**: `app/db/__init__.py`
- **Action**: UPDATE
- **Implement**: Keep the module docstring and export `Base`, model classes, and session helper names via imports and `__all__`.
- **Mirror**: `app/__init__.py:1` - small package-level API with explicit `__all__`.
- **Validate**: `python -m pytest tests/test_db_models.py tests/test_db_session.py`

### Task 7: Add model creation and insert/read tests

- **File**: `tests/test_db_models.py`
- **Action**: CREATE
- **Implement**: Use a local SQLite engine to call `create_all_tables`; assert all eight table names exist; insert one game, patch event, feedback item, model run, classification, issue cluster, patch link, and report; query them back and assert relationships plus JSON/list fields.
- **Mirror**: `tests/test_schemas.py:19` - build realistic PRD-like examples and assert parsed/persisted fields.
- **Validate**: `python -m pytest tests/test_db_models.py`

### Task 8: Add duplicate constraint tests

- **File**: `tests/test_db_models.py`
- **Action**: UPDATE
- **Implement**: Insert duplicate `PatchEventRecord` and `FeedbackItemRecord` values with the same `source`/`external_id` and assert SQLAlchemy raises `IntegrityError` on commit. Roll back between checks.
- **Mirror**: `tests/test_config.py:55` - use `pytest.raises(...)` for invalid/failure paths.
- **Validate**: `python -m pytest tests/test_db_models.py`

### Task 9: Add session helper tests

- **File**: `tests/test_db_session.py`
- **Action**: CREATE
- **Implement**: Verify `create_database_engine("sqlite+pysqlite:///:memory:")` works without live services; verify `create_database_engine()` honors a monkeypatched `DATABASE_URL`; verify `session_scope` commits on success and rolls back on exceptions.
- **Mirror**: `tests/test_config.py:71` - use `monkeypatch` for environment-driven settings without credentials.
- **Validate**: `python -m pytest tests/test_db_session.py`

### Task 10: Run full validation

- **File**: N/A
- **Action**: RUN
- **Implement**: Run the full test suite after the DB layer is added.
- **Mirror**: `AGENTS.md:257` - full validation command is `python -m pytest`.
- **Validate**: `python -m pytest`

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Tests accidentally try to connect to the default PostgreSQL/RDS URL. | Do not create a global engine at import time. In tests, pass `sqlite+pysqlite:///:memory:` explicitly or monkeypatch `DATABASE_URL` to SQLite. |
| SQLAlchemy JSON behavior differs between SQLite and PostgreSQL. | Store only JSON-compatible lists/dicts/strings/numbers in JSON columns and verify round trips in SQLite; avoid PostgreSQL-only JSON operators in this story. |
| Duplicate constraints are too broad or too narrow. | Follow the story wording exactly with `source` plus `external_id` unique constraints on Steam-derived patch and feedback tables. |
| Relationship requirements are overbuilt before repositories exist. | Add only straightforward relationships needed for insert/read tests and likely later persistence; leave repository methods for later stories. |
| Timestamps become timezone-inconsistent across SQLite and PostgreSQL. | Use timezone-aware Python UTC defaults and `DateTime(timezone=True)` columns. Avoid database-specific timestamp functions for core behavior. |
| PostgreSQL driver choice conflicts with default URL. | Use `psycopg2-binary` because `.env.example` and `AppSettings` default to `postgresql+psycopg2://...`. |

---

## Validation

Run these commands after implementation:

```bash
python -m pytest tests/test_db_models.py
python -m pytest tests/test_db_session.py
python -m pytest
```

No lint, typecheck, migration, or build command is currently configured.

## End-to-End Verification

- [ ] `python -m pytest tests/test_db_models.py` creates all eight core tables in SQLite.
- [ ] Insert/read test persists a full graph from game through report and model metadata.
- [ ] Duplicate `source`/`external_id` patch and feedback records fail with `IntegrityError`.
- [ ] `python -m pytest tests/test_db_session.py` verifies helper-created sessions commit and roll back locally.
- [ ] Full `python -m pytest` passes without live RDS, Qwen, OSS, Bailian Knowledge Base, or Steam calls.

## Acceptance Criteria

- [ ] All planned tasks completed.
- [ ] `requirements.txt` includes SQLAlchemy and a compatible PostgreSQL driver.
- [ ] SQLAlchemy models exist for `games`, `patch_events`, `feedback_items`, `feedback_classifications`, `issue_clusters`, `patch_links`, `live_ops_reports`, and `model_runs`.
- [ ] Database engine/session helpers read `DATABASE_URL` through the existing settings layer.
- [ ] Deterministic table creation exists through `create_all_tables`.
- [ ] Duplicate Steam records are prevented by source/external ID unique constraints.
- [ ] SQLite-backed tests verify schema creation and insert/read behavior without live RDS.
- [ ] Full validation passes with `python -m pytest`.
- [ ] Implementation follows `AGENTS.md` and keeps repository/service work for later stories.
