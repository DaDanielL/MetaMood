from fastapi.testclient import TestClient

from app import APP_VERSION, SERVICE_NAME
from app.main import app


def test_health_endpoint_returns_service_metadata() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": APP_VERSION,
    }
