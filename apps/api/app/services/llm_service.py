import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import SessionAnswer

logger = logging.getLogger(__name__)


def assist_message(db: Session, session_id: str, current_screen: str, user_query: str | None) -> dict:
    safe_fallback = "Por defecto se muestran las mejores opciones segun tu perfilamiento."
    try:
        answers = db.scalars(select(SessionAnswer).where(SessionAnswer.session_id == session_id)).all()
        answer_map = {a.question_key: a.answer_label or str(a.answer_value) for a in answers}

        zone = answer_map.get("zone", "tu zona preferida")
        property_type = answer_map.get("property_type", "propiedad")
        query_hint = "te puedo ayudar a elegir una opcion concreta" if user_query else "podemos afinar el perfil"

        return {
            "message": f"Perfecto, vamos afinando tu busqueda de {property_type} en {zone}. {query_hint}.",
            "intent": "encouragement",
            "hint": f"En la pantalla {current_screen} puedes ajustar presupuesto para mejorar el match.",
            "safe_fallback": safe_fallback,
        }
    except Exception:
        logger.exception("assist_message_failed")
        return {
            "message": "",
            "intent": "fallback",
            "hint": "",
            "safe_fallback": safe_fallback,
        }


def generate_lead_summary(raw_data: dict) -> dict:
    budget = raw_data.get("budget_uf", "No declarado")
    zone = raw_data.get("zone", "No declarada")
    target = raw_data.get("goal", "No declarado")
    timeline = raw_data.get("purchase_timeline", "No declarado")

    bullets = [
        f"Interes principal: {target} en zona {zone}.",
        f"Presupuesto declarado: {budget} UF.",
        f"Plazo de compra estimado: {timeline}.",
    ]

    if raw_data.get("down_payment_ready") is True:
        bullets.append("Cliente declara pie listo, potencial alta prioridad.")

    return {
        "executive_summary": bullets,
        "suggested_approach": "Abrir conversacion con opciones de mayor match y validar financiamiento en 1er contacto.",
    }
