from apps.api.app.config import settings


def test_login_and_me(client):
    res = client.post("/api/v1/auth/login", json={"email": "eflores@urbani.cl"})
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == "eflores@urbani.cl"

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "eflores@urbani.cl"
    assert me.json()["role"] == "executive"


def test_supervisor_only_endpoint_forbidden_to_executive(client):
    login = client.post("/api/v1/auth/login", json={"email": "eflores@urbani.cl"})
    token = login.json()["access_token"]

    metrics = client.get(
        "/api/v1/queue/metrics/executives",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert metrics.status_code == 403


def test_supervisor_can_access_supervisor_endpoint(client):
    previous = settings.supervisor_emails
    try:
        settings.supervisor_emails = "eflores@urbani.cl"
        login = client.post("/api/v1/auth/login", json={"email": "eflores@urbani.cl"})
        token = login.json()["access_token"]

        metrics = client.get(
            "/api/v1/queue/metrics/executives",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert metrics.status_code == 200
    finally:
        settings.supervisor_emails = previous
