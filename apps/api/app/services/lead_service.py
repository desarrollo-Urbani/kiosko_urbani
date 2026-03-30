from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Lead, SessionAnswer


def collect_raw_data(db: Session, session_id: str) -> dict:
    answers = db.scalars(select(SessionAnswer).where(SessionAnswer.session_id == session_id)).all()
    data: dict[str, object] = {}
    for answer in answers:
        if isinstance(answer.answer_value, dict) and "value" in answer.answer_value:
            data[answer.question_key] = answer.answer_value["value"]
        else:
            data[answer.question_key] = answer.answer_value
    return data


def create_or_update_lead(db: Session, session_id: str) -> Lead:
    lead = db.scalars(select(Lead).where(Lead.session_id == session_id)).first()
    raw_data = collect_raw_data(db, session_id)

    answered_count = len([value for value in raw_data.values() if value not in (None, "", "skip")])
    purchase_timeline = str(raw_data.get("purchase_timeline", raw_data.get("purchase_term", ""))).lower()
    down_payment_ready = raw_data.get("down_payment_ready")
    income_range = str(raw_data.get("income_range", "")).lower()

    short_term_values = {"0-3 meses", "0-6 meses", "0_3m", "0_6m", "pronto", "inmediata"}
    compatible_income_values = {"2000_3500", "3500_plus", "3500+", "4000_plus", "mas_2500"}
    has_short_term = purchase_timeline in short_term_values
    has_compatible_income = income_range in compatible_income_values

    score = 0
    if down_payment_ready is True:
        score += 45
    if has_compatible_income:
        score += 35
    if has_short_term:
        score += 20

    if down_payment_ready is True and has_compatible_income and has_short_term:
        classification = "high"
    elif answered_count < 4:
        classification = "low"
    elif down_payment_ready is False and not has_compatible_income:
        classification = "low"
    elif down_payment_ready is True or has_compatible_income or has_short_term:
        classification = "medium"
    else:
        classification = "low"

    if answered_count < 3:
        lead_status = "sin datos suficientes"
    elif classification == "high":
        lead_status = "listo"
    elif classification == "medium":
        lead_status = "casi listo"
    elif down_payment_ready is False:
        lead_status = "falta ahorro"
    elif not has_compatible_income:
        lead_status = "falta credito"
    else:
        lead_status = "sin datos suficientes"

    priority = classification
    enriched_raw_data = dict(raw_data)
    enriched_raw_data["lead_score"] = score
    enriched_raw_data["lead_classification"] = classification

    if lead:
        lead.raw_data = enriched_raw_data
        lead.priority = priority
        lead.lead_status = lead_status
    else:
        lead = Lead(
            session_id=session_id,
            raw_data=enriched_raw_data,
            priority=priority,
            lead_status=lead_status,
        )
        db.add(lead)

    db.commit()
    db.refresh(lead)
    return lead
