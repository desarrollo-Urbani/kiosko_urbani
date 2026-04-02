from sqlalchemy.orm import Session

from apps.api.app.models import EventLog, KioskSession, QueueTicket


TOKEN_HEADERS = {"X-Kiosk-Token": "dev-kiosk-token"}


def test_queue_ticket_status_flow_and_audit(client, db_session: Session):
    session_res = client.post(
        "/api/v1/sessions/",
        json={"kiosk_id": "kiosk-queue-test"},
        headers=TOKEN_HEADERS,
    )
    assert session_res.status_code == 200
    session_id = session_res.json()["session_id"]

    r = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_key": "rut", "answer_value": "11111111-1", "answer_label": "11111111-1"},
        headers=TOKEN_HEADERS,
    )
    assert r.status_code == 200

    ticket_res = client.post(
        "/api/v1/queue/tickets",
        json={"session_id": session_id, "name": "Cliente Prueba"},
        headers=TOKEN_HEADERS,
    )
    assert ticket_res.status_code == 200
    ticket_number = ticket_res.json()["ticket_number"]

    ticket = db_session.query(QueueTicket).filter(QueueTicket.ticket_number == ticket_number).one_or_none()
    assert ticket is not None
    assert ticket.status == "waiting"

    for status in ["called", "in_service", "completed"]:
        res = client.patch(
            f"/api/v1/queue/tickets/{ticket.id}/status",
            json={"status": status},
            headers=TOKEN_HEADERS,
        )
        assert res.status_code == 200

    db_session.refresh(ticket)
    assert ticket.status == "completed"

    session = db_session.get(KioskSession, session_id)
    assert session is not None
    assert session.status == "finished"

    events = (
        db_session.query(EventLog)
        .filter(EventLog.session_id == session_id)
        .order_by(EventLog.created_at.asc(), EventLog.id.asc())
        .all()
    )
    event_types = [e.event_type for e in events]
    assert "queue_ticket_created" in event_types
    assert event_types.count("queue_ticket_status_changed") >= 3


def test_call_next_assigns_distinct_tickets_per_executive(client, db_session: Session):
    session_ids = []
    for i in range(2):
        s = client.post(
            "/api/v1/sessions/",
            json={"kiosk_id": f"kiosk-multi-{i}"},
            headers=TOKEN_HEADERS,
        )
        assert s.status_code == 200
        session_ids.append(s.json()["session_id"])
        r = client.post(
            f"/api/v1/sessions/{session_ids[-1]}/answers",
            json={"question_key": "rut", "answer_value": f"1111111{i}-1", "answer_label": f"1111111{i}-1"},
            headers=TOKEN_HEADERS,
        )
        assert r.status_code == 200
        t = client.post(
            "/api/v1/queue/tickets",
            json={"session_id": session_ids[-1], "name": f"Cliente {i}"},
            headers=TOKEN_HEADERS,
        )
        assert t.status_code == 200

    e1 = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-a"},
        headers=TOKEN_HEADERS,
    )
    e2 = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-b"},
        headers=TOKEN_HEADERS,
    )
    assert e1.status_code == 200
    assert e2.status_code == 200
    assert e1.json()["ticket"]["id"] != e2.json()["ticket"]["id"]


def test_status_change_is_blocked_for_other_executive(client, db_session: Session):
    s = client.post(
        "/api/v1/sessions/",
        json={"kiosk_id": "kiosk-own"},
        headers=TOKEN_HEADERS,
    )
    assert s.status_code == 200
    session_id = s.json()["session_id"]
    r = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"question_key": "rut", "answer_value": "22222222-2", "answer_label": "22222222-2"},
        headers=TOKEN_HEADERS,
    )
    assert r.status_code == 200

    t = client.post(
        "/api/v1/queue/tickets",
        json={"session_id": session_id, "name": "Cliente Ownership"},
        headers=TOKEN_HEADERS,
    )
    assert t.status_code == 200

    called = client.post(
        "/api/v1/queue/call-next",
        json={"executive_id": "exec-owner"},
        headers=TOKEN_HEADERS,
    )
    assert called.status_code == 200
    ticket_id = called.json()["ticket"]["id"]

    blocked = client.patch(
        f"/api/v1/queue/tickets/{ticket_id}/status",
        json={"status": "in_service", "executive_id": "exec-other"},
        headers=TOKEN_HEADERS,
    )
    assert blocked.status_code == 409
