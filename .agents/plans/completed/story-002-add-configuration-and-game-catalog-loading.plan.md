# Plan: Add Configuration and Game Catalog Loading

## Summary

Implement STORY-002 by adding a typed configuration layer for app settings and the Steam game catalog, a `config/games.yaml` MVP catalog, a backend `GET /games` route that returns only enabled games, and a `.env.example` covering the required Alibaba Cloud, Qwen, RDS, Knowledge Base, Steam, and dev/test settings. The implementation should keep cloud credentials optional for local tests, validate catalog data with Pydantic, and preserve the current thin FastAPI route pattern.

## User Story

As a live-ops producer, I want MetaMood to load a configured Steam game catalog, so that I can select enabled games for analysis.

## Metadata

| Field | Value |
|-------|-------|
| Type | NEW_CAPABILITY |
| Complexity | MEDIUM |
| Systems Affected | FastAPI API, configuration loading, test suite, dependency metadata, documentation |
| GitHub Issue | #2, https://github.com/DaDanielL/MetaMood/issues/2 |
| Source PRD | `.agents/PRDs/metamood-mvp.prd.md` |
| Source Story | `.agents/stories/metamood-mvp.stories.md#STORY-002` |
| Current Branch | `main` |
| Working Tree | Clean at planning time |

---

## Feature Understanding

- **Problem**: MetaMood currently has a runnable scaffold, but no typed app settings, no Steam game catalog, and no `/games` endpoint for the dashboard to consume.
- **Scope**: Add local configuration primitives and the first catalog-driven backend endpoint. Do not implement Steam ingestion, Streamlit game selection, database persistence, OSS, Qwen, or Knowledge Base calls in this story.
- **Issue Acceptance Criteria**:
  - Add `config/games.yaml` with 3-5 enabled Steam games.
  - Implement config loading for app settings and game catalog entries.
  - Exclude disabled games from the game list returned to the UI/API.
  - Add `.env.example` with required app, Steam, OSS, RDS, Qwen, and Knowledge Base variables.
  - Add tests for valid catalog loading, disabled games, and missing required fields.

---

## Patterns to Follow

### Naming

```text
SOURCE: AGENTS.md:157
Use snake_case for Python modules, functions, variables, and config keys.
Use PascalCase for Pydantic and SQLAlchemy model classes.
Use explicit IDs in domain names such as game_id.
```

### Route Registration

```text
SOURCE: app/main.py:9
create_app() constructs FastAPI(title="MetaMood", version=APP_VERSION), includes route modules, and returns the application.
Add a games router import and include_router call next to the existing health router.
```

### Thin API Routes

```text
SOURCE: app/api/routes_health.py:7
Routes use APIRouter at module scope and small endpoint functions.
SOURCE: AGENTS.md:153
Keep API handlers thin and put orchestration outside route modules.
```

### Configuration and Secrets

```text
SOURCE: AGENTS.md:206
Use environment variables and .env.example; never hardcode keys.
Required groups: App, Qwen, OSS, RDS, Knowledge Base, Steam, Dev/test.
SOURCE: .agents/PRDs/metamood-mvp.prd.md:785
PRD provides the concrete .env.example values and defaults.
```

### Game Catalog Contract

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:297
config/games.yaml contains games with game_id, display_name, steam_appid, platform, and enabled.
Disabled games do not appear in the UI.
SOURCE: .agents/PRDs/metamood-mvp.prd.md:864
GET /games response includes game_id, display_name, steam_appid, and enabled.
```

### Pydantic Types

```text
SOURCE: .agents/PRDs/metamood-mvp.prd.md:1150
class GameConfig(BaseModel):
    game_id: str
    display_name: str
    steam_appid: int
    platform: str = "steam"
    enabled: bool = True
```

### Tests

```text
SOURCE: tests/test_health.py:7
Use pytest with FastAPI TestClient for endpoint smoke tests.
SOURCE: AGENTS.md:235
Default tests must not call live Qwen, OSS, RDS, Bailian Knowledge Base, or Steam endpoints.
```

---

## Files to Change

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | UPDATE | Add `PyYAML` for catalog parsing and `python-dotenv` for local `.env` loading. |
| `.env.example` | CREATE | Document required app, Qwen, OSS, RDS, Knowledge Base, Steam, and dev/test variables from the PRD. |
| `config/games.yaml` | CREATE | Provide the MVP Steam game catalog with 3 enabled games and at least 1 disabled example for filtering tests. |
| `app/config.py` | CREATE | Define typed app settings, catalog models, and loader/filter helper functions. |
| `app/api/routes_games.py` | CREATE | Add `GET /games` route that returns enabled catalog entries in the PRD response shape. |
| `app/main.py` | UPDATE | Register the games router alongside the health router. |
| `tests/test_config.py` | CREATE | Cover app settings loading, valid catalog loading, disabled-game filtering, and missing required catalog fields. |
| `tests/test_games.py` | CREATE | Cover `GET /games` response shape and disabled-game exclusion through FastAPI. |
| `README.md` | UPDATE | Add the new `/games` endpoint and mention `.env.example`/catalog setup briefly. |

---

## Implementation Design

### App Settings

Create `AppSettings` in `app/config.py` using Pydantic v2 `BaseModel`. Keep credential-like values optional or empty-safe so tests and local scaffold startup do not require real cloud credentials. Include fields for:

- App: `app_env`, `app_host`, `app_port`, `frontend_port`
- Qwen: `dashscope_api_key`, `qwen_base_url`, `qwen_model_classifier`, `qwen_model_reasoner`, `qwen_model_report`, `qwen_request_timeout_seconds`
- OSS: `alibaba_cloud_access_key_id`, `alibaba_cloud_access_key_secret`, `oss_endpoint`, `oss_region`, `oss_bucket_name`
- RDS: `database_url`
- Knowledge Base: `bailian_kb_enabled`, `bailian_kb_id`, `bailian_workspace_id`, `bailian_api_key`
- Steam: `steam_review_language`, `steam_review_max_pages`, `steam_review_num_per_page`, `steam_review_max_reviews`, `steam_review_type`, `steam_review_filter`
- Dev/test: `use_mock_qwen`, `use_mock_oss`, `use_mock_knowledge_base`

Implement `load_app_settings(env_file: Path | None = Path(".env")) -> AppSettings`:

- Call `load_dotenv(env_file, override=False)` when an env file exists.
- Read environment variables with safe PRD defaults for non-secret fields.
- Do not log or print loaded values.
- Let Pydantic validate int and bool fields.

### Game Catalog

Create Pydantic models in `app/config.py`:

- `GameConfig`: `game_id`, `display_name`, `steam_appid`, `platform="steam"`, `enabled=True`
- `GameCatalog`: `games: list[GameConfig]`

Implement:

- `load_game_catalog(path: Path = DEFAULT_GAME_CATALOG_PATH) -> GameCatalog`
- `load_enabled_games(path: Path = DEFAULT_GAME_CATALOG_PATH) -> list[GameConfig]`
- `game_to_public_payload(game: GameConfig) -> dict[str, str | int | bool]`

Validation and errors:

- Use `yaml.safe_load`.
- Use Pydantic validation for missing required fields.
- Raise a small `ConfigError` for missing files, non-mapping YAML, YAML parse failures, or validation failures.
- Preserve the original exception as `__cause__` where useful.
- Keep error messages actionable but avoid leaking secrets. Catalog paths are fine to include.

### API Route

Create `app/api/routes_games.py`:

- Use module-level `router = APIRouter()`.
- Add `@router.get("/games")`.
- Return `list[dict[str, str | int | bool]]` generated from `load_enabled_games()`.
- Catch `ConfigError` and raise `HTTPException(status_code=500, detail="Game catalog configuration is invalid.")`.
- Do not make Steam, OSS, RDS, Qwen, or Knowledge Base calls.

### Catalog Contents

Create `config/games.yaml` with 3 enabled Steam games from the PRD:

- `helldivers_2`, `HELLDIVERS 2`, appid `553850`
- `counter_strike_2`, `Counter-Strike 2`, appid `730`
- `dota_2`, `Dota 2`, appid `570`

Add one disabled Steam game to exercise filtering, for example:

- `team_fortress_2`, `Team Fortress 2`, appid `440`, `enabled: false`

Keep every entry explicit with `platform: "steam"` and `enabled: true/false`, even though the Pydantic model may provide defaults.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Adding config loading accidentally requires real Alibaba/Qwen/RDS credentials. | Make credential fields optional or empty-safe, and test settings loading without live credentials. |
| YAML parsing introduces a dependency that is not installed. | Add `PyYAML` to `requirements.txt` and include dependency install in validation. |
| `.env` loading is expected locally but not supported. | Add `python-dotenv` and load `.env` only when present. Keep environment variables as the source of truth. |
| `/games` response leaks internal fields or disabled entries. | Serialize public payloads explicitly and add endpoint tests that assert `platform` is omitted and disabled entries are absent. |
| Catalog validation errors are exposed with noisy internals. | Wrap loader failures in `ConfigError`; API returns a stable generic 500 detail while unit tests inspect direct loader behavior. |
| Updating Streamlit in this story expands scope. | Do not wire the dashboard selector yet; STORY-016 owns the Game Monitor UI. The API route prepares the backend contract. |

---

## Tasks

Execute in order. Each task is atomic and verifiable.

### Task 1: Add Config Dependencies

- **File**: `requirements.txt`
- **Action**: UPDATE
- **Implement**: Add bounded dependencies for `PyYAML` and `python-dotenv`.
- **Mirror**: `requirements.txt:1` - preserve one dependency per line with compatible version ranges.
- **Validate**: `python -m pip install -r requirements.txt`

### Task 2: Add Environment Example

- **File**: `.env.example`
- **Action**: CREATE
- **Implement**: Add the variable groups and defaults from PRD section 9, using empty placeholders for secrets and credential values.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:785` - copy the documented env shape without real credentials.
- **Validate**: `python -m pytest`

### Task 3: Add MVP Game Catalog

- **File**: `config/games.yaml`
- **Action**: CREATE
- **Implement**: Add 3 enabled Steam games and 1 disabled Steam game. Include `game_id`, `display_name`, `steam_appid`, `platform`, and `enabled` for every entry.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:303` - follow the documented YAML structure.
- **Validate**: `python -m pytest`

### Task 4: Implement Typed Settings and Catalog Loading

- **File**: `app/config.py`
- **Action**: CREATE
- **Implement**: Add `AppSettings`, `GameConfig`, `GameCatalog`, `ConfigError`, `load_app_settings`, `load_game_catalog`, `load_enabled_games`, and `game_to_public_payload`.
- **Mirror**: `.agents/PRDs/metamood-mvp.prd.md:1150` - use the PRD `GameConfig` fields; `AGENTS.md:206` - source app settings from environment variables.
- **Validate**: `python -m pytest`

### Task 5: Add Games API Route

- **File**: `app/api/routes_games.py`
- **Action**: CREATE
- **Implement**: Add `GET /games`, load enabled games through `app.config`, serialize the public response shape, and convert `ConfigError` into a stable HTTP 500 response.
- **Mirror**: `app/api/routes_health.py:7` - module-level router and small endpoint function; `.agents/PRDs/metamood-mvp.prd.md:864` - response fields.
- **Validate**: `python -m pytest`

### Task 6: Register Games Router

- **File**: `app/main.py`
- **Action**: UPDATE
- **Implement**: Import the games router and include it in `create_app()` next to the health router.
- **Mirror**: `app/main.py:6` and `app/main.py:12` - existing router import and `include_router` pattern.
- **Validate**: `python -m pytest`

### Task 7: Add Config Unit Tests

- **File**: `tests/test_config.py`
- **Action**: CREATE
- **Implement**: Test valid catalog loading from `tmp_path`, disabled-game filtering, missing required field failure, and app settings env override/default loading without credentials.
- **Mirror**: `tests/test_health.py:7` - concise pytest tests with direct assertions.
- **Validate**: `python -m pytest`

### Task 8: Add Games Endpoint Tests

- **File**: `tests/test_games.py`
- **Action**: CREATE
- **Implement**: Use `TestClient(app)` to call `/games`; assert status 200, enabled games only, required public fields, and no `platform` field in the public response.
- **Mirror**: `tests/test_health.py:8` - FastAPI `TestClient` smoke style.
- **Validate**: `python -m pytest`

### Task 9: Update README API Notes

- **File**: `README.md`
- **Action**: UPDATE
- **Implement**: Add a short note that `.env.example` documents local settings, `config/games.yaml` contains the MVP catalog, and `GET /games` returns enabled games.
- **Mirror**: `README.md:40` - current compact API documentation style.
- **Validate**: `python -m pytest`

---

## Validation

Run these commands after implementation:

```bash
python -m pip install -r requirements.txt
python -m pytest
```

No lint, typecheck, or build command is configured yet.

## End-to-End Verification

- [ ] Start the backend with `python -m uvicorn app.main:app --reload`.
- [ ] Visit or request `GET /health`; expect the existing service metadata response to remain unchanged.
- [ ] Visit or request `GET /games`; expect a JSON list containing only enabled games from `config/games.yaml`.
- [ ] Confirm the disabled catalog entry does not appear in the `/games` response.
- [ ] Confirm the `/games` response uses the PRD public fields: `game_id`, `display_name`, `steam_appid`, `enabled`.

## Acceptance Criteria

- [ ] `config/games.yaml` exists with 3-5 enabled Steam games.
- [ ] Typed config loading exists for app settings and game catalog entries.
- [ ] Disabled games are excluded from the `GET /games` response.
- [ ] `.env.example` exists with required app, Steam, OSS, RDS, Qwen, and Knowledge Base variables.
- [ ] Tests cover valid catalog loading, disabled games, and missing required fields.
- [ ] Validation commands pass.
- [ ] Implementation follows `AGENTS.md`.
