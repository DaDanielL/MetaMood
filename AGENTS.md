# AGENTS.md

This file gives Codex and other AI agents the operating context for the MetaMood repository.

## Project Overview

MetaMood is an Alibaba Cloud AI MaaS demo for live-service game teams. The MVP automatically detects a selected game's latest Steam update, collects recent public Steam reviews, stores raw and structured data on Alibaba Cloud services, uses Bailian / Model Studio Knowledge Base for RAG over patch context, and calls Qwen to generate patch-linked issue clusters, a Patch Impact Graph, a Team Action Board, a Live-Ops Intelligence Brief, and a Community Response Draft.

The project is currently pre-scaffold: product requirements exist in `.agents/PRDs/metamood-mvp.prd.md`, while application source folders are expected to be created through stories and plans. Treat the PRD as the source of truth until product code exists.

## Product Context

- **Primary users**: Live-ops producers, community managers, game designers, QA/engineering leads, and Alibaba Cloud Solution Architect demo reviewers.
- **Core problem**: Live-service teams need to understand which post-patch player complaints are patch-linked, severe, actionable, and safe to communicate about.
- **MVP outcome**: A local/ECS-runnable FastAPI + Streamlit demo that ingests Steam data, stores raw artifacts in OSS, stores structured records in RDS PostgreSQL, retrieves patch context through Bailian Knowledge Base, and uses Qwen for classification and reasoning.
- **Source PRD**: `.agents/PRDs/metamood-mvp.prd.md`

## Project Type

Planned full-stack web app with a Python backend and Streamlit dashboard. The repository currently contains AI-layer workflow artifacts and PRD documentation only; app source code, tests, and runtime manifests have not been scaffolded yet.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.11+ | Primary application runtime |
| FastAPI | Backend API and orchestration layer |
| Streamlit | MVP dashboard and Solution Architect demo UI |
| Pydantic | Domain schemas and LLM output validation |
| SQLAlchemy | Database models and persistence |
| Alembic or deterministic table creation | Database setup and migrations |
| ApsaraDB RDS PostgreSQL | Structured application records |
| Alibaba Cloud OSS Python SDK | Raw API responses, processed docs, generated reports, exports |
| Alibaba Cloud Model Studio / Qwen | AI MaaS classification, reasoning, and report generation |
| Bailian / Model Studio Knowledge Base | RAG over patch notes, known issues, and policy documents |
| pytest | Unit and mocked integration tests |
| Alibaba Cloud ECS | MVP backend and optional dashboard hosting |
| Alibaba Cloud PAI Model Gallery | Future fine-tuning path, not an MVP blocker |

## Commands

Current repository inspection and workflow commands:

```bash
# List tracked and hidden project files
find . -maxdepth 3 -type f | sort

# Search workflow and product docs
rg -n "MetaMood|Qwen|Bailian|OSS|RDS|Steam|Knowledge Base" .agents README.md AGENTS.md

# Check git state
git status --short
```

Expected commands after STORY-001 scaffolds the app:

```bash
# Install dependencies when requirements.txt exists
python -m pip install -r requirements.txt

# Start backend
python -m uvicorn app.main:app --reload

# Start Streamlit dashboard
python -m streamlit run streamlit_app.py

# Run tests
python -m pytest
```

If `pyproject.toml` defines project scripts later, prefer those documented scripts over raw module commands and update this file.

## Architecture

Use a modular monolith for the MVP. Keep a single FastAPI backend process responsible for ingestion, persistence, Qwen calls, RAG retrieval, analysis, and report generation. Keep Streamlit as a thin dashboard that calls backend endpoints and displays results.

```text
Steam News API / Steam Reviews API
        |
        v
FastAPI backend on ECS or local dev
        |
        +--> OSS: raw JSON, processed patch docs, reports, exports
        |
        +--> RDS PostgreSQL: structured records and model metadata
        |
        +--> Bailian Knowledge Base: RAG retrieval over patch context
        |
        +--> Qwen: classification, patch-link reasoning, reports
        |
        v
Streamlit dashboard
```

Prefer explicit adapters at every external boundary:

- Steam connectors fetch and normalize public data.
- OSS client stores raw and generated artifacts.
- Database repositories persist structured state.
- Qwen client handles Model Studio calls and errors.
- Knowledge Base client abstracts Bailian and local mock retrieval.

## Folder Structure

Target structure from the PRD:

```text
.
|-- AGENTS.md
|-- README.md
|-- .env.example
|-- requirements.txt
|-- pyproject.toml
|-- streamlit_app.py
|-- config/
|   `-- games.yaml
|-- app/
|   |-- main.py
|   |-- config.py
|   |-- schemas.py
|   |-- api/
|   |-- connectors/
|   |-- storage/
|   |-- db/
|   |-- llm/
|   |-- rag/
|   |-- analysis/
|   |-- reports/
|   `-- services/
|-- tests/
|   `-- fixtures/
`-- .agents/
    |-- PRDs/
    |-- stories/
    |-- plans/
    |-- reports/
    `-- reviews/
```

Do not add unrelated demo apps or framework samples. When scaffolding starts, build only the MetaMood app described by the PRD.

## API Contracts

MVP endpoints:

- `GET /health`
- `GET /games`
- `POST /analyze/latest`
- `GET /analysis/{analysis_run_id}`
- `GET /reports/{report_id}`
- `GET /reports/{report_id}/patch-impact-graph`

Use response shapes from `.agents/PRDs/metamood-mvp.prd.md`. Keep API handlers thin; put orchestration in `app/services/analysis_pipeline.py` and persistence in repositories.

## Code Patterns

### Naming

- Use snake_case for Python modules, functions, variables, and config keys.
- Use PascalCase for Pydantic and SQLAlchemy model classes.
- Use explicit IDs in domain names: `game_id`, `patch_event_id`, `analysis_run_id`, `report_id`.
- Use prompt version constants such as `PROMPT_VERSION_CLASSIFY_FEEDBACK = "classify_feedback_v1"`.

### File Organization

- `app/api/`: FastAPI route modules only.
- `app/connectors/`: external data ingestion, starting with Steam News and Reviews.
- `app/storage/`: OSS client and object key builders.
- `app/db/`: SQLAlchemy models, sessions, repositories.
- `app/llm/`: Qwen client, prompts, output parsing.
- `app/rag/`: `KnowledgeBaseClient`, Bailian implementation, local mock implementation.
- `app/analysis/`: classification, clustering, urgency scoring, patch linking.
- `app/reports/`: live-ops brief, community response, serializers.
- `app/services/`: end-to-end workflow orchestration.

### Data and Storage

- OSS stores full raw artifacts and generated files.
- RDS PostgreSQL stores queryable structured records and OSS object keys.
- Never store secrets in OSS, RDS, fixtures, logs, or generated reports.
- Deduplicate Steam records by source and external ID.
- Preserve raw Steam responses in OSS before relying on normalized records.

### RAG

- Treat Bailian / Model Studio Knowledge Base as the intended production RAG system.
- Keep `LocalMockKnowledgeBaseClient` for development and tests only.
- In production mode, fail clearly if Knowledge Base access is required but unavailable.
- Do not silently pretend RAG succeeded.

### LLM Usage

- Use Qwen through Model Studio configuration from environment variables.
- Validate all Qwen JSON output with Pydantic before persistence.
- Store `model_name`, `prompt_version`, status, latency, and error metadata for model runs.
- Do not claim internal telemetry confirms a finding unless telemetry data was provided.
- Prefer deterministic scoring and grouping before adding complex agent behavior.

### Error Handling

- Steam errors should include endpoint type and status code, not sensitive URLs.
- OSS failures should mark the analysis as partial failure when artifacts cannot be uploaded.
- RDS failures should roll back and stop report generation when required records cannot be saved.
- Qwen failures should store failed model run metadata and never generate fake output.

### Configuration

Use environment variables and `.env.example`; never hardcode keys.

Required variable groups:

- App: `APP_ENV`, `APP_HOST`, `APP_PORT`, `FRONTEND_PORT`
- Qwen: `DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, `QWEN_MODEL_CLASSIFIER`, `QWEN_MODEL_REASONER`, `QWEN_MODEL_REPORT`
- OSS: `ALIBABA_CLOUD_ACCESS_KEY_ID`, `ALIBABA_CLOUD_ACCESS_KEY_SECRET`, `OSS_ENDPOINT`, `OSS_REGION`, `OSS_BUCKET_NAME`
- RDS: `DATABASE_URL`
- Knowledge Base: `BAILIAN_KB_ENABLED`, `BAILIAN_KB_ID`, `BAILIAN_WORKSPACE_ID`, `BAILIAN_API_KEY`
- Steam: `STEAM_REVIEW_LANGUAGE`, `STEAM_REVIEW_MAX_PAGES`, `STEAM_REVIEW_NUM_PER_PAGE`, `STEAM_REVIEW_MAX_REVIEWS`, `STEAM_REVIEW_TYPE`, `STEAM_REVIEW_FILTER`
- Dev/test: `USE_MOCK_QWEN`, `USE_MOCK_OSS`, `USE_MOCK_KNOWLEDGE_BASE`

## Database Patterns

Core tables from the PRD:

- `games`
- `patch_events`
- `feedback_items`
- `feedback_classifications`
- `issue_clusters`
- `patch_links`
- `live_ops_reports`
- `model_runs`

Use repositories for database operations. Keep SQLAlchemy session lifecycle explicit and avoid database writes from Streamlit.

## Testing and Validation

Default tests must not call live external services:

- no live Qwen
- no live OSS
- no live RDS
- no live Bailian Knowledge Base
- no live Steam endpoints

Expected test coverage:

- Game config loading.
- Steam News patch detection and normalization.
- Steam Reviews pagination, deduplication, and timestamp filtering.
- OSS object key generation.
- SQLAlchemy model creation.
- Qwen output parsing and schema validation.
- Urgency scoring.
- Mocked Knowledge Base retrieval.
- Mocked end-to-end analysis run.

Run before reporting implementation complete after scaffold:

```bash
python -m pytest
```

If live integration tests are added, mark them explicitly and require opt-in environment flags.

## Security Requirements

- Never hardcode Alibaba, Qwen, RDS, or Steam credentials.
- Never log secrets.
- Do not expose Alibaba access keys to Streamlit.
- Make Steam calls from the backend, not the frontend.
- Store only public review metadata needed for analysis.
- Do not deanonymize Steam users.
- Require human review before publishing generated community responses.
- Keep OSS permissions least privilege.

## Deployment

MVP deployment target is a single Alibaba Cloud ECS instance running:

- FastAPI backend.
- Streamlit frontend, either on the same instance or local frontend pointing to ECS.

Document:

- environment variable setup
- ECS startup method, such as systemd or Docker
- security group ports
- health check
- RDS connectivity
- OSS bucket access
- Qwen and Knowledge Base account limitations

Kubernetes, multi-region deployment, production monitoring, and full RBAC are out of scope for MVP.

## GitHub Workflow

- Use GitHub Issues for trackable work when useful.
- Use story manifests in `.agents/stories/` as the local source of story IDs.
- Use `gh issue create` when turning approved stories into issues.
- Use `gh issue view {number}` before planning linked GitHub work.
- Use `gh pr create` for pull requests and `gh pr view` to inspect PR context.
- PRs should include summary, validation run, linked issue/story, and screenshots for UI changes.

## AI Layer

Generated artifacts live under `.agents/`:

| Artifact | Path |
|----------|------|
| PRDs | `.agents/PRDs/` |
| Story manifests | `.agents/stories/` |
| Implementation plans | `.agents/plans/` |
| Implementation reports | `.agents/reports/` |
| Reviews | `.agents/reviews/` |

Recommended workflow:

1. `create-stories .agents/PRDs/metamood-mvp.prd.md`
2. `prime`
3. `plan {story-or-issue}`
4. `implement`
5. `validate`
6. `review` / `security-review`

## Key Files

| File | Purpose |
|------|---------|
| `.agents/PRDs/metamood-mvp.prd.md` | Source PRD and MVP scope |
| `.agents/README.md` | AI workflow guide |
| `.agents/AGENTS-template.md` | Base template used to generate project rules |
| `AGENTS.md` | Current project operating rules |
| `README.md` | Root overview; update when app scaffold is added |
| `config/games.yaml` | Target game catalog once scaffolded |
| `app/main.py` | Target FastAPI entry point once scaffolded |
| `streamlit_app.py` | Target Streamlit entry point once scaffolded |
| `tests/` | Target unit and mocked integration tests once scaffolded |

## Agent Notes

- Preserve user changes; do not revert unrelated work.
- Treat `.agents/PRDs/metamood-mvp.prd.md` as the current product source of truth.
- Implement one story at a time.
- Build Alibaba cloud plumbing early; do not start with UI polish.
- Keep all cloud integrations mockable.
- Prefer simple deterministic logic before advanced ML or agentic behavior.
- Do not implement future roadmap features before MVP stories.
- Fine-tuning with PAI is lower priority until the core MaaS/RAG/cloud flow works.
- Update `AGENTS.md` when architecture, commands, or conventions change.
