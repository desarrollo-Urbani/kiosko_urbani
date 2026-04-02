from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..config import settings
from ..database import get_db
from ..models import EventLog, KioskSession, QueueExecutiveAssignment, QueueTicket, SessionAnswer
from ..schemas import QueueCallNextRequest, QueueTicketStatusPatchRequest, TicketCreateRequest, TicketResponse
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
    db.flush()
    db.add(
        EventLog(
            session_id=payload.session_id,
            event_type="queue_ticket_created",
            payload={
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "eta_minutes": eta,
            },
        )
    )
    db.commit()

    create_or_update_lead(db, payload.session_id)

    return TicketResponse(ticket_number=ticket_number, eta_minutes=eta)


@router.get("/tickets")
def list_tickets(status: str | None = None, db: Session = Depends(get_db)):
    query = select(QueueTicket).order_by(QueueTicket.created_at.asc(), QueueTicket.id.asc())
    if status:
        query = query.where(QueueTicket.status == status)
    tickets = db.scalars(query).all()
    assignment_by_ticket: dict[int, str] = {}
    if tickets:
        ticket_ids = [t.id for t in tickets]
        assignments = db.scalars(
            select(QueueExecutiveAssignment).where(QueueExecutiveAssignment.ticket_id.in_(ticket_ids))
        ).all()
        assignment_by_ticket = {a.ticket_id: a.executive_id for a in assignments}
    return {
        "items": [
            {
                "id": t.id,
                "ticket_number": t.ticket_number,
                "session_id": t.session_id,
                "status": t.status,
                "executive_id": assignment_by_ticket.get(t.id),
                "profiled": bool(
                    db.scalar(
                        select(SessionAnswer.id)
                        .where(SessionAnswer.session_id == t.session_id)
                        .limit(1)
                    )
                ),
                "estimated_wait_minutes": t.estimated_wait_minutes,
                "created_at": t.created_at,
            }
            for t in tickets
        ]
    }


@router.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    payload: QueueTicketStatusPatchRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(QueueTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    assignment = db.scalar(
        select(QueueExecutiveAssignment).where(QueueExecutiveAssignment.ticket_id == ticket_id)
    )
    if payload.executive_id and assignment and assignment.executive_id != payload.executive_id:
        raise HTTPException(status_code=409, detail="Ticket is assigned to another executive")

    old_status = ticket.status
    ticket.status = payload.status

    session = db.get(KioskSession, ticket.session_id)
    if session:
        session.last_activity_at = datetime.utcnow()
        if payload.status in {"completed", "no_show"}:
            session.status = "finished"
            session.finished_at = datetime.utcnow()
        elif payload.status in {"called", "in_service"}:
            session.status = "active"

    if assignment:
        assignment.status = payload.status
        if payload.status == "in_service":
            assignment.started_at = datetime.utcnow()
        if payload.status in {"completed", "no_show"}:
            assignment.ended_at = datetime.utcnow()

    db.add(
        EventLog(
            session_id=ticket.session_id,
            event_type="queue_ticket_status_changed",
            payload={
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "from": old_status,
                "to": payload.status,
                "executive_id": payload.executive_id,
            },
        )
    )
    db.commit()
    return {"ok": True, "ticket_id": ticket.id, "status": ticket.status}


@router.post("/call-next")
def call_next_ticket(payload: QueueCallNextRequest, db: Session = Depends(get_db)):
    current_assignment = db.scalar(
        select(QueueExecutiveAssignment).where(
            and_(
                QueueExecutiveAssignment.executive_id == payload.executive_id,
                QueueExecutiveAssignment.status.in_(["called", "in_service"]),
            )
        )
    )
    if current_assignment:
        ticket = db.get(QueueTicket, current_assignment.ticket_id)
        if ticket:
            return {
                "already_assigned": True,
                "ticket": {
                    "id": ticket.id,
                    "ticket_number": ticket.ticket_number,
                    "session_id": ticket.session_id,
                    "status": ticket.status,
                    "estimated_wait_minutes": ticket.estimated_wait_minutes,
                    "created_at": ticket.created_at,
                    "executive_id": payload.executive_id,
                },
            }

    for _ in range(5):
        candidate = db.scalar(
            select(QueueTicket)
            .where(QueueTicket.status == "waiting")
            .order_by(QueueTicket.created_at.asc(), QueueTicket.id.asc())
            .limit(1)
        )
        if not candidate:
            raise HTTPException(status_code=404, detail="No tickets waiting")

        claim = db.execute(
            update(QueueTicket)
            .where(and_(QueueTicket.id == candidate.id, QueueTicket.status == "waiting"))
            .values(status="called")
        )
        if claim.rowcount != 1:
            db.rollback()
            continue

        db.add(
            QueueExecutiveAssignment(
                ticket_id=candidate.id,
                executive_id=payload.executive_id,
                status="called",
            )
        )

        session = db.get(KioskSession, candidate.session_id)
        if session:
            session.status = "active"
            session.last_activity_at = datetime.utcnow()

        db.add(
            EventLog(
                session_id=candidate.session_id,
                event_type="queue_ticket_called",
                payload={
                    "ticket_id": candidate.id,
                    "ticket_number": candidate.ticket_number,
                    "executive_id": payload.executive_id,
                },
            )
        )
        try:
            db.commit()
            db.refresh(candidate)
            return {
                "already_assigned": False,
                "ticket": {
                    "id": candidate.id,
                    "ticket_number": candidate.ticket_number,
                    "session_id": candidate.session_id,
                    "status": candidate.status,
                    "estimated_wait_minutes": candidate.estimated_wait_minutes,
                    "created_at": candidate.created_at,
                    "executive_id": payload.executive_id,
                },
            }
        except IntegrityError:
            db.rollback()
            continue

    raise HTTPException(status_code=409, detail="Queue conflict, retry")
