"""Game catalog routes."""

from fastapi import APIRouter, HTTPException

from app.config import ConfigError, game_to_public_payload, load_enabled_games
from app.schemas import GameResponse

router = APIRouter()


@router.get("/games", response_model=list[GameResponse])
def get_games() -> list[GameResponse]:
    """Return enabled games from the configured Steam catalog."""
    try:
        games = load_enabled_games()
    except ConfigError as exc:
        raise HTTPException(status_code=500, detail="Game catalog configuration is invalid.") from exc
    return [GameResponse.model_validate(game_to_public_payload(game)) for game in games]
