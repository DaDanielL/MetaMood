"""Database engine, session, and deterministic table creation helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import load_app_settings
from app.db.base import Base


def create_database_engine(database_url: str | None = None, **engine_kwargs: Any) -> Engine:
    """Create a SQLAlchemy engine from an explicit URL or configured DATABASE_URL."""
    url = database_url or load_app_settings().database_url
    options: dict[str, Any] = {"pool_pre_ping": True, "future": True}
    options.update(engine_kwargs)
    return create_engine(url, **options)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the configured session factory for an engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Provide a transactional scope around one database unit of work."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables(engine: Engine) -> None:
    """Create all registered MetaMood database tables."""
    import app.db.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
