"""FastAPI application entry point."""

from fastapi import FastAPI

from app import APP_VERSION
from app.api.routes_games import router as games_router
from app.api.routes_health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the MetaMood FastAPI app."""
    application = FastAPI(title="MetaMood", version=APP_VERSION)
    application.include_router(health_router)
    application.include_router(games_router)
    return application


app = create_app()
