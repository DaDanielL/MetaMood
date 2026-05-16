"""Application settings and game catalog loading."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from yaml import YAMLError

from app.schemas import GameConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GAME_CATALOG_PATH = PROJECT_ROOT / "config" / "games.yaml"


class ConfigError(RuntimeError):
    """Raised when application configuration cannot be loaded."""


class AppSettings(BaseModel):
    """Typed settings loaded from environment variables."""

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_port: int = 8501
    dashscope_api_key: str = ""
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    qwen_model_classifier: str = "qwen-plus"
    qwen_model_reasoner: str = "qwen-plus"
    qwen_model_report: str = "qwen-plus"
    qwen_request_timeout_seconds: int = 60
    alibaba_cloud_access_key_id: str = ""
    alibaba_cloud_access_key_secret: str = ""
    oss_endpoint: str = ""
    oss_region: str = ""
    oss_bucket_name: str = ""
    database_url: str = "postgresql+psycopg2://user:password@host:5432/metamood"
    bailian_kb_enabled: bool = True
    bailian_kb_id: str = ""
    bailian_workspace_id: str = ""
    bailian_api_key: str = ""
    steam_review_language: str = "english"
    steam_review_max_pages: int = 5
    steam_review_num_per_page: int = 100
    steam_review_max_reviews: int = 500
    steam_review_type: str = "all"
    steam_review_filter: str = "recent"
    use_mock_qwen: bool = False
    use_mock_oss: bool = False
    use_mock_knowledge_base: bool = False


class GameCatalog(BaseModel):
    """Steam game catalog loaded from YAML."""

    games: list[GameConfig]


def load_app_settings(env_file: Path | None = PROJECT_ROOT / ".env") -> AppSettings:
    """Load typed app settings from environment variables."""
    if env_file is not None and env_file.exists():
        load_dotenv(env_file, override=False)

    return AppSettings(
        app_env=_env("APP_ENV", "development"),
        app_host=_env("APP_HOST", "0.0.0.0"),
        app_port=_env("APP_PORT", 8000),
        frontend_port=_env("FRONTEND_PORT", 8501),
        dashscope_api_key=_env("DASHSCOPE_API_KEY", ""),
        qwen_base_url=_env("QWEN_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"),
        qwen_model_classifier=_env("QWEN_MODEL_CLASSIFIER", "qwen-plus"),
        qwen_model_reasoner=_env("QWEN_MODEL_REASONER", "qwen-plus"),
        qwen_model_report=_env("QWEN_MODEL_REPORT", "qwen-plus"),
        qwen_request_timeout_seconds=_env("QWEN_REQUEST_TIMEOUT_SECONDS", 60),
        alibaba_cloud_access_key_id=_env("ALIBABA_CLOUD_ACCESS_KEY_ID", ""),
        alibaba_cloud_access_key_secret=_env("ALIBABA_CLOUD_ACCESS_KEY_SECRET", ""),
        oss_endpoint=_env("OSS_ENDPOINT", ""),
        oss_region=_env("OSS_REGION", ""),
        oss_bucket_name=_env("OSS_BUCKET_NAME", ""),
        database_url=_env("DATABASE_URL", "postgresql+psycopg2://user:password@host:5432/metamood"),
        bailian_kb_enabled=_env("BAILIAN_KB_ENABLED", True),
        bailian_kb_id=_env("BAILIAN_KB_ID", ""),
        bailian_workspace_id=_env("BAILIAN_WORKSPACE_ID", ""),
        bailian_api_key=_env("BAILIAN_API_KEY", ""),
        steam_review_language=_env("STEAM_REVIEW_LANGUAGE", "english"),
        steam_review_max_pages=_env("STEAM_REVIEW_MAX_PAGES", 5),
        steam_review_num_per_page=_env("STEAM_REVIEW_NUM_PER_PAGE", 100),
        steam_review_max_reviews=_env("STEAM_REVIEW_MAX_REVIEWS", 500),
        steam_review_type=_env("STEAM_REVIEW_TYPE", "all"),
        steam_review_filter=_env("STEAM_REVIEW_FILTER", "recent"),
        use_mock_qwen=_env("USE_MOCK_QWEN", False),
        use_mock_oss=_env("USE_MOCK_OSS", False),
        use_mock_knowledge_base=_env("USE_MOCK_KNOWLEDGE_BASE", False),
    )


def load_game_catalog(path: Path = DEFAULT_GAME_CATALOG_PATH) -> GameCatalog:
    """Load and validate the configured Steam game catalog."""
    try:
        raw_catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"Game catalog not found at {path}") from exc
    except YAMLError as exc:
        raise ConfigError(f"Game catalog YAML is invalid at {path}") from exc

    if not isinstance(raw_catalog, Mapping):
        raise ConfigError(f"Game catalog must be a mapping at {path}")

    try:
        return GameCatalog.model_validate(raw_catalog)
    except ValidationError as exc:
        raise ConfigError(f"Game catalog validation failed at {path}") from exc


def load_enabled_games(path: Path = DEFAULT_GAME_CATALOG_PATH) -> list[GameConfig]:
    """Return enabled games from the configured catalog."""
    catalog = load_game_catalog(path)
    return [game for game in catalog.games if game.enabled]


def game_to_public_payload(game: GameConfig) -> dict[str, str | int | bool]:
    """Serialize a configured game for the public games API."""
    return {
        "game_id": game.game_id,
        "display_name": game.display_name,
        "steam_appid": game.steam_appid,
        "enabled": game.enabled,
    }


def _env(name: str, default: Any) -> Any:
    return os.environ.get(name, default)
