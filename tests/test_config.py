from pathlib import Path

import pytest

from app.config import ConfigError, PROJECT_ROOT, load_app_settings, load_enabled_games, load_game_catalog


def test_load_game_catalog_validates_catalog_entries(tmp_path: Path) -> None:
    catalog_path = tmp_path / "games.yaml"
    catalog_path.write_text(
        """
games:
  - game_id: "enabled_game"
    display_name: "Enabled Game"
    steam_appid: 123
    platform: "steam"
    enabled: true
""",
        encoding="utf-8",
    )

    catalog = load_game_catalog(catalog_path)

    assert len(catalog.games) == 1
    assert catalog.games[0].game_id == "enabled_game"
    assert catalog.games[0].steam_appid == 123
    assert catalog.games[0].platform == "steam"
    assert catalog.games[0].enabled is True


def test_load_enabled_games_excludes_disabled_games(tmp_path: Path) -> None:
    catalog_path = tmp_path / "games.yaml"
    catalog_path.write_text(
        """
games:
  - game_id: "enabled_game"
    display_name: "Enabled Game"
    steam_appid: 123
    platform: "steam"
    enabled: true
  - game_id: "disabled_game"
    display_name: "Disabled Game"
    steam_appid: 456
    platform: "steam"
    enabled: false
""",
        encoding="utf-8",
    )

    enabled_games = load_enabled_games(catalog_path)

    assert [game.game_id for game in enabled_games] == ["enabled_game"]


def test_load_game_catalog_raises_for_missing_required_fields(tmp_path: Path) -> None:
    catalog_path = tmp_path / "games.yaml"
    catalog_path.write_text(
        """
games:
  - display_name: "Missing App ID"
    platform: "steam"
    enabled: true
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="validation failed"):
        load_game_catalog(catalog_path)


def test_load_app_settings_uses_env_overrides_without_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("ALIBABA_CLOUD_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", raising=False)
    monkeypatch.delenv("BAILIAN_API_KEY", raising=False)
    monkeypatch.setenv("APP_PORT", "9001")
    monkeypatch.setenv("BAILIAN_KB_ENABLED", "false")
    monkeypatch.setenv("STEAM_REVIEW_MAX_REVIEWS", "250")
    monkeypatch.setenv("USE_MOCK_QWEN", "true")

    settings = load_app_settings(env_file=None)

    assert settings.app_port == 9001
    assert settings.bailian_kb_enabled is False
    assert settings.steam_review_max_reviews == 250
    assert settings.use_mock_qwen is True
    assert settings.dashscope_api_key == ""
    assert settings.alibaba_cloud_access_key_id == ""
    assert settings.alibaba_cloud_access_key_secret == ""
    assert settings.bailian_api_key == ""


def test_load_app_settings_default_env_file_is_project_root() -> None:
    defaults = load_app_settings.__defaults__

    assert defaults == (PROJECT_ROOT / ".env",)
