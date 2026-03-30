from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..database import get_db
from ..models import EventLog, KioskSession
from ..schemas import EventCreateRequest

router = APIRouter(prefix="/events", tags=["events"], dependencies=[Depends(verify_kiosk_token)])


@router.post("/")
def create_event(payload: EventCreateRequest, db: Session = Depends(get_db)):
    event = EventLog(
        session_id=payload.session_id,
        event_type=payload.event_type,
        payload=payload.payload,
    )
    db.add(event)

    session = db.get(KioskSession, payload.session_id)
    if session:
        session.last_activity_at = datetime.utcnow()

    db.commit()
    return {"ok": True}
