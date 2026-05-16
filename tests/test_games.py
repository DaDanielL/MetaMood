from fastapi.testclient import TestClient

from app.main import app


def test_games_endpoint_returns_only_enabled_games() -> None:
    client = TestClient(app)

    response = client.get("/games")

    assert response.status_code == 200
    games = response.json()
    game_ids = {game["game_id"] for game in games}
    assert game_ids == {"helldivers_2", "counter_strike_2", "dota_2"}
    assert "team_fortress_2" not in game_ids


def test_games_endpoint_returns_public_game_shape() -> None:
    client = TestClient(app)

    response = client.get("/games")

    assert response.status_code == 200
    for game in response.json():
        assert set(game) == {"game_id", "display_name", "steam_appid", "enabled"}
        assert isinstance(game["game_id"], str)
        assert isinstance(game["display_name"], str)
        assert isinstance(game["steam_appid"], int)
        assert game["enabled"] is True


def test_games_endpoint_documents_response_model() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()["paths"]["/games"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["items"]["$ref"] == "#/components/schemas/GameResponse"
