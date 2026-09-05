from src.app import app


def test_info():
    client = app.test_client()

    response = client.get("/api/v1/info")

    assert response.status_code == 200


def test_health():
    client = app.test_client()

    response = client.get("/api/v1/healthz")

    assert response.status_code == 200
    assert response.json["status"] == "up"