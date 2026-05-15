# Plan: STORY-001 Scaffold MetaMood FastAPI and Streamlit App

## Summary

Scaffold the first runnable MetaMood application foundation without implementing live integrations. The implementation should create the planned Python package boundaries, add a FastAPI entry point with a `/health` route, add a minimal Streamlit shell that does not require cloud credentials, define initial dependency metadata, and add a pytest smoke test for the health endpoint. Because the repository is currently pre-scaffold, the plan mirrors the documented structure and rules in `AGENTS.md`, the PRD, and STORY-001 rather than existing product code.

## User Story

As a developer, I want to scaffold the MetaMood backend and dashboard entry points, so that future stories have a runnable project foundation.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | FastAPI backend scaffold, Streamlit dashboard shell, Python dependency metadata, pytest smoke tests |
| GitHub Issue | #1, https://github.com/DaDanielL/MetaMood/issues/1 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-001` |

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:155
Use snake_case for Python modules, functions, variables, and config keys; PascalCase is reserved for Pydantic and SQLAlchemy classes.
```

```text
SOURCE: AGENTS.md:164
Respect package boundaries: `app/api/` for FastAPI routes, `app/connectors/` for ingestion adapters, `app/storage/` for OSS boundaries, `app/db/` for persistence, `app/llm/` for Qwen, `app/rag/` for Knowledge Base, `app/analysis/` for analysis logic, `app/reports/` for report generation, and `app/services/` for orchestration.
```

### Architecture

```text
SOURCE: AGENTS.md:75
Use a modular monolith. FastAPI owns backend orchestration and Streamlit remains a thin dashboard that calls backend endpoints.
```

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:215
The PRD defines the target repository structure, including `app/main.py`, `app/api/routes_health.py`, service boundary directories, `streamlit_app.py`, and `tests/`.
```

### API Contract

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:852
`GET /health` must return:
{"status": "ok", "service": "metamood", "version": "0.1.0"}
```

### Error Handling

```text
SOURCE: .agents/stories/metamood-mvp.stories.md:60
Do not implement live Steam, Qwen, OSS, RDS, or Knowledge Base calls in this story.
```

```text
SOURCE: AGENTS.md:140
Do not add unrelated demo apps or framework samples. Build only the MetaMood app described by the PRD.
```

### Tests

```text
SOURCE: AGENTS.md:237
Default tests must not call live Qwen, OSS, RDS, Bailian Knowledge Base, or Steam endpoints.
```

```text
SOURCE: .agents/stories/metamood-mvp.stories.md:54
Add a smoke test for the health endpoint.
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | CREATE | Initial runtime and test dependencies compatible with AGENTS commands. |
| `app/__init__.py` | CREATE | Mark the application package and define shared service/version constants. |
| `app/main.py` | CREATE | FastAPI app factory and module-level `app` entry point for Uvicorn. |
| `app/api/__init__.py` | CREATE | Mark API route package. |
| `app/api/routes_health.py` | CREATE | Implement the `/health` API route. |
| `app/connectors/__init__.py` | CREATE | Reserve connector boundary for later Steam stories. |
| `app/storage/__init__.py` | CREATE | Reserve storage boundary for later OSS story. |
| `app/db/__init__.py` | CREATE | Reserve database boundary for later RDS story. |
| `app/llm/__init__.py` | CREATE | Reserve LLM boundary for later Qwen story. |
| `app/rag/__init__.py` | CREATE | Reserve RAG boundary for later Knowledge Base story. |
| `app/analysis/__init__.py` | CREATE | Reserve analysis boundary for later classification, clustering, and patch-linking stories. |
| `app/reports/__init__.py` | CREATE | Reserve report generation boundary for later brief/community response stories. |
| `app/services/__init__.py` | CREATE | Reserve orchestration boundary for later analysis pipeline story. |
| `streamlit_app.py` | CREATE | Minimal dashboard shell that imports Streamlit and loads without credentials. |
| `tests/test_health.py` | CREATE | Smoke test for the FastAPI health endpoint. |
| `README.md` | UPDATE | Replace template-only text with minimal MetaMood setup and scaffold commands once the app exists. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add Initial Dependency Metadata

- **File**: `requirements.txt`
- **Action**: CREATE
- **Implement**: Add the minimal dependencies for this story: `fastapi`, `uvicorn[standard]`, `streamlit`, `pytest`, and `httpx`. Include `pydantic` explicitly because later domain schemas depend on it and it is part of the planned stack.
- **Mirror**: `AGENTS.md:55` - expected install, backend, dashboard, and test commands assume `requirements.txt`.
- **Validate**: `python -m pip install -r requirements.txt`

### Task 2: Create the Application Package Boundaries

- **File**: `app/__init__.py`, `app/api/__init__.py`, `app/connectors/__init__.py`, `app/storage/__init__.py`, `app/db/__init__.py`, `app/llm/__init__.py`, `app/rag/__init__.py`, `app/analysis/__init__.py`, `app/reports/__init__.py`, `app/services/__init__.py`
- **Action**: CREATE
- **Implement**: Create all planned package directories with `__init__.py` files so the boundaries are importable and tracked. Define `SERVICE_NAME = "metamood"` and `APP_VERSION = "0.1.0"` in `app/__init__.py`; leave other package initializers empty or with one short package docstring.
- **Mirror**: `AGENTS.md:105` and `.agents/PRDs/metamood-mvp.prd.md:215` - target folder structure and module boundaries.
- **Validate**: `python -m pytest`

### Task 3: Implement the Health Route

- **File**: `app/api/routes_health.py`
- **Action**: CREATE
- **Implement**: Create an `APIRouter`, expose `GET /health`, and return exactly `{"status": "ok", "service": "metamood", "version": "0.1.0"}` using the constants from `app/__init__.py`.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:852` - health response contract.
- **Validate**: `python -m pytest`

### Task 4: Add the FastAPI Entry Point

- **File**: `app/main.py`
- **Action**: CREATE
- **Implement**: Create `create_app() -> FastAPI`, set the app title to `MetaMood`, set version `0.1.0`, include the health router, and expose a module-level `app = create_app()` for Uvicorn.
- **Mirror**: `AGENTS.md:142` and `AGENTS.md:153` - route contracts and thin API handlers.
- **Validate**: `python -m uvicorn app.main:app --reload`

### Task 5: Add a Minimal Streamlit Shell

- **File**: `streamlit_app.py`
- **Action**: CREATE
- **Implement**: Add a small Streamlit entry point with page config, MetaMood title, and a basic Game Monitor shell. Do not read live cloud credentials, do not call backend services, and do not implement future dashboard pages in this story.
- **Mirror**: `.agents/stories/metamood-mvp.stories.md:52` and `.agents/stories/metamood-mvp.stories.md:59` - minimal shell, Streamlit stays thin.
- **Validate**: `python -m streamlit run streamlit_app.py`

### Task 6: Add the Health Smoke Test

- **File**: `tests/test_health.py`
- **Action**: CREATE
- **Implement**: Use `fastapi.testclient.TestClient` against `app.main.app`, request `/health`, assert HTTP 200, and assert the exact JSON response.
- **Mirror**: `.agents/stories/metamood-mvp.stories.md:54` and `AGENTS.md:237` - health smoke test with no live external services.
- **Validate**: `python -m pytest`

### Task 7: Update the README for the Scaffold

- **File**: `README.md`
- **Action**: UPDATE
- **Implement**: Replace the template-only README content with a concise MetaMood overview and local setup commands for installing dependencies, running FastAPI, running Streamlit, and running tests. Keep full ECS, OSS, RDS, Qwen, and Knowledge Base setup for later stories.
- **Mirror**: `AGENTS.md:335` and `.agents/PRDs/metamood-mvp.prd.md:984` - README should reflect scaffolded entry points and phase 1 setup notes.
- **Validate**: `python -m pytest`

---

## Risks

| Risk | Mitigation |
|------|------------|
| The scaffold accidentally overreaches into future integration stories. | Create package boundaries only; implement only `/health`, Streamlit shell, dependency metadata, and smoke test. |
| Empty directories are not tracked by git. | Add `__init__.py` package files for all planned Python boundaries. |
| Health route response drifts from the PRD contract. | Test exact status code and exact JSON payload. |
| Streamlit shell starts requiring cloud configuration too early. | Keep it static for STORY-001 and avoid environment reads or backend calls. |
| Dependency metadata omits packages needed by the smoke test. | Include `httpx` so FastAPI/Starlette `TestClient` works in the default test environment. |

## Validation

Run these commands after implementation:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

Manual startup checks:

```bash
python -m uvicorn app.main:app --reload
python -m streamlit run streamlit_app.py
```

No lint, typecheck, or build command is configured yet.

## End-to-End Verification

- [ ] `python -m pytest` passes and verifies `GET /health`.
- [ ] Running `python -m uvicorn app.main:app --reload` exposes `/health`.
- [ ] A browser or HTTP client receives `{"status": "ok", "service": "metamood", "version": "0.1.0"}` from `/health`.
- [ ] Running `python -m streamlit run streamlit_app.py` loads the dashboard shell without Alibaba, Qwen, RDS, OSS, Knowledge Base, or Steam credentials.

## Acceptance Criteria

- [ ] All planned tasks completed.
- [ ] Relevant tests added or updated.
- [ ] Validation commands pass.
- [ ] End-to-end verification passes.
- [ ] Implementation follows `AGENTS.md`.
- [ ] GitHub issue #1 acceptance criteria are satisfied.
