from sqlalchemy.orm import Session

from apps.api.app.models import KioskSession, Project, Property, SessionAnswer
from apps.api.app.services.recommender import run_recommendation


def _seed_session(db_session: Session) -> str:
    session = KioskSession(kiosk_device_id="kiosk-test", session_key="abc12345")
    db_session.add(session)
    db_session.commit()
    return session.id


def test_recommender_requires_property_type(db_session: Session):
    session_id = _seed_session(db_session)
    db_session.add(SessionAnswer(session_id=session_id, question_key="zone", answer_value={"value": "Vitacura"}, answer_label="Vitacura"))
    db_session.commit()

    items = run_recommendation(db_session, session_id)
    assert items == []


def test_recommender_excludes_unavailable_stock_and_builds_debug(db_session: Session):
    session_id = _seed_session(db_session)
    project = Project(
        name="Urbani Vitacura",
        commune="Vitacura",
        city="Santiago",
        delivery_status="immediate",
        subsidy_available=False,
        is_active=True,
    )
    db_session.add(project)
    db_session.flush()
    db_session.add_all(
        [
            Property(
                project_id=project.id,
                property_type="dept",
                bedrooms=2,
                bathrooms=2,
                area_total_m2=70,
                price_uf=5100,
                dividend_est_clp=640000,
                stock_status="available",
            ),
            Property(
                project_id=project.id,
                property_type="dept",
                bedrooms=2,
                bathrooms=2,
                area_total_m2=70,
                price_uf=4800,
                dividend_est_clp=620000,
                stock_status="reserved",
            ),
        ]
    )
    db_session.add_all(
        [
            SessionAnswer(session_id=session_id, question_key="property_type", answer_value={"value": "dept"}, answer_label="Departamento"),
            SessionAnswer(session_id=session_id, question_key="zone", answer_value={"value": "Vitacura"}, answer_label="Vitacura"),
            SessionAnswer(session_id=session_id, question_key="budget_uf", answer_value={"value": 5500}, answer_label="5500"),
            SessionAnswer(session_id=session_id, question_key="bedrooms", answer_value={"value": 2}, answer_label="2"),
        ]
    )
    db_session.commit()

    items = run_recommendation(db_session, session_id)
    assert len(items) == 1
    assert items[0]["total_score"] >= 80
    assert items[0]["match_level"] == "high"
    assert items[0]["match_debug"]["property_id"] == items[0]["property_id"]
    assert "tipo_ok" in items[0]["match_debug"]["match_tags"]
