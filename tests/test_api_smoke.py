from sqlalchemy.orm import Session

from apps.api.app.models import KioskSession, Lead, Project, Property


TOKEN_HEADERS = {"X-Kiosk-Token": "dev-kiosk-token"}


def test_session_requires_token(client):
    response = client.post("/api/v1/sessions/", json={"kiosk_id": "kiosk-smoke"})
    assert response.status_code == 401


def test_smoke_kiosk_flow_creates_lead_and_recommendation(client, db_session: Session):
    project = Project(
        name="Urbani Test",
        commune="Vitacura",
        city="Santiago",
        delivery_status="immediate",
        subsidy_available=True,
        is_active=True,
    )
    db_session.add(project)
    db_session.flush()
    db_session.add(
        Property(
            project_id=project.id,
            property_type="dept",
            bedrooms=2,
            bathrooms=2,
            area_total_m2=70,
            price_uf=5200,
            dividend_est_clp=650000,
            stock_status="available",
        )
    )
    db_session.commit()

    session_res = client.post(
        "/api/v1/sessions/",
        json={"kiosk_id": "kiosk-smoke"},
        headers=TOKEN_HEADERS,
    )
    assert session_res.status_code == 200
    session_id = session_res.json()["session_id"]

    for payload in [
        {"question_key": "property_type", "answer_value": "dept", "answer_label": "Departamento"},
        {"question_key": "zone", "answer_value": "Vitacura", "answer_label": "Vitacura"},
        {"question_key": "budget_uf", "answer_value": 5500, "answer_label": "5500"},
    ]:
        answer_res = client.post(
            f"/api/v1/sessions/{session_id}/answers",
            json=payload,
            headers=TOKEN_HEADERS,
        )
        assert answer_res.status_code == 200

    rec_res = client.post(
        "/api/v1/recommendations/run",
        json={"session_id": session_id},
        headers=TOKEN_HEADERS,
    )
    assert rec_res.status_code == 200
    items = rec_res.json()["items"]
    assert len(items) >= 1
    assert "match_debug" in items[0]
    assert items[0]["match_level"] in {"high", "medium", "low"}

    lead = db_session.query(Lead).filter(Lead.session_id == session_id).one_or_none()
    assert lead is not None
    assert lead.lead_status in {
        "listo",
        "casi listo",
        "falta ahorro",
        "falta credito",
        "sin datos suficientes",
    }

    session = db_session.query(KioskSession).filter(KioskSession.id == session_id).one_or_none()
    assert session is not None
