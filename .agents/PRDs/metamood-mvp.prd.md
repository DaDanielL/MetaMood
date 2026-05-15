# PRD: MetaMood MVP

## 1. Executive Summary

MetaMood is an Alibaba Cloud AI MaaS demo for live-service game teams. It automatically detects a selected game's latest Steam update, collects recent public player feedback, stores raw and structured data on Alibaba Cloud services, uses Bailian / Model Studio Knowledge Base for retrieval-augmented generation over patch context, and calls Qwen API to generate patch-linked issue clusters and live-ops briefs.

The core value proposition is patch impact intelligence. Generic sentiment dashboards can show whether players are happy or unhappy, but MetaMood is designed to answer operational questions: which complaints are l ikely tied to the latest patch, which issues are high severity versus merely high volume, and what evidence supports the conclusion.

The MVP goal is to build a credible Alibaba Cloud Solution Architect demo. The product should prove the end-to-end flow from automatic Steam ingestion to OSS/RDS persistence, Bailian / Model Studio Knowledge Base RAG, Qwen reasoning, Streamlit dashboard display, and ECS deployment documentation, while keeping future integrations and fine-tuning out of the critical path.

## 2. Mission

MetaMood's mission is to help live-service game teams turn messy post-patch public feedback into evidence-grounded, team-routable live-ops decisions using Alibaba Cloud AI MaaS and cloud-native storage.

Core principles:

1. Automatic ingestion first: the main MVP flow starts with selecting a configured game and running analysis, not manual file upload.
2. Evidence-grounded outputs: every recommendation should trace back to player feedback and retrieved patch context.
3. Alibaba Cloud fluency: the MVP should clearly demonstrate Model Studio / Bailian, Qwen, OSS, RDS, ECS, and future PAI usage.
4. Mockable service boundaries: Steam, OSS, RDS, Qwen, and Knowledge Base integrations must be replaceable in tests and local development.
5. Honest capability claims: the app must not claim internal telemetry, production Knowledge Base access, or fine-tuned model behavior unless those capabilities are actually configured.

## 3. Target Users

### Primary Persona: Live-Ops Producer

Technical comfort level: moderate. Comfortable with dashboards, issue prioritization, reports, and stakeholder summaries.

Needs and pain points:

- Understand what players are reacting to after a patch.
- Identify high-priority issues quickly.
- Separate high-severity problems from high-volume noise.
- See representative evidence and recommended next actions.

### Secondary Persona: Community Manager

Technical comfort level: low to moderate. Comfortable editing generated drafts and reviewing risk notes.

Needs and pain points:

- Know the main player concerns after an update.
- Draft public responses that acknowledge frustration without overpromising.
- Avoid defensive tone or unsupported claims.
- Identify issues likely to damage player trust.

### Secondary Persona: Game Designer

Technical comfort level: moderate to high. Comfortable with patch notes, balance changes, and telemetry follow-up questions.

Needs and pain points:

- Understand balance, progression, rewards, monetization, and content complaints.
- See which complaints appear connected to recent patch changes.
- Review representative quotes before proposing hotfix candidates.
- Avoid confusing anecdotal feedback with confirmed internal metrics.

### Secondary Persona: QA / Engineering Lead

Technical comfort level: high. Comfortable with triage, reproducibility clues, logs, and technical severity.

Needs and pain points:

- Identify crash, bug, performance, and platform issue clusters.
- Prioritize critical technical issues even when volume is lower.
- Extract reproducibility hints from public comments.
- Escalate issues with clear evidence.

### Demo Persona: Alibaba Cloud Solution Architect

Technical comfort level: high. Comfortable discussing cloud architecture, service tradeoffs, and implementation strategy.

Needs and pain points:

- Present a concrete vertical AI MaaS use case.
- Explain why Qwen and RAG are useful for the client problem.
- Map OSS, RDS, ECS, Model Studio / Bailian, Knowledge Base, and PAI to business needs.
- Discuss cost, latency, scaling, and production hardening.

## 4. MVP Scope

### In Scope

#### Core Functionality

- [ ] Select a game from a configured Steam catalog.
- [ ] Automatically fetch recent Steam News posts for the selected game.
- [ ] Detect the latest likely patch/update post using keyword rules.
- [ ] Clean patch note content into plain text.
- [ ] Automatically fetch recent Steam reviews after the detected patch date.
- [ ] Normalize patch events and feedback items into typed schemas.
- [ ] Classify feedback by theme, sentiment, severity, actionability, player trust risk, owner team, confidence, and rationale.
- [ ] Group classified feedback into issue clusters.
- [ ] Score urgency using deterministic weights.
- [ ] Retrieve patch context for top issue clusters.
- [ ] Generate a Patch Impact Graph.
- [ ] Generate a Live-Ops Intelligence Brief.

#### Technical

- [ ] FastAPI backend.
- [ ] Streamlit MVP dashboard.
- [ ] Pydantic domain schemas.
- [ ] SQLAlchemy models for structured storage.
- [ ] Alembic migrations or deterministic table creation.
- [ ] Prompt versioning for all Qwen tasks.
- [ ] Model run metadata tracking.
- [ ] Mocked tests for external service boundaries.
- [ ] README setup and architecture documentation.

#### Integration

- [ ] Alibaba Cloud OSS wrapper for raw API responses, processed patch docs, report artifacts, and fine-tuning exports.
- [ ] ApsaraDB RDS PostgreSQL-compatible storage through `DATABASE_URL`.
- [ ] Qwen API wrapper through Alibaba Cloud Model Studio OpenAI-compatible configuration.
- [ ] Bailian / Model Studio Knowledge Base adapter for RAG.
- [ ] Local mock Knowledge Base adapter for development and tests only.
- [ ] Steam News connector.
- [ ] Steam Reviews connector.

#### Deployment

- [ ] Local development instructions.
- [ ] ECS deployment notes.
- [ ] Environment variable setup.
- [ ] Security group and health check notes.
- [ ] Guidance for connecting ECS to OSS, RDS, Qwen, and Knowledge Base where account access is available.

### Out of Scope

#### Product

- [ ] Full production authentication.
- [ ] Multi-user enterprise RBAC.
- [ ] Manual upload-first workflow.
- [ ] Real-time streaming ingestion.
- [ ] Discord ingestion.
- [ ] Reddit ingestion.
- [ ] YouTube ingestion.
- [ ] Support ticket ingestion.
- [ ] Before/after hotfix comparison.
- [ ] Full frontend polish.

#### AI / ML

- [ ] Actual PAI fine-tuning job.
- [ ] Wan video generation.
- [ ] Advanced embeddings or semantic clustering.
- [ ] Claims based on internal telemetry unless telemetry is provided.

#### Infrastructure

- [ ] Kubernetes deployment.
- [ ] Multi-region deployment.
- [ ] Complex microservices architecture.
- [ ] Production-grade monitoring and alerting.
- [ ] Production secrets manager integration beyond environment variables for MVP.

## 5. User Stories

1. As a live-ops producer, I want to select a game and analyze its latest update, so that I can quickly understand post-patch player reaction without manually gathering comments.

   Example: I select `HELLDIVERS 2`, click **Analyze Latest Update**, and see the detected patch plus the number of reviews analyzed.

2. As a live-ops producer, I want feedback grouped into issue clusters, so that I can focus on the most important themes instead of reading hundreds of reviews.

   Example: MetaMood groups reviews into clusters such as loading-screen crashes, weapon balance complaints, and reward progression frustration.

3. As a game designer, I want issue clusters linked to retrieved patch-note context, so that I can assess whether player complaints are likely tied to specific patch changes.

   Example: A weapon complaint links to the patch section that changed weapon damage or fire rate.

4. As a QA / engineering lead, I want urgency scoring to account for severity and actionability, so that critical technical problems can outrank low-severity high-volume complaints.

   Example: 18 crash reports can outrank 67 low-severity complaints if the crash cluster is critical and actionable.

5. As a community manager, I want a public response draft and risk check, so that I can respond calmly without overpromising fixes or timelines.

   Example: The draft acknowledges frustration and says the team is investigating, but does not claim a hotfix is confirmed unless that information was supplied.

6. As an Alibaba Cloud Solution Architect, I want the dashboard to explain the service architecture, so that I can present how ECS, OSS, RDS, Model Studio / Bailian, Qwen, Knowledge Base, and PAI fit together.

   Example: The Alibaba Architecture page maps each service to a role in the client solution.

7. As a developer, I want each cloud and model integration behind an adapter, so that default tests run locally without live Qwen, OSS, RDS, Knowledge Base, or Steam calls.

   Example: Tests use mock OSS, mock Qwen, SQLite or a local test database, fixture Steam responses, and `LocalMockKnowledgeBaseClient`.

8. As a developer, I want prompt versions and model run metadata stored, so that generated outputs remain traceable across model and prompt changes.

   Example: A classification stores `model_name=qwen-plus`, `prompt_version=classify_feedback_v1`, token estimates, latency, status, and error metadata.

## 6. Core Architecture & Patterns

### High-Level Architecture

```text
Steam News API / Steam Reviews API
        |
        v
FastAPI backend on Alibaba Cloud ECS
        |
        +--> OSS bucket for raw JSON, processed docs, generated reports
        |
        +--> ApsaraDB RDS PostgreSQL for structured records
        |
        +--> Bailian / Model Studio Knowledge Base for patch-note RAG
        |
        +--> Qwen API through Model Studio for classification and reasoning
        |
        v
Streamlit dashboard
```

### Recommended Repository Structure

```text
metamood/
|-- AGENTS.md
|-- README.md
|-- .env.example
|-- requirements.txt
|-- pyproject.toml
|-- streamlit_app.py
|-- config/
|   `-- games.yaml
|-- app/
|   |-- __init__.py
|   |-- main.py
|   |-- config.py
|   |-- schemas.py
|   |-- api/
|   |   |-- routes_health.py
|   |   |-- routes_games.py
|   |   |-- routes_analysis.py
|   |   `-- routes_reports.py
|   |-- connectors/
|   |   |-- steam_news.py
|   |   `-- steam_reviews.py
|   |-- storage/
|   |   |-- oss_client.py
|   |   `-- object_keys.py
|   |-- db/
|   |   |-- models.py
|   |   |-- session.py
|   |   `-- repositories.py
|   |-- llm/
|   |   |-- qwen_client.py
|   |   |-- prompts.py
|   |   `-- output_parsers.py
|   |-- rag/
|   |   |-- knowledge_base_client.py
|   |   |-- bailian_client.py
|   |   `-- local_mock_client.py
|   |-- analysis/
|   |   |-- classify_feedback.py
|   |   |-- cluster_issues.py
|   |   |-- urgency.py
|   |   `-- patch_linking.py
|   |-- reports/
|   |   |-- live_ops_brief.py
|   |   |-- community_response.py
|   |   `-- serializers.py
|   `-- services/
|       `-- analysis_pipeline.py
|-- tests/
|   |-- fixtures/
|   |   |-- steam_news_response.json
|   |   `-- steam_reviews_response_page_1.json
|   |-- test_game_config.py
|   |-- test_steam_news.py
|   |-- test_steam_reviews.py
|   |-- test_oss_keys.py
|   |-- test_urgency.py
|   |-- test_output_parsers.py
|   `-- test_analysis_pipeline_mocked.py
`-- .agents/
    |-- PRDs/
    |-- stories/
    |-- plans/
    |-- reports/
    `-- reviews/
```

### Key Patterns

- Adapter pattern for external services.
- Repository pattern for database writes, reads, and deduplication.
- Typed schemas for domain objects and LLM outputs.
- Prompt version constants for every Qwen task.
- Deterministic scoring before advanced model behavior.
- Mock-first test strategy for all cloud and external integrations.
- Explicit failure behavior for production Knowledge Base unavailability.

## 7. Tools / Features

### 7.1 Game Catalog

MetaMood should maintain a small configured Steam game catalog for MVP in `config/games.yaml`.

Example:

```yaml
games:
  - game_id: "helldivers_2"
    display_name: "HELLDIVERS 2"
    steam_appid: 553850
    platform: "steam"
    enabled: true

  - game_id: "counter_strike_2"
    display_name: "Counter-Strike 2"
    steam_appid: 730
    platform: "steam"
    enabled: true

  - game_id: "dota_2"
    display_name: "Dota 2"
    steam_appid: 570
    platform: "steam"
    enabled: true
```

Acceptance criteria:

- User can select a configured game.
- Each game has `game_id`, `display_name`, `steam_appid`, `platform`, and `enabled`.
- Disabled games do not appear in the UI.
- Tests validate config loading.

### 7.2 Steam News Connector

Fetch recent Steam News posts for a selected game and detect likely patch/update posts.

Inputs:

- `steam_appid`
- `count`
- `maxlength`
- optional `enddate`

Patch detection keywords:

```python
PATCH_KEYWORDS = [
    "patch",
    "hotfix",
    "update",
    "balance",
    "release notes",
    "maintenance",
    "season",
    "major update",
    "minor update",
    "bug fix",
]
```

Acceptance criteria:

- Backend calls Steam News API for selected app ID.
- Backend fetches at least the most recent 10-20 news posts.
- Backend detects likely patch/update posts using keyword rules.
- Backend selects the newest matching post.
- Backend cleans HTML/BBCode-like content into plain text.
- Backend stores raw response in OSS.
- Backend stores normalized patch event in RDS.
- Tests cover patch keyword detection, date parsing, and normalization.

### 7.3 Steam Reviews Connector

Fetch recent Steam reviews for the selected game after the latest patch date.

MVP defaults:

```env
STEAM_REVIEW_LANGUAGE=english
STEAM_REVIEW_MAX_PAGES=5
STEAM_REVIEW_NUM_PER_PAGE=100
STEAM_REVIEW_MAX_REVIEWS=500
STEAM_REVIEW_TYPE=all
STEAM_REVIEW_FILTER=recent
```

Acceptance criteria:

- Backend fetches review pages using cursor pagination.
- Backend limits request volume with configurable max pages/reviews.
- Backend filters reviews to those created after the detected patch date when possible.
- Backend normalizes review text, vote, helpful votes, playtime, created timestamp, language, and external ID.
- Backend stores raw response pages in OSS.
- Backend stores normalized feedback records in RDS.
- Tests cover pagination handling, duplicate prevention, and timestamp filtering.

### 7.4 OSS Storage

Use Alibaba Cloud OSS to store raw API responses, processed patch documents, generated report artifacts, and future fine-tuning dataset exports.

Required OSS paths:

```text
raw/steam_news/{game_id}/{patch_id}/{timestamp}.json
raw/steam_reviews/{game_id}/{patch_id}/page_{page_number}_{timestamp}.json
processed/patch_notes/{game_id}/{patch_id}/patch_notes.txt
processed/rag_docs/{game_id}/{patch_id}/{document_name}.txt
reports/{game_id}/{patch_id}/live_ops_brief.md
reports/{game_id}/{patch_id}/action_board.json
reports/{game_id}/{patch_id}/community_response.md
exports/fine_tuning/{game_id}/{patch_id}/classification_dataset.jsonl
```

Acceptance criteria:

- OSS client reads credentials from environment variables.
- App uploads raw Steam News responses to OSS.
- App uploads raw Steam Review response pages to OSS.
- App uploads cleaned patch notes to OSS.
- App uploads generated reports to OSS.
- App stores OSS object keys in RDS.
- Tests use a mock OSS adapter, not live OSS calls.

### 7.5 RDS PostgreSQL Storage

Use ApsaraDB RDS PostgreSQL as the structured application database.

Required tables:

- `games`: configured games.
- `patch_events`: detected updates and patch notes.
- `feedback_items`: normalized player feedback.
- `feedback_classifications`: Qwen classification results.
- `issue_clusters`: grouped issues.
- `patch_links`: RAG-supported issue-to-patch links.
- `live_ops_reports`: generated briefs and report metadata.
- `model_runs`: Qwen / AI run tracking.

Acceptance criteria:

- SQLAlchemy models exist for all core tables.
- Alembic migrations or deterministic table creation exists.
- Application can connect to local PostgreSQL for development and ApsaraDB RDS for deployment.
- `DATABASE_URL` is loaded from environment variables.
- Duplicate Steam records are prevented by unique constraints on source/external ID.
- Tests use a local test database or SQLite adapter when appropriate.

### 7.6 Bailian / Model Studio Knowledge Base RAG

Use Bailian / Model Studio Knowledge Base as the intended primary RAG system. Patch notes, known issues, community response guidelines, and game design policy snippets should be indexed or prepared for retrieval.

MVP documents:

```text
latest_patch_notes.txt
known_issues.txt
community_response_guidelines.txt
game_design_policy.txt
```

Required adapter interface:

```python
class KnowledgeBaseClient(Protocol):
    def index_document(
        self,
        *,
        game_id: str,
        patch_id: str,
        title: str,
        content: str,
        oss_key: str | None = None,
    ) -> str:
        ...

    def retrieve(
        self,
        *,
        query: str,
        game_id: str,
        patch_id: str,
        top_k: int = 5,
    ) -> list[RetrievedContext]:
        ...
```

Implementations:

1. `BailianKnowledgeBaseClient`: primary implementation.
2. `LocalMockKnowledgeBaseClient`: testing and development fallback only.

Acceptance criteria:

- Patch notes are stored in OSS.
- Patch notes are indexed into Bailian / Model Studio Knowledge Base when access is available.
- App retrieves patch context for issue clusters.
- Retrieved context is passed into Qwen prompts.
- Final report includes retrieved patch evidence.
- Tests use local mock knowledge base retrieval.
- README documents setup steps and access limitations.

### 7.7 Qwen API Integration

Use Alibaba Cloud Model Studio Qwen API as the MaaS inference layer.

Required Qwen tasks:

1. Feedback classification.
2. Issue summarization.
3. Patch-link reasoning.
4. Live-ops brief generation.

Environment variables:

```env
DASHSCOPE_API_KEY=
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_CLASSIFIER=qwen-plus
QWEN_MODEL_REASONER=qwen-plus
QWEN_MODEL_REPORT=qwen-plus
QWEN_REQUEST_TIMEOUT_SECONDS=60
```

Prompt versions:

```python
PROMPT_VERSION_CLASSIFY_FEEDBACK = "classify_feedback_v1"
PROMPT_VERSION_PATCH_LINK = "patch_link_v1"
```

Acceptance criteria:

- Qwen client uses environment variables.
- API keys are never hardcoded.
- Qwen calls are wrapped in a service class.
- Qwen failures produce typed errors.
- Prompt versions are tracked.
- Model name and prompt version are stored in RDS for generated outputs.
- Tests mock Qwen responses.

### 7.8 Feedback Classification

Classify each feedback item into structured labels.

Required output schema:

```json
{
  "theme": "balance",
  "sentiment": "negative",
  "severity": "high",
  "actionability": "medium",
  "player_trust_risk": "low",
  "owner_team": "Combat Design",
  "confidence": 0.82,
  "rationale": "The player complains that a weapon is overpowered in ranked gameplay."
}
```

Theme labels:

```text
bug
crash
performance
matchmaking
balance
monetization
rewards
progression
new_content
toxicity_safety
localization
praise
other
```

Owner teams:

```text
QA / Engineering
Combat Design
Economy Design
Live Ops
Community
Player Safety
Localization
Marketing
Product Analytics
Unknown
```

Acceptance criteria:

- Feedback classification returns valid JSON.
- Invalid Qwen output is repaired or rejected safely.
- Each classification is stored in RDS.
- Classification prompt is versioned.
- Tests cover schema validation.

### 7.9 Issue Clustering and Urgency Scoring

MVP clustering should use a simple grouping approach first:

```text
theme + sentiment + repeated keywords + representative Qwen summary
```

Urgency formula:

```text
urgency_score =
  severity_weight
+ volume_weight
+ actionability_weight
+ player_trust_risk_weight
+ patch_link_confidence_weight
+ gameplay_blocking_bonus
```

Acceptance criteria:

- Classifications are grouped into issue clusters.
- Cluster volume is calculated.
- Representative quotes are selected.
- Severity and actionability are aggregated.
- Owner team is assigned.
- Lower-volume critical issues can outrank higher-volume low-severity complaints.
- Results are stored in RDS and displayed in the Team Action Board.

### 7.10 Patch Impact Graph

Show how patch changes connect to player issue clusters.

Each graph entry should include:

```text
Patch Change
Detected Player Reaction
Evidence
Patch-Link Confidence
Suggested Owner
Recommended Action
```

Acceptance criteria:

- For each top issue, retrieve relevant patch context.
- Qwen assesses whether the issue is likely patch-linked.
- Output includes retrieved patch evidence.
- Output includes confidence and reasoning.
- Output includes owner team and recommended action.
- Display appears in dashboard.

### 7.11 Team Action Board

Generate a table of recommended actions grouped by owner team.

Columns:

```text
Owner Team
Priority
Issue
Evidence
Patch Link
Recommended Action
Suggested Timeline
```

Acceptance criteria:

- Generated from issue clusters and patch links.
- Ordered by urgency.
- Stored in report JSON.
- Displayed in dashboard.

### 7.12 Live-Ops Intelligence Brief

Generate a concise stakeholder brief with:

1. Executive Summary.
2. Latest Update Detected.
3. Data Sources Analyzed.
4. Top Player Pain Points.
5. Patch-Linked Issues.
6. Critical / High-Severity Issues.
7. Team Action Board.
8. Recommended Community Response.
9. Follow-Up Metrics to Monitor.
10. Limitations and Confidence Notes.

Acceptance criteria:

- Brief is generated by Qwen using structured context.
- Brief cites representative feedback and retrieved patch context.
- Brief avoids unsupported claims.
- Brief does not say internal telemetry confirms something unless telemetry was provided.
- Brief is saved to OSS as Markdown.
- Report metadata is stored in RDS.

### 7.13 Community Response Draft

Generate a public-facing draft response that community managers can edit.

Tone rules:

- Acknowledge player frustration.
- Avoid overpromising fix dates.
- Avoid defensive tone.
- Mention active investigation when appropriate.
- Focus on the top issues.
- Do not claim fixes are coming unless confirmed.
- Do not blame players.

Risk checker questions:

- Does the response overpromise?
- Does it ignore the biggest issue?
- Is the tone defensive?
- Does it acknowledge frustration?
- Does it include unsupported claims?

Acceptance criteria:

- Community response is generated.
- Risk check returns `pass`, `warn`, or `fail`.
- Warnings are displayed.
- Draft is saved in RDS and OSS.

### 7.14 Dashboard

MVP frontend should use Streamlit.

Required pages:

1. Game Monitor: game selection, app ID, analyze button, backend health, Alibaba service configuration status.
2. Latest Update: detected update title, published date, source, patch note preview, OSS key, RAG indexing status.
3. Player Signal Dashboard: reviews fetched, reviews after patch, sentiment split, top themes, severity distribution, representative quotes.
4. Patch Impact Graph: patch change, player reaction cluster, retrieved context, confidence, recommended action.
5. Team Action Board: owner team, priority, issue, evidence, recommended action, timeline.
6. Live-Ops Brief: generated Markdown report, report OSS key, community response draft, risk checker output.
7. Alibaba Architecture: architecture diagram and explanation of ECS, OSS, RDS, Model Studio / Bailian, Qwen, Knowledge Base, and PAI.

Acceptance criteria:

- Dashboard runs locally.
- Dashboard can connect to ECS backend or local backend.
- Dashboard clearly shows automatic ingestion, not manual upload.
- Dashboard includes an Alibaba Architecture page.

## 8. Technology Stack

| Area | Technology | Purpose |
| --- | --- | --- |
| Backend | Python 3.11+ and FastAPI | API and orchestration |
| Frontend | Streamlit | MVP dashboard |
| Schemas | Pydantic | Domain and LLM output validation |
| Database ORM | SQLAlchemy | RDS PostgreSQL models and persistence |
| Migrations | Alembic or deterministic table creation | Database setup |
| Database | ApsaraDB RDS PostgreSQL | Structured records |
| Object Storage | Alibaba Cloud OSS Python SDK | Raw files, processed docs, reports, exports |
| LLM | Qwen through Model Studio / DashScope-compatible API | MaaS classification and reasoning |
| RAG | Bailian / Model Studio Knowledge Base | Patch context retrieval |
| Test RAG | Local mock retrieval | Development and tests |
| Testing | pytest | Unit and mocked integration tests |
| Deployment | Alibaba Cloud ECS | Backend and optional dashboard hosting |
| Future ML | Alibaba Cloud PAI Model Gallery | Later LoRA / QLoRA classifier fine-tuning |

Optional dependencies:

- `httpx` or `requests` for Steam and API clients.
- `beautifulsoup4` or equivalent for HTML cleanup.
- `python-dotenv` for local environment loading.
- `psycopg2` or compatible PostgreSQL driver.

## 9. Security & Configuration

### Authentication and Authorization

MVP does not include production authentication, multi-user RBAC, or enterprise SSO. The initial version may run as a trusted internal demo. Production hardening is a future phase.

### Environment Variables

```env
# App
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_PORT=8501

# Qwen / Model Studio
DASHSCOPE_API_KEY=
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL_CLASSIFIER=qwen-plus
QWEN_MODEL_REASONER=qwen-plus
QWEN_MODEL_REPORT=qwen-plus
QWEN_REQUEST_TIMEOUT_SECONDS=60

# Alibaba Cloud OSS
ALIBABA_CLOUD_ACCESS_KEY_ID=
ALIBABA_CLOUD_ACCESS_KEY_SECRET=
OSS_ENDPOINT=
OSS_REGION=
OSS_BUCKET_NAME=

# ApsaraDB RDS PostgreSQL
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/metamood

# Bailian / Model Studio Knowledge Base
BAILIAN_KB_ENABLED=true
BAILIAN_KB_ID=
BAILIAN_WORKSPACE_ID=
BAILIAN_API_KEY=

# Steam
STEAM_REVIEW_LANGUAGE=english
STEAM_REVIEW_MAX_PAGES=5
STEAM_REVIEW_NUM_PER_PAGE=100
STEAM_REVIEW_MAX_REVIEWS=500
STEAM_REVIEW_TYPE=all
STEAM_REVIEW_FILTER=recent

# Dev/Test
USE_MOCK_QWEN=false
USE_MOCK_OSS=false
USE_MOCK_KNOWLEDGE_BASE=false
```

### Security Requirements

- Never hardcode API keys.
- Never print secrets in logs.
- Do not expose Alibaba access keys to the frontend.
- Steam API calls must be made from the backend.
- RDS credentials must come from environment variables.
- OSS bucket permissions should be least privilege.
- Do not store unnecessary personal user data.
- Do not deanonymize Steam users.
- Store only public review metadata needed for analysis.
- Community response drafts require human review before publishing.
- The system must not claim internal telemetry exists unless telemetry was actually provided.

### Error Handling Requirements

- Steam failures should return a clear error, log status code and endpoint type, avoid sensitive URLs, and allow retry.
- OSS failures should preserve local temporary data when possible, mark the analysis as a partial failure, and return an actionable error.
- RDS failures should roll back transactions and stop report generation if required records cannot be saved.
- Knowledge Base failures should use mock retrieval only in development and return a clear setup error in production.
- Qwen failures should retry where appropriate, store failed model run metadata, return useful UI errors, and never generate fake output.

## 10. API Specification

### `GET /health`

Response:

```json
{
  "status": "ok",
  "service": "metamood",
  "version": "0.1.0"
}
```

### `GET /games`

Response:

```json
[
  {
    "game_id": "helldivers_2",
    "display_name": "HELLDIVERS 2",
    "steam_appid": 553850,
    "enabled": true
  }
]
```

### `POST /analyze/latest`

Request:

```json
{
  "game_id": "helldivers_2",
  "max_reviews": 500
}
```

Response:

```json
{
  "analysis_run_id": "run_123",
  "game_id": "helldivers_2",
  "patch_event_id": "patch_456",
  "status": "completed",
  "report_id": "report_789"
}
```

### `GET /analysis/{analysis_run_id}`

Response:

```json
{
  "analysis_run_id": "run_123",
  "status": "running",
  "stage": "classifying_feedback",
  "progress": 0.65
}
```

### `GET /reports/{report_id}`

Response:

```json
{
  "report_id": "report_789",
  "game_id": "helldivers_2",
  "patch_title": "Patch 01.002.104",
  "executive_summary": "...",
  "team_action_board": [],
  "community_response": "...",
  "report_oss_key": "reports/..."
}
```

### `GET /reports/{report_id}/patch-impact-graph`

Response:

```json
[
  {
    "patch_change": "Adjusted weapon damage.",
    "player_reaction": "Players say the weapon is overpowered.",
    "evidence": ["..."],
    "patch_link_confidence": "high",
    "owner_team": "Combat Design",
    "recommended_action": "Review telemetry and prepare hotfix candidate if internal metrics support the player feedback."
  }
]
```

## 11. Success Criteria

MVP success means MetaMood can run a mocked or configured end-to-end analysis from game selection through report display while clearly demonstrating Alibaba Cloud AI MaaS architecture and preserving testability without live external calls.

Functional requirements:

- [ ] User can select a configured Steam game.
- [ ] App automatically detects the latest patch/update from Steam News.
- [ ] App automatically fetches recent Steam reviews.
- [ ] Raw Steam data is uploaded to OSS when configured.
- [ ] Structured patch, review, classification, cluster, patch-link, report, and model-run data is stored in RDS.
- [ ] Patch notes are indexed or prepared for Bailian / Model Studio Knowledge Base.
- [ ] RAG retrieval returns patch context for issue clusters.
- [ ] Qwen classifies feedback.
- [ ] Qwen generates patch-link reasoning.
- [ ] App displays issue clusters.
- [ ] App displays Patch Impact Graph.
- [ ] App displays Team Action Board.
- [ ] App generates Live-Ops Brief.
- [ ] App generates Community Response Draft and risk check.
- [ ] Backend can run on ECS.
- [ ] README explains Alibaba Cloud architecture and setup.
- [ ] Tests pass with mocked external services.
- [ ] Fine-tuning dataset export is documented or implemented as a lower-priority extension.

Quality indicators:

- Default tests do not call live Qwen, OSS, RDS, Knowledge Base, or Steam endpoints.
- External service failures produce typed, user-understandable errors.
- LLM output is validated before persistence.
- Reports cite representative feedback and retrieved context.
- The app avoids unsupported claims about internal telemetry.
- The demo can be explained in Solution Architect terms.

## 12. Implementation Phases

### Phase 1: Foundation and Alibaba Storage Plumbing

Goal: establish the app skeleton, schemas, game catalog, database, OSS abstraction, and local test setup.

Deliverables:

- [ ] FastAPI app with `/health`.
- [ ] Streamlit shell with Game Monitor page.
- [ ] `config/games.yaml`.
- [ ] `.env.example`.
- [ ] Pydantic schemas.
- [ ] SQLAlchemy models and database session setup.
- [ ] OSS client wrapper and mock client.
- [ ] Basic pytest setup.
- [ ] README setup notes.

Validation:

- Health endpoint returns expected response.
- Game catalog loads enabled games.
- Database models can be created in test mode.
- OSS path generation is deterministic.

Estimated duration: 1-2 weeks.

### Phase 2: Steam Automatic Ingestion

Goal: detect the latest Steam update and fetch post-patch reviews automatically.

Deliverables:

- [ ] Steam News connector.
- [ ] Patch keyword detection.
- [ ] Patch note cleanup.
- [ ] Steam Reviews connector with cursor pagination.
- [ ] Review timestamp filtering.
- [ ] Raw response storage to OSS.
- [ ] Normalized patch and feedback storage to RDS.
- [ ] Fixture-based tests.

Validation:

- Latest update detection works with fixture data.
- Review pagination, deduplication, and filtering are tested.
- Default tests make no live Steam calls.

Estimated duration: 1-2 weeks.

### Phase 3: Qwen Classification and Issue Analysis

Goal: classify feedback, cluster issues, and compute urgency using Qwen plus deterministic logic.

Deliverables:

- [ ] Qwen client and mock client.
- [ ] Prompt version constants.
- [ ] Strict JSON output parser.
- [ ] Feedback classification pipeline.
- [ ] Issue clustering.
- [ ] Urgency scoring.
- [ ] Model run logging.
- [ ] Tests for valid and invalid model output.

Validation:

- Classifications validate against schemas.
- Prompt version and model metadata are persisted.
- Urgency scoring tests prove severity can outrank volume.

Estimated duration: 1-2 weeks.

### Phase 4: RAG, Reporting, Dashboard, and Deployment

Goal: complete Knowledge Base integration, patch-link reasoning, report generation, dashboard pages, and ECS deployment guidance.

Deliverables:

- [ ] `KnowledgeBaseClient` interface.
- [ ] `BailianKnowledgeBaseClient`.
- [ ] `LocalMockKnowledgeBaseClient`.
- [ ] Patch note indexing or account-supported Knowledge Base workflow.
- [ ] Patch Impact Graph generation.
- [ ] Team Action Board generation.
- [ ] Live-Ops Brief generation.
- [ ] Community Response Draft and risk checker.
- [ ] Streamlit dashboard pages.
- [ ] ECS deployment documentation.
- [ ] PAI fine-tuning dataset export documentation or low-priority export utility.

Validation:

- Mocked end-to-end analysis run completes.
- Dashboard displays update, player signals, patch impact, action board, brief, community response, and Alibaba architecture.
- Knowledge Base access limitations are documented clearly.

Estimated duration: 2-3 weeks.

## 13. Future Considerations

- Reddit connector for subreddit search and comments.
- YouTube connector for update video comments.
- Discord or support ticket ingestion.
- Before/after hotfix comparison.
- Scheduled monitoring every 24 hours after detected patches.
- Embedding-based clustering and semantic deduplication.
- PAI fine-tuned classifier using exported Qwen-labeled feedback.
- Wan extension for patch recap scripts, storyboards, or short-form community updates.
- CloudMonitor, structured logs, alerting, and cost tracking.
- Production authentication, RBAC, audit logs, and enterprise deployment hardening.

## 14. Risks & Mitigations

### Risk 1: Bailian / Model Studio Knowledge Base Access Restrictions

Mitigation:

- Verify account access early.
- Build the Knowledge Base adapter interface regardless of live access.
- Use local mock retrieval only for development and tests.
- Document limitations honestly.
- In production mode, fail clearly if Knowledge Base access is required but unavailable.

### Risk 2: Steam API Instability or Rate Limits

Mitigation:

- Limit review pages and max reviews.
- Cache stored responses.
- Use fixture data for tests.
- Add retry/backoff.
- Avoid excessive requests.

### Risk 3: Qwen Output Is Not Valid JSON

Mitigation:

- Use strict JSON-only prompts.
- Validate outputs with Pydantic.
- Retry once with a correction prompt where appropriate.
- Store failed model run metadata.
- Reject or mark partial failure instead of generating fake output.

### Risk 4: Cloud Cost

Mitigation:

- Use small ECS instance for MVP.
- Limit review count.
- Cache repeated analysis outputs.
- Use controlled Qwen calls.
- Keep PAI fine-tuning out of MVP execution.

### Risk 5: Overbuilding

Mitigation:

- Steam-only ingestion first.
- Build cloud plumbing before UI polish.
- Implement one story at a time.
- Defer Reddit, YouTube, Discord, Wan, full observability, and actual fine-tuning.

## 15. Appendix

### Data Schemas

```python
class GameConfig(BaseModel):
    game_id: str
    display_name: str
    steam_appid: int
    platform: str = "steam"
    enabled: bool = True


class PatchEvent(BaseModel):
    game_id: str
    external_id: str
    source: str
    title: str
    published_at: datetime
    url: str | None = None
    raw_oss_key: str | None = None
    cleaned_text_oss_key: str | None = None
    content: str


class FeedbackItem(BaseModel):
    game_id: str
    patch_event_id: str | None = None
    source: str
    external_id: str
    text: str
    created_at_source: datetime
    url: str | None = None
    language: str | None = None
    positive: bool | None = None
    helpful_votes: int | None = None
    playtime_hours: float | None = None
    raw_oss_key: str | None = None


class RetrievedContext(BaseModel):
    source_title: str
    source_type: str
    content: str
    score: float | None = None
    knowledge_base_id: str | None = None


class IssueCluster(BaseModel):
    theme: str
    summary: str
    volume: int
    sentiment: str
    severity: str
    actionability: str
    player_trust_risk: str
    suggested_owner: str
    representative_quotes: list[str]
    urgency_score: float


class PatchLink(BaseModel):
    issue_cluster_id: str
    retrieved_context: list[RetrievedContext]
    patch_link_confidence: Literal["high", "medium", "low", "none"]
    reasoning: str


class LiveOpsReport(BaseModel):
    game_id: str
    patch_event_id: str
    title: str
    executive_summary: str
    top_risks: list[dict]
    team_action_board: list[dict]
    patch_impact_graph: list[dict]
    community_response: str
    limitations: list[str]
    report_oss_key: str | None = None
```

### Suggested Story Breakdown

1. STORY-001: Scaffold MetaMood Project.
2. STORY-002: Implement RDS Data Models.
3. STORY-003: Implement OSS Storage Client.
4. STORY-004: Implement Steam News Connector.
5. STORY-005: Implement Steam Reviews Connector.
6. STORY-006: Implement Qwen Client and Prompt Framework.
7. STORY-007: Implement Feedback Classification Pipeline.
8. STORY-008: Implement Issue Clustering and Urgency Scoring.
9. STORY-009: Implement Bailian Knowledge Base RAG Adapter.
10. STORY-010: Implement Patch Impact Graph.
11. STORY-011: Implement Live-Ops Brief and Community Response.
12. STORY-012: Implement Streamlit Dashboard.
13. STORY-013: Deploy Backend to ECS.
14. STORY-014: Export Fine-Tuning Dataset for PAI.

### Initial Build Recommendation

1. STORY-001: Scaffold project.
2. STORY-002: RDS data models.
3. STORY-003: OSS client.
4. STORY-004: Steam News connector.
5. STORY-005: Steam Reviews connector.
6. STORY-006: Qwen client.
7. STORY-007: Feedback classification.
8. STORY-009: Bailian Knowledge Base adapter.
9. STORY-010: Patch Impact Graph.
10. STORY-011: Live-Ops Brief.
11. STORY-012: Dashboard.
12. STORY-013: ECS deployment.
13. STORY-014: Fine-tuning dataset export.

Do not start with Streamlit visuals first. Build Alibaba cloud plumbing early because the main learning goal is Alibaba Cloud AI Solution Architecture, not only a local dashboard.

### Demo Script

Opening:

> MetaMood is an Alibaba Cloud AI MaaS demo for live-service gaming teams. Instead of manually uploading feedback, the app automatically detects the latest Steam update, fetches recent player reviews, and uses Qwen plus RAG over patch notes to generate live-ops recommendations.

Automatic ingestion:

> Here I select a game and click Analyze Latest Update. The backend fetches Steam News to identify the latest patch, then fetches Steam reviews after that patch.

Alibaba Cloud data flow:

> Raw API responses are stored in OSS, while structured comments, patch events, classifications, and generated reports are saved in ApsaraDB RDS PostgreSQL.

RAG:

> The cleaned patch notes are indexed into Bailian / Model Studio Knowledge Base. When the model sees a player complaint, it retrieves the relevant patch context before deciding whether the complaint is patch-linked.

Patch Impact Graph:

> This is the main unique feature. It connects a specific patch change to a detected player reaction, supporting evidence, confidence, owner team, and recommended action.

Team Action Board:

> The output is not just sentiment. It routes each issue to QA, Combat Design, Live Ops, Community, or Economy Design with priority and evidence.

Community response:

> The app also drafts a public-facing response and checks whether it overpromises or ignores major concerns.

Solution Architect close:

> I built this to practice the AI Solution Architect workflow: identify a vertical client use case, design the cloud architecture, choose the right Alibaba AI services, implement RAG and Qwen-based reasoning, and explain how the solution could scale.

### Source-Backed Implementation Assumptions

- Alibaba Cloud Model Studio supports Qwen API calls through OpenAI-compatible interfaces and DashScope SDK calls. MetaMood should use a Qwen client wrapper configured by `DASHSCOPE_API_KEY`, `QWEN_BASE_URL`, and model-specific environment variables. [Alibaba Cloud Model Studio Qwen quick start][1]
- Alibaba Cloud Model Studio Knowledge Base is a RAG capability for supplementing LLMs with private or up-to-date external knowledge. Documentation states document-search knowledge bases can use local uploads or import data from OSS. [Alibaba Cloud Model Studio Knowledge Base][2]
- Steam's `ISteamNews/GetNewsForApp/v2` endpoint retrieves news for a specified app ID and supports parameters such as `appid`, `maxlength`, `enddate`, `count`, and `feeds`. [Steamworks ISteamNews][3]
- Steam's review endpoint supports `GET store.steampowered.com/appreviews/<appid>?json=1` with filters, language, cursor pagination, review type, purchase type, and up to 100 reviews per page. [Steamworks User Reviews][4]
- Alibaba Cloud OSS Python SDK supports simple upload for files up to 5 GB and supports resumable or multipart uploads for larger files. [Alibaba Cloud OSS upload docs][5]
- Alibaba Cloud's RDS PostgreSQL getting-started workflow includes creating an instance, creating a database/account, configuring access control, applying a public endpoint if needed, and connecting from an application. [Alibaba Cloud RDS PostgreSQL guide][6]
- Alibaba Cloud PAI Model Gallery supports Qwen3 fine-tuning with SFT, LoRA, and QLoRA strategies. Training data and model output can use OSS. Fine-tuning is a later milestone, not an MVP blocker. [Alibaba Cloud PAI Qwen3 fine-tuning guide][7]

### Citations

[1]: https://www.alibabacloud.com/help/en/model-studio/getting-started/quick-start/ "Send Your First Qwen API Request via DashScope SDK - Model Studio - Alibaba Cloud"
[2]: https://www.alibabacloud.com/help/en/model-studio/rag-knowledge-base/ "Knowledge base - Alibaba Cloud Model Studio - Alibaba Cloud Documentation Center"
[3]: https://partner.steamgames.com/doc/webapi/ISteamNews "ISteamNews Interface - Steamworks Documentation"
[4]: https://partner.steamgames.com/doc/store/getreviews "User Reviews - Get List - Steamworks Documentation"
[5]: https://www.alibabacloud.com/help/en/oss/developer-reference/upload-objects-2/ "Upload files - Object Storage Service - Alibaba Cloud Documentation Center"
[6]: https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-postgresql/general-workflow-to-use-apsaradb-rds-for-postgresql "Get started with ApsaraDB RDS for PostgreSQL - Alibaba Cloud"
[7]: https://www.alibabacloud.com/help/en/pai/use-cases/deploy-fine-tune-and-evaluate-qwen3-in-quickstart/ "Run Qwen3 on PAI Model Gallery with Fine-Tuning and Evaluation - Alibaba Cloud"
