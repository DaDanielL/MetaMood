# Stories: MetaMood MVP

**Source PRD**: `.agents/PRDs/metamood-mvp.prd.md`  
**Generated**: 2026-05-15T18:53:16Z  
**Status**: issues-created  
**GitHub Repo**: `DaDanielL/MetaMood`  
**Milestone**: `MVP Demo`

## Summary

| ID | Title | Type | Priority | Complexity | Phase | GitHub Issue |
|----|-------|------|----------|------------|-------|--------------|
| STORY-001 | Scaffold MetaMood FastAPI and Streamlit App | Technical | High | Medium | 1 | [#1](https://github.com/DaDanielL/MetaMood/issues/1) |
| STORY-002 | Add Configuration and Game Catalog Loading | Technical | High | Small | 1 | [#2](https://github.com/DaDanielL/MetaMood/issues/2) |
| STORY-003 | Define Core Pydantic Schemas | Technical | High | Small | 1 | [#5](https://github.com/DaDanielL/MetaMood/issues/5) |
| STORY-004 | Implement RDS PostgreSQL Data Models and Session Layer | Technical | High | Medium | 1 | [#6](https://github.com/DaDanielL/MetaMood/issues/6) |
| STORY-005 | Implement OSS Storage Client and Object Key Helpers | Technical | High | Medium | 1 | [#4](https://github.com/DaDanielL/MetaMood/issues/4) |
| STORY-006 | Implement Steam News Connector and Patch Detection | Feature | High | Medium | 2 | [#7](https://github.com/DaDanielL/MetaMood/issues/7) |
| STORY-007 | Implement Steam Reviews Connector and Filtering | Feature | High | Medium | 2 | [#3](https://github.com/DaDanielL/MetaMood/issues/3) |
| STORY-008 | Persist Ingested Patch and Feedback Data | Technical | High | Medium | 2 | [#8](https://github.com/DaDanielL/MetaMood/issues/8) |
| STORY-009 | Implement Qwen Client and Prompt Framework | Technical | High | Medium | 3 | [#12](https://github.com/DaDanielL/MetaMood/issues/12) |
| STORY-010 | Implement Feedback Classification Pipeline | Feature | High | Medium | 3 | [#9](https://github.com/DaDanielL/MetaMood/issues/9) |
| STORY-011 | Implement Issue Clustering and Urgency Scoring | Feature | High | Medium | 3 | [#11](https://github.com/DaDanielL/MetaMood/issues/11) |
| STORY-012 | Implement Bailian Knowledge Base RAG Adapter | Technical | High | Large | 4 | [#10](https://github.com/DaDanielL/MetaMood/issues/10) |
| STORY-013 | Implement Patch-Link Reasoning and Patch Impact Graph | Feature | High | Medium | 4 | [#13](https://github.com/DaDanielL/MetaMood/issues/13) |
| STORY-014 | Generate Live-Ops Brief and Team Action Board | Feature | High | Medium | 4 | [#14](https://github.com/DaDanielL/MetaMood/issues/14) |
| STORY-015 | Generate Community Response Draft and Risk Check | Feature | Medium | Medium | 4 | [#18](https://github.com/DaDanielL/MetaMood/issues/18) |
| STORY-016 | Build Streamlit MVP Dashboard | Feature | High | Medium | 4 | [#16](https://github.com/DaDanielL/MetaMood/issues/16) |
| STORY-017 | Add Mocked End-to-End Analysis Test Coverage | Technical | High | Medium | 4 | [#15](https://github.com/DaDanielL/MetaMood/issues/15) |
| STORY-018 | Document ECS Deployment and PAI Export Path | Technical | Medium | Medium | 4 | [#17](https://github.com/DaDanielL/MetaMood/issues/17) |

---

## STORY-001: Scaffold MetaMood FastAPI and Streamlit App

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 1 - Foundation and Alibaba Storage Plumbing  
**Labels**: `type:technical`, `backend`, `frontend`  
**GitHub Issue**: [#1](https://github.com/DaDanielL/MetaMood/issues/1)  
**Source**: `PRD Section 12 - Phase 1: Foundation and Alibaba Storage Plumbing`

### Description

As a developer, I want to scaffold the MetaMood backend and dashboard entry points, so that future stories have a runnable project foundation.

### Acceptance Criteria

- [ ] Create the planned `app/` package structure with route, connector, storage, database, LLM, RAG, analysis, reports, and service directories.
- [ ] Add a FastAPI app entry point with `GET /health` returning service name `metamood` and version `0.1.0`.
- [ ] Add a minimal `streamlit_app.py` that loads without requiring live cloud credentials.
- [ ] Add `requirements.txt` and/or `pyproject.toml` with initial runtime and test dependencies.
- [ ] Add a smoke test for the health endpoint.

### Technical Notes

- Follow the target structure in `AGENTS.md`.
- Keep Streamlit thin; orchestration belongs in backend services.
- Do not implement live Steam, Qwen, OSS, RDS, or Knowledge Base calls in this story.

### Dependencies

- Blocked by: None
- Blocks: STORY-002, STORY-003, STORY-004, STORY-005, STORY-006, STORY-009, STORY-016

### GitHub Issue Body

Scaffold the MetaMood application foundation described in `.agents/PRDs/metamood-mvp.prd.md`.

Acceptance criteria:

- Create the planned `app/` package structure.
- Add `GET /health` returning service name `metamood` and version `0.1.0`.
- Add a minimal `streamlit_app.py` that loads without live cloud credentials.
- Add initial Python dependency metadata.
- Add a smoke test for the health endpoint.

---

## STORY-002: Add Configuration and Game Catalog Loading

**Type**: Technical  
**Priority**: High  
**Complexity**: Small  
**Phase**: 1 - Foundation and Alibaba Storage Plumbing  
**Labels**: `type:technical`, `backend`, `config`  
**GitHub Issue**: [#2](https://github.com/DaDanielL/MetaMood/issues/2)  
**Source**: `PRD Section 7.1 - Game Catalog; PRD Section 9 - Security & Configuration`

### Description

As a live-ops producer, I want MetaMood to load a configured Steam game catalog, so that I can select enabled games for analysis.

### Acceptance Criteria

- [ ] Add `config/games.yaml` with 3-5 enabled Steam games.
- [ ] Implement config loading for app settings and game catalog entries.
- [ ] Exclude disabled games from the game list returned to the UI.
- [ ] Add `.env.example` with required app, Steam, OSS, RDS, Qwen, and Knowledge Base variables.
- [ ] Add tests for valid catalog loading, disabled games, and missing required fields.

### Technical Notes

- Use Pydantic or equivalent typed validation for config objects.
- Never require real cloud credentials for config unit tests.

### Dependencies

- Blocked by: STORY-001
- Blocks: STORY-006, STORY-007, STORY-016

### GitHub Issue Body

Implement MetaMood settings and game catalog loading.

Acceptance criteria:

- Add `config/games.yaml` with 3-5 enabled Steam games.
- Implement typed config loading.
- Exclude disabled games from UI/API results.
- Add `.env.example`.
- Add tests for catalog loading and validation.

---

## STORY-003: Define Core Pydantic Schemas

**Type**: Technical  
**Priority**: High  
**Complexity**: Small  
**Phase**: 1 - Foundation and Alibaba Storage Plumbing  
**Labels**: `type:technical`, `backend`, `api`  
**GitHub Issue**: [#5](https://github.com/DaDanielL/MetaMood/issues/5)  
**Source**: `PRD Section 15 - Data Schemas`

### Description

As a developer, I want typed domain schemas for MetaMood entities, so that ingestion, analysis, RAG, and reporting share clear contracts.

### Acceptance Criteria

- [ ] Add schemas for `GameConfig`, `PatchEvent`, `FeedbackItem`, `FeedbackClassification`, `RetrievedContext`, `IssueCluster`, `PatchLink`, and `LiveOpsReport`.
- [ ] Use strict enums or literals for classification labels where specified.
- [ ] Validate confidence and score fields with appropriate numeric constraints.
- [ ] Add schema tests for valid and invalid examples.

### Technical Notes

- Keep schemas in `app/schemas.py` unless the app grows enough to justify a schema package.
- These schemas should be usable by API routes, services, and tests.

### Dependencies

- Blocked by: STORY-001
- Blocks: STORY-004, STORY-006, STORY-007, STORY-010, STORY-012, STORY-013, STORY-014

### GitHub Issue Body

Add the core Pydantic schemas for the MetaMood domain.

Acceptance criteria:

- Define all core schemas from the PRD.
- Use strict labels for classification fields.
- Validate numeric confidence/score fields.
- Add valid and invalid schema tests.

---

## STORY-004: Implement RDS PostgreSQL Data Models and Session Layer

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 1 - Foundation and Alibaba Storage Plumbing  
**Labels**: `type:technical`, `database`, `backend`  
**GitHub Issue**: [#6](https://github.com/DaDanielL/MetaMood/issues/6)  
**Source**: `PRD Section 7.5 - RDS PostgreSQL Storage`

### Description

As a developer, I want SQLAlchemy models and database session management, so that MetaMood can persist structured game, patch, feedback, analysis, report, and model-run records.

### Acceptance Criteria

- [ ] Add SQLAlchemy models for `games`, `patch_events`, `feedback_items`, `feedback_classifications`, `issue_clusters`, `patch_links`, `live_ops_reports`, and `model_runs`.
- [ ] Add database session configuration from `DATABASE_URL`.
- [ ] Add deterministic table creation or Alembic migration support.
- [ ] Add unique constraints to prevent duplicate Steam records by source/external ID.
- [ ] Add tests that create the schema and verify basic insert/read behavior without live RDS.

### Technical Notes

- Use local SQLite or a local test database for default tests.
- Keep database access behind repositories in later stories.
- Do not put raw large API responses directly in relational rows; store OSS keys.

### Dependencies

- Blocked by: STORY-001, STORY-003
- Blocks: STORY-008, STORY-010, STORY-011, STORY-013, STORY-014, STORY-015, STORY-017

### GitHub Issue Body

Implement MetaMood RDS-compatible SQLAlchemy models and session management.

Acceptance criteria:

- Add all core database tables from the PRD.
- Configure sessions from `DATABASE_URL`.
- Support deterministic table creation or Alembic.
- Prevent duplicate Steam records.
- Add local tests for schema creation and insert/read behavior.

---

## STORY-005: Implement OSS Storage Client and Object Key Helpers

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 1 - Foundation and Alibaba Storage Plumbing  
**Labels**: `type:technical`, `storage`, `backend`  
**GitHub Issue**: [#4](https://github.com/DaDanielL/MetaMood/issues/4)  
**Source**: `PRD Section 7.4 - OSS Storage`

### Description

As a developer, I want an OSS storage adapter and deterministic object key helpers, so that MetaMood can store raw data, processed patch docs, generated reports, and future dataset exports.

### Acceptance Criteria

- [ ] Add object key builders for raw Steam News, raw Steam Reviews, processed patch notes, RAG docs, reports, and fine-tuning exports.
- [ ] Add an OSS client wrapper that reads credentials and bucket config from environment variables.
- [ ] Add a mock OSS client for tests and development.
- [ ] Add upload helpers for JSON, text, Markdown, and JSONL content.
- [ ] Add tests for object key generation and mock uploads.

### Technical Notes

- Do not log Alibaba access keys or bucket credentials.
- Return OSS object keys for persistence in RDS.

### Dependencies

- Blocked by: STORY-001
- Blocks: STORY-006, STORY-007, STORY-008, STORY-012, STORY-014, STORY-015, STORY-018

### GitHub Issue Body

Implement OSS storage support for MetaMood artifacts.

Acceptance criteria:

- Add deterministic object key builders.
- Add an environment-configured OSS client wrapper.
- Add a mock OSS client.
- Support JSON, text, Markdown, and JSONL uploads.
- Add object key and mock upload tests.

---

## STORY-006: Implement Steam News Connector and Patch Detection

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 2 - Steam Automatic Ingestion  
**Labels**: `type:feature`, `backend`, `ingestion`  
**GitHub Issue**: [#7](https://github.com/DaDanielL/MetaMood/issues/7)  
**Source**: `PRD Section 7.2 - Steam News Connector`

### Description

As a live-ops producer, I want MetaMood to detect the latest Steam update for a selected game, so that analysis starts from the correct patch context.

### Acceptance Criteria

- [ ] Fetch recent Steam News posts for a configured app ID using injectable HTTP client behavior.
- [ ] Detect likely patch/update posts using PRD keyword rules.
- [ ] Select the newest matching post.
- [ ] Normalize the result into `PatchEvent`.
- [ ] Clean HTML/BBCode-like content into readable plain text.
- [ ] Add fixture-based tests for detection, normalization, and date parsing.

### Technical Notes

- Default tests must use fixtures and make no live Steam calls.
- Keep network and normalization logic separable for testability.

### Dependencies

- Blocked by: STORY-001, STORY-002, STORY-003
- Blocks: STORY-008, STORY-012, STORY-013, STORY-017

### GitHub Issue Body

Implement Steam News ingestion and latest patch detection.

Acceptance criteria:

- Fetch recent Steam News posts using injectable HTTP behavior.
- Detect patch/update posts with keyword rules.
- Select newest matching post.
- Normalize to `PatchEvent`.
- Clean patch content.
- Add fixture-based tests.

---

## STORY-007: Implement Steam Reviews Connector and Filtering

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 2 - Steam Automatic Ingestion  
**Labels**: `type:feature`, `backend`, `ingestion`  
**GitHub Issue**: [#3](https://github.com/DaDanielL/MetaMood/issues/3)  
**Source**: `PRD Section 7.3 - Steam Reviews Connector`

### Description

As a live-ops producer, I want MetaMood to fetch recent reviews after a detected patch date, so that the analysis focuses on post-patch player response.

### Acceptance Criteria

- [ ] Fetch Steam reviews using cursor pagination with configurable page and review limits.
- [ ] Normalize reviews into `FeedbackItem` values.
- [ ] Filter reviews to those created after the patch date when timestamps are available.
- [ ] Preserve raw page payloads for storage.
- [ ] Add fixture-based tests for pagination, deduplication, normalization, and timestamp filtering.

### Technical Notes

- Respect `STEAM_REVIEW_MAX_PAGES`, `STEAM_REVIEW_NUM_PER_PAGE`, and `STEAM_REVIEW_MAX_REVIEWS`.
- Default tests must not call live Steam endpoints.

### Dependencies

- Blocked by: STORY-001, STORY-002, STORY-003
- Blocks: STORY-008, STORY-010, STORY-017

### GitHub Issue Body

Implement Steam Reviews ingestion and post-patch filtering.

Acceptance criteria:

- Fetch review pages using cursor pagination.
- Respect configured request limits.
- Normalize reviews into `FeedbackItem`.
- Filter by patch date.
- Preserve raw page payloads.
- Add fixture-based tests.

---

## STORY-008: Persist Ingested Patch and Feedback Data

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 2 - Steam Automatic Ingestion  
**Labels**: `type:technical`, `backend`, `database`, `storage`  
**GitHub Issue**: [#8](https://github.com/DaDanielL/MetaMood/issues/8)  
**Source**: `PRD Section 7.4 - OSS Storage; PRD Section 7.5 - RDS PostgreSQL Storage`

### Description

As a developer, I want the ingestion pipeline to store raw artifacts in OSS and normalized records in RDS, so that MetaMood has traceable evidence and queryable application state.

### Acceptance Criteria

- [ ] Store raw Steam News responses in OSS and save object keys on patch records.
- [ ] Store cleaned patch notes in OSS and save object keys on patch records.
- [ ] Store raw Steam Review pages in OSS and save object keys on feedback records or ingestion metadata.
- [ ] Persist normalized patch events and feedback items in RDS.
- [ ] Prevent duplicate persisted feedback records by source/external ID.
- [ ] Add mocked integration tests for ingestion persistence.

### Technical Notes

- OSS stores full artifacts; RDS stores structured rows and object keys.
- Keep persistence behind repository/storage interfaces.

### Dependencies

- Blocked by: STORY-004, STORY-005, STORY-006, STORY-007
- Blocks: STORY-010, STORY-011, STORY-012, STORY-017

### GitHub Issue Body

Wire ingestion outputs into OSS and RDS persistence.

Acceptance criteria:

- Store raw Steam News and cleaned patch notes in OSS.
- Store raw review pages in OSS.
- Persist normalized patch and feedback records in RDS.
- Deduplicate feedback by source/external ID.
- Add mocked persistence integration tests.

---

## STORY-009: Implement Qwen Client and Prompt Framework

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 3 - Qwen Classification and Issue Analysis  
**Labels**: `type:technical`, `backend`, `llm`  
**GitHub Issue**: [#12](https://github.com/DaDanielL/MetaMood/issues/12)  
**Source**: `PRD Section 7.7 - Qwen API Integration`

### Description

As a developer, I want a Qwen client and versioned prompt framework, so that MetaMood can call Alibaba Cloud Model Studio safely and traceably.

### Acceptance Criteria

- [ ] Add a Qwen client wrapper configured by `DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, model names, and request timeout.
- [ ] Add a mock Qwen client for default tests.
- [ ] Add prompt version constants for classification, patch-link reasoning, live-ops brief, and community response tasks.
- [ ] Add typed model errors and retry behavior where appropriate.
- [ ] Record model run metadata for success and failure paths.
- [ ] Add tests for configuration, mock responses, and error handling.

### Technical Notes

- Do not hardcode API keys.
- Keep prompt text centralized under `app/llm/prompts.py`.

### Dependencies

- Blocked by: STORY-001
- Blocks: STORY-010, STORY-013, STORY-014, STORY-015, STORY-017

### GitHub Issue Body

Implement the Qwen client and prompt framework.

Acceptance criteria:

- Add environment-configured Qwen client wrapper.
- Add mock Qwen client.
- Add prompt version constants.
- Add typed model errors and retry behavior.
- Record model run metadata.
- Add tests for config and error paths.

---

## STORY-010: Implement Feedback Classification Pipeline

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 3 - Qwen Classification and Issue Analysis  
**Labels**: `type:feature`, `backend`, `llm`  
**GitHub Issue**: [#9](https://github.com/DaDanielL/MetaMood/issues/9)  
**Source**: `PRD Section 7.8 - Feedback Classification`

### Description

As a live-ops producer, I want feedback classified into structured labels, so that player responses can be grouped, prioritized, and routed.

### Acceptance Criteria

- [ ] Classify feedback into theme, sentiment, severity, actionability, player trust risk, owner team, confidence, and rationale.
- [ ] Parse strict JSON from Qwen responses.
- [ ] Validate classification output against schemas before persistence.
- [ ] Reject or safely repair invalid model output.
- [ ] Persist classifications in RDS with model name and prompt version.
- [ ] Add tests for valid output, invalid output, repair/reject behavior, and persistence.

### Technical Notes

- Use the fixed label sets from the PRD.
- Do not infer internal telemetry.

### Dependencies

- Blocked by: STORY-003, STORY-008, STORY-009
- Blocks: STORY-011, STORY-013, STORY-014, STORY-017

### GitHub Issue Body

Implement feedback classification using Qwen and validated JSON outputs.

Acceptance criteria:

- Classify all required fields.
- Parse strict JSON.
- Validate against schemas.
- Repair or reject invalid output safely.
- Persist classifications with model metadata.
- Add tests for output and persistence behavior.

---

## STORY-011: Implement Issue Clustering and Urgency Scoring

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 3 - Qwen Classification and Issue Analysis  
**Labels**: `type:feature`, `backend`, `analysis`  
**GitHub Issue**: [#11](https://github.com/DaDanielL/MetaMood/issues/11)  
**Source**: `PRD Section 7.9 - Issue Clustering and Urgency Scoring`

### Description

As a live-ops producer, I want classified feedback grouped and scored, so that urgent issues can be prioritized over noisy low-severity complaints.

### Acceptance Criteria

- [ ] Group classified feedback by theme, sentiment, repeated keywords, and representative summary.
- [ ] Select representative quotes for each issue cluster.
- [ ] Aggregate severity, actionability, player trust risk, and suggested owner.
- [ ] Compute deterministic urgency scores using PRD weights.
- [ ] Persist issue clusters in RDS.
- [ ] Add tests proving lower-volume critical issues can outrank higher-volume low-severity complaints.

### Technical Notes

- Keep MVP clustering simple and deterministic before adding embeddings.
- Store representative quotes as JSON-compatible data.

### Dependencies

- Blocked by: STORY-004, STORY-008, STORY-010
- Blocks: STORY-012, STORY-013, STORY-014, STORY-016, STORY-017

### GitHub Issue Body

Implement issue clustering and urgency scoring.

Acceptance criteria:

- Group classified feedback into issue clusters.
- Select representative quotes.
- Aggregate key classification fields.
- Compute deterministic urgency scores.
- Persist clusters in RDS.
- Add scoring tests.

---

## STORY-012: Implement Bailian Knowledge Base RAG Adapter

**Type**: Technical  
**Priority**: High  
**Complexity**: Large  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:technical`, `backend`, `rag`  
**GitHub Issue**: [#10](https://github.com/DaDanielL/MetaMood/issues/10)  
**Source**: `PRD Section 7.6 - Bailian / Model Studio Knowledge Base RAG`

### Description

As a developer, I want a Knowledge Base adapter with Bailian and local mock implementations, so that MetaMood can retrieve patch context for grounded Qwen reasoning while remaining testable without live cloud calls.

### Acceptance Criteria

- [ ] Define the `KnowledgeBaseClient` protocol with `index_document` and `retrieve`.
- [ ] Implement `LocalMockKnowledgeBaseClient` for tests and development.
- [ ] Implement `BailianKnowledgeBaseClient` using environment configuration and clear setup errors when unavailable.
- [ ] Support indexing cleaned patch notes and seed documents where account access allows.
- [ ] Return `RetrievedContext` values for issue-cluster queries.
- [ ] Document Alibaba access limitations and setup requirements.
- [ ] Add tests for mock retrieval and production-mode unavailable behavior.

### Technical Notes

- Do not silently pretend production RAG succeeded.
- Keep local mock retrieval clearly marked as dev/test only.

### Dependencies

- Blocked by: STORY-003, STORY-005, STORY-006, STORY-008, STORY-011
- Blocks: STORY-013, STORY-014, STORY-017

### GitHub Issue Body

Implement the Knowledge Base RAG adapter layer.

Acceptance criteria:

- Define `KnowledgeBaseClient`.
- Add local mock retrieval.
- Add Bailian implementation with environment config.
- Support patch note indexing where access allows.
- Return `RetrievedContext` for cluster queries.
- Document access limitations.
- Add mock and error-path tests.

---

## STORY-013: Implement Patch-Link Reasoning and Patch Impact Graph

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:feature`, `backend`, `rag`, `llm`  
**GitHub Issue**: [#13](https://github.com/DaDanielL/MetaMood/issues/13)  
**Source**: `PRD Section 7.10 - Patch Impact Graph`

### Description

As a game designer, I want issue clusters linked to patch-note evidence, so that I can judge whether player complaints are likely caused by recent changes.

### Acceptance Criteria

- [ ] Retrieve patch context for top issue clusters using `KnowledgeBaseClient`.
- [ ] Call Qwen with issue summary, representative quotes, and retrieved context.
- [ ] Produce patch-link confidence, relevant patch change, reasoning, owner team, recommended action, and limitations.
- [ ] Persist patch links in RDS with retrieved context and model metadata.
- [ ] Generate Patch Impact Graph entries for report and dashboard use.
- [ ] Add tests with mocked Knowledge Base and Qwen responses.

### Technical Notes

- The output must distinguish low confidence from unsupported claims.
- Do not claim telemetry confirms an issue unless telemetry was provided.

### Dependencies

- Blocked by: STORY-006, STORY-010, STORY-011, STORY-012
- Blocks: STORY-014, STORY-016, STORY-017

### GitHub Issue Body

Implement patch-link reasoning and Patch Impact Graph generation.

Acceptance criteria:

- Retrieve patch context for issue clusters.
- Call Qwen with issue evidence and retrieved context.
- Produce confidence, reasoning, owner, action, and limitations.
- Persist patch links with model metadata.
- Generate graph entries.
- Add mocked tests.

---

## STORY-014: Generate Live-Ops Brief and Team Action Board

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:feature`, `backend`, `reports`, `llm`  
**GitHub Issue**: [#14](https://github.com/DaDanielL/MetaMood/issues/14)  
**Source**: `PRD Section 7.11 - Team Action Board; PRD Section 7.12 - Live-Ops Intelligence Brief`

### Description

As a live-ops producer, I want a generated brief and action board, so that stakeholder teams can review top issues, evidence, and recommended next steps.

### Acceptance Criteria

- [ ] Generate a Team Action Board ordered by urgency and grouped by owner team.
- [ ] Generate a Live-Ops Intelligence Brief with the PRD-required sections.
- [ ] Include representative feedback and retrieved patch evidence.
- [ ] Save Markdown and JSON report artifacts to OSS.
- [ ] Store report metadata in RDS.
- [ ] Add tests for serialization, unsupported-claim guardrails, and mocked Qwen output.

### Technical Notes

- The brief must not claim internal telemetry confirms anything.
- Save report OSS keys in structured report records.

### Dependencies

- Blocked by: STORY-005, STORY-009, STORY-011, STORY-012, STORY-013
- Blocks: STORY-015, STORY-016, STORY-017

### GitHub Issue Body

Generate the Live-Ops Intelligence Brief and Team Action Board.

Acceptance criteria:

- Generate action board ordered by urgency.
- Generate the brief with required sections.
- Include feedback and retrieved patch evidence.
- Save report artifacts to OSS.
- Store report metadata in RDS.
- Add serialization and guardrail tests.

---

## STORY-015: Generate Community Response Draft and Risk Check

**Type**: Feature  
**Priority**: Medium  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:feature`, `backend`, `reports`, `llm`  
**GitHub Issue**: [#18](https://github.com/DaDanielL/MetaMood/issues/18)  
**Source**: `PRD Section 7.13 - Community Response Draft`

### Description

As a community manager, I want a response draft with risk checks, so that I can communicate player-facing updates without overpromising or sounding defensive.

### Acceptance Criteria

- [ ] Generate a public-facing community response draft from top issues and report context.
- [ ] Run a risk checker that returns `pass`, `warn`, or `fail`.
- [ ] Flag overpromising, missing major issues, defensive tone, lack of acknowledgement, and unsupported claims.
- [ ] Save the draft and risk output in RDS and OSS where appropriate.
- [ ] Add tests with mocked Qwen responses for pass, warn, and fail outcomes.

### Technical Notes

- Human review remains required before publishing.
- Keep tone rules in versioned prompts.

### Dependencies

- Blocked by: STORY-009, STORY-014
- Blocks: STORY-016, STORY-017

### GitHub Issue Body

Generate the community response draft and risk check.

Acceptance criteria:

- Generate a public-facing response draft.
- Run risk checker returning `pass`, `warn`, or `fail`.
- Flag overpromising and unsupported claims.
- Save outputs in RDS and OSS.
- Add mocked tests for pass/warn/fail.

---

## STORY-016: Build Streamlit MVP Dashboard

**Type**: Feature  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:feature`, `frontend`, `api`  
**GitHub Issue**: [#16](https://github.com/DaDanielL/MetaMood/issues/16)  
**Source**: `PRD Section 7.14 - Dashboard`

### Description

As a live-ops stakeholder, I want a Streamlit dashboard for MetaMood, so that I can run analysis and review patch impact outputs in a demo-friendly interface.

### Acceptance Criteria

- [ ] Add Game Monitor page with game selection, app ID, analyze button, backend health, and service configuration status.
- [ ] Add Latest Update and Player Signal views.
- [ ] Add Patch Impact Graph and Team Action Board views.
- [ ] Add Live-Ops Brief and Community Response views.
- [ ] Add Alibaba Architecture page explaining ECS, OSS, RDS, Model Studio / Bailian, Qwen, Knowledge Base, and PAI.
- [ ] Dashboard supports local backend URL configuration.

### Technical Notes

- Keep UI pragmatic and demo-focused; no heavy frontend polish in MVP.
- Do not expose Alibaba credentials in the frontend.

### Dependencies

- Blocked by: STORY-001, STORY-002, STORY-011, STORY-013, STORY-014, STORY-015
- Blocks: STORY-017

### GitHub Issue Body

Build the Streamlit MVP dashboard.

Acceptance criteria:

- Add Game Monitor page.
- Add Latest Update and Player Signal views.
- Add Patch Impact Graph and Team Action Board views.
- Add Live-Ops Brief and Community Response views.
- Add Alibaba Architecture page.
- Support local backend URL configuration.

---

## STORY-017: Add Mocked End-to-End Analysis Test Coverage

**Type**: Technical  
**Priority**: High  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:technical`, `testing`, `backend`  
**GitHub Issue**: [#15](https://github.com/DaDanielL/MetaMood/issues/15)  
**Source**: `PRD Section 11 - Success Criteria; PRD Section 12 - Implementation Phases`

### Description

As a developer, I want mocked end-to-end analysis test coverage, so that MetaMood can be validated without live external services.

### Acceptance Criteria

- [ ] Add an end-to-end mocked analysis test covering game selection through report generation.
- [ ] Use fixture Steam News and Steam Reviews responses.
- [ ] Use mock OSS, mock Qwen, mock/local Knowledge Base, and local test database.
- [ ] Verify raw artifact keys, structured records, classifications, clusters, patch links, and report metadata.
- [ ] Ensure default test suite makes no live Steam, Qwen, OSS, RDS, or Bailian calls.

### Technical Notes

- This story should harden the pipeline after the major pieces exist.
- Add explicit markers for optional live integration tests if any are introduced later.

### Dependencies

- Blocked by: STORY-004, STORY-008, STORY-009, STORY-010, STORY-011, STORY-012, STORY-013, STORY-014, STORY-015, STORY-016
- Blocks: None

### GitHub Issue Body

Add mocked end-to-end analysis test coverage.

Acceptance criteria:

- Cover game selection through report generation.
- Use Steam fixtures.
- Use mock OSS, Qwen, Knowledge Base, and local DB.
- Verify persisted records and artifacts.
- Ensure default tests make no live external calls.

---

## STORY-018: Document ECS Deployment and PAI Export Path

**Type**: Technical  
**Priority**: Medium  
**Complexity**: Medium  
**Phase**: 4 - RAG, Reporting, Dashboard, and Deployment  
**Labels**: `type:technical`, `docs`, `deployment`  
**GitHub Issue**: [#17](https://github.com/DaDanielL/MetaMood/issues/17)  
**Source**: `PRD Section 12 - Phase 4; PRD Section 13 - Future Considerations`

### Description

As an Alibaba Cloud Solution Architect, I want deployment and future fine-tuning documentation, so that the MVP can be explained as a credible cloud solution and roadmap.

### Acceptance Criteria

- [ ] Document local setup, required environment variables, and mock-mode development.
- [ ] Document ECS deployment assumptions, startup options, health check, and security group notes.
- [ ] Document how the app connects to OSS, RDS, Qwen, and Knowledge Base where account access is available.
- [ ] Document Bailian Knowledge Base access limitations honestly.
- [ ] Document the future PAI dataset export path and why fine-tuning is deferred from MVP.
- [ ] Update README and keep links to the PRD and stories.

### Technical Notes

- Do not claim production Knowledge Base API integration works unless verified.
- Keep PAI fine-tuning lower priority until the core MaaS/RAG/cloud flow works.

### Dependencies

- Blocked by: STORY-005, STORY-012
- Blocks: None

### GitHub Issue Body

Document ECS deployment and the future PAI export path.

Acceptance criteria:

- Document local setup and mock mode.
- Document ECS deployment assumptions.
- Document OSS, RDS, Qwen, and Knowledge Base configuration.
- Document Knowledge Base access limitations.
- Document future PAI export/fine-tuning path.
- Update README with PRD and story links.
