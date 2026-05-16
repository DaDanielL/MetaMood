"""Shared API response schemas."""

from pydantic import BaseModel


class GameResponse(BaseModel):
    """Public game metadata returned by the games API."""

    game_id: str
    display_name: str
    steam_appid: int
    enabled: bool
