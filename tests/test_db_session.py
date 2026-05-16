from __future__ import annotations

import pytest

from app.db.models import Game
from app.db.session import create_all_tables, create_database_engine, create_session_factory, session_scope


def test_create_database_engine_uses_explicit_database_url() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")

    assert engine.url.drivername == "sqlite+pysqlite"
    assert engine.url.database == ":memory:"


def test_create_database_engine_reads_database_url_from_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    engine = create_database_engine()

    assert engine.url.drivername == "sqlite+pysqlite"
    assert engine.url.database == ":memory:"


def test_session_scope_commits_successful_unit_of_work() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")
    create_all_tables(engine)
    session_factory = create_session_factory(engine)

    with session_scope(session_factory) as session:
        session.add(
            Game(
                game_id="helldivers_2",
                display_name="HELLDIVERS 2",
                steam_appid=553850,
                platform="steam",
                enabled=True,
            )
        )

    with session_scope(session_factory) as session:
        game = session.get(Game, "helldivers_2")

        assert game is not None
        assert game.display_name == "HELLDIVERS 2"


def test_session_scope_rolls_back_failed_unit_of_work() -> None:
    engine = create_database_engine("sqlite+pysqlite:///:memory:")
    create_all_tables(engine)
    session_factory = create_session_factory(engine)

    with pytest.raises(RuntimeError, match="stop before commit"):
        with session_scope(session_factory) as session:
            session.add(
                Game(
                    game_id="helldivers_2",
                    display_name="HELLDIVERS 2",
                    steam_appid=553850,
                    platform="steam",
                    enabled=True,
                )
            )
            raise RuntimeError("stop before commit")

    with session_scope(session_factory) as session:
        assert session.get(Game, "helldivers_2") is None
