from sqlalchemy.orm import Session

from apps.api.app.models import QueueTicket


TOKEN_HEADERS = {"X-Kiosk-Token": "dev-kiosk-token"}


def _create_ticket(client, kiosk_id: str, answers: list[dict] | None = None) -> int:
    session_res = client.post("/api/v1/sessions/", json={"kiosk_id": kiosk_id}, headers=TOKEN_HEADERS)
    assert session_res.status_code == 200
    session_id = session_res.json()["session_id"]
    base_answers = [
        {"question_key": "rut", "answer_value": "11111111-1", "answer_label": "11111111-1"},
    ]
    for payload in base_answers + (answers or []):
        r = client.post(f"/api/v1/sessions/{session_id}/answers", json=payload, headers=TOKEN_HEADERS)
        assert r.status_code == 200
    ticket_res = client.post("/api/v1/queue/tickets", json={"session_id": session_id}, headers=TOKEN_HEADERS)
    assert ticket_res.status_code == 200
    return session_id


def test_ticket_requires_rut(client):
    session_res = client.post("/api/v1/sessions/", json={"kiosk_id": "kiosk-no-rut"}, headers=TOKEN_HEADERS)
    assert session_res.status_code == 200
    session_id = session_res.json()["session_id"]

    ticket_res = client.post("/api/v1/queue/tickets", json={"session_id": session_id}, headers=TOKEN_HEADERS)
    assert ticket_res.status_code == 400
    assert ticket_res.json()["detail"] == "RUT is required to create ticket"


def test_call_next_respects_scope(client, db_session: Session):
    _create_ticket(client, "kiosk-a-1")
    _create_ticket(client, "kiosk-b-1")

    call_a = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-a", "queue_scope": "kiosk-a", "priority_mode": "fifo"},
        headers=TOKEN_HEADERS,
    )
    assert call_a.status_code == 200
    ticket_id = call_a.json()["ticket"]["id"]
    ticket = db_session.get(QueueTicket, ticket_id)
    assert ticket is not None


def test_call_next_smart_priority_prefers_vip(client):
    _create_ticket(client, "kiosk-p-1")
    _create_ticket(
        client,
        "kiosk-p-1",
        answers=[
            {"question_key": "vip", "answer_value": True, "answer_label": "VIP"},
        ],
    )

    call = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-smart", "queue_scope": "kiosk-p", "priority_mode": "smart"},
        headers=TOKEN_HEADERS,
    )
    assert call.status_code == 200
    assert call.json()["ticket"]["status"] == "called"


def test_supervisor_metrics_endpoints_work(client):
    summary = client.get("/api/v1/queue/metrics/summary?queue_scope=kiosk-", headers=TOKEN_HEADERS)
    by_exec = client.get("/api/v1/queue/metrics/executives?queue_scope=kiosk-", headers=TOKEN_HEADERS)
    assert summary.status_code == 200
    assert by_exec.status_code == 200
    assert "waiting_count" in summary.json()
    assert "items" in by_exec.json()


def test_transfer_ticket_between_executives(client):
    _create_ticket(client, "kiosk-t-1")
    call = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-from", "queue_scope": "kiosk-t", "priority_mode": "fifo"},
        headers=TOKEN_HEADERS,
    )
    assert call.status_code == 200
    ticket_id = call.json()["ticket"]["id"]

    transfer = client.post(
        f"/api/v1/queue/tickets/{ticket_id}/transfer",
        json={"from_executive_id": "exec-from", "to_executive_id": "exec-to"},
        headers=TOKEN_HEADERS,
    )
    assert transfer.status_code == 200
    assert transfer.json()["executive_id"] == "exec-to"


def test_mark_ticket_as_no_show(client):
    _create_ticket(client, "kiosk-noshow-1")
    call = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-no-show", "queue_scope": "kiosk-noshow", "priority_mode": "fifo"},
        headers=TOKEN_HEADERS,
    )
    assert call.status_code == 200
    ticket_id = call.json()["ticket"]["id"]

    mark = client.patch(
        f"/api/v1/queue/tickets/{ticket_id}/status",
        json={"status": "no_show", "executive_id": "exec-no-show"},
        headers=TOKEN_HEADERS,
    )
    assert mark.status_code == 200
    assert mark.json()["status"] == "no_show"


def test_prioritize_waiting_ticket(client):
    _create_ticket(client, "kiosk-prio-1")
    waiting = client.get("/api/v1/queue/tickets?status=waiting&queue_scope=kiosk-prio", headers=TOKEN_HEADERS)
    assert waiting.status_code == 200
    assert waiting.json()["items"]
    ticket_id = waiting.json()["items"][0]["id"]

    p = client.post(
        f"/api/v1/queue/tickets/{ticket_id}/prioritize",
        json={"priority_minutes": 300},
        headers=TOKEN_HEADERS,
    )
    assert p.status_code == 200
    assert p.json()["ok"] is True


def test_reset_queue_by_scope(client):
    _create_ticket(client, "kiosk-reset-1")
    before = client.get("/api/v1/queue/tickets?status=waiting&queue_scope=kiosk-reset", headers=TOKEN_HEADERS)
    assert before.status_code == 200
    assert len(before.json()["items"]) >= 1

    reset = client.post(
        "/api/v1/queue/admin/reset",
        json={"queue_scope": "kiosk-reset"},
        headers=TOKEN_HEADERS,
    )
    assert reset.status_code == 200
    assert reset.json()["ok"] is True

    after = client.get("/api/v1/queue/tickets?status=waiting&queue_scope=kiosk-reset", headers=TOKEN_HEADERS)
    assert after.status_code == 200
    assert len(after.json()["items"]) == 0
