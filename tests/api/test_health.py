from fastapi.testclient import TestClient

from seoul_mens_daily_edit.app import create_app
from seoul_mens_daily_edit.core.config import Settings


def test_health_returns_ok(settings: Settings) -> None:
    with TestClient(create_app(settings)) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
