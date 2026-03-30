from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..config import settings
from ..database import get_db
from ..models import KioskSession, QueueTicket
from ..schemas import TicketCreateRequest, TicketResponse
from ..services.lead_service import create_or_update_lead

router = APIRouter(prefix="/queue", tags=["queue"], dependencies=[Depends(verify_kiosk_token)])


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(payload: TicketCreateRequest, db: Session = Depends(get_db)):
    session = db.get(KioskSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    waiting_count = db.scalar(
        select(func.count()).select_from(QueueTicket).where(QueueTicket.status == "waiting")
    ) or 0
    total_tickets = db.scalar(select(func.count()).select_from(QueueTicket)) or 0

    ticket_number = f"A-{total_tickets + 1:02d}"
    eta = (waiting_count + 1) * settings.average_attention_minutes

    ticket = QueueTicket(
        session_id=payload.session_id,
        ticket_number=ticket_number,
        customer_name=payload.name,
        customer_phone=payload.phone,
        estimated_wait_minutes=eta,
        status="waiting",
    )
    db.add(ticket)
    db.commit()

    create_or_update_lead(db, payload.session_id)

    return TicketResponse(ticket_number=ticket_number, eta_minutes=eta)
