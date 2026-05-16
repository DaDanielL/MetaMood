# MetaMood

MetaMood is an Alibaba Cloud AI MaaS demo for live-service game teams. The MVP will detect a selected game's latest Steam update, collect recent public Steam reviews, store evidence in Alibaba Cloud OSS and RDS PostgreSQL, retrieve patch context through Bailian / Model Studio Knowledge Base, and use Qwen to generate live-ops analysis.

This repository now contains the initial FastAPI and Streamlit scaffold for STORY-001. Live Steam, Qwen, OSS, RDS, and Knowledge Base integrations are intentionally left for later stories.

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the initial dependencies inside the virtual environment:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` only when you need local overrides or live service credentials. The committed example documents the expected app, Steam, OSS, RDS, Qwen, Knowledge Base, and mock-mode settings without storing secrets.

The MVP Steam game catalog lives in `config/games.yaml`. Disabled games remain in the catalog for future use but are excluded from API responses.

Start the FastAPI backend:

```bash
python -m uvicorn app.main:app --reload
```

Start the Streamlit dashboard shell:

```bash
python -m streamlit run streamlit_app.py
```

Run tests:

```bash
python -m pytest
```

## Current API

`GET /health` returns:

```json
{
  "status": "ok",
  "service": "metamood",
  "version": "0.1.0"
}
```

`GET /games` returns enabled Steam games from `config/games.yaml`:

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

## Project Workflow

The AI workflow artifacts live under `.agents/`. Start with [.agents/README.md](.agents/README.md) for the planning and implementation flow, and use [AGENTS.md](AGENTS.md) for project-specific engineering rules.
