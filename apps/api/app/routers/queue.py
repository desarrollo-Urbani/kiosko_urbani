from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..config import settings
from ..database import get_db
from ..models import EventLog, KioskSession, QueueExecutiveAssignment, QueueTicket, SessionAnswer
from ..schemas import (
    QueueAdminResetRequest,
    QueueCallNextRequest,
    QueuePrioritizeRequest,
    QueueTicketStatusPatchRequest,
    QueueTransferRequest,
    TicketCreateRequest,
    TicketResponse,
)
from ..services.lead_service import create_or_update_lead

router = APIRouter(prefix="/queue", tags=["queue"], dependencies=[Depends(verify_kiosk_token)])


def _scope_matches(scope: str | None, kiosk_device_id: str | None) -> bool:
    if not scope:
        return True
    return (kiosk_device_id or "").strip().lower().startswith(scope.strip().lower())


def _priority_score(db: Session, ticket: QueueTicket) -> int:
    age_minutes = max(0, int((datetime.utcnow() - ticket.created_at).total_seconds() / 60))
    score = min(age_minutes, 120)
    answer_rows = db.scalars(select(SessionAnswer).where(SessionAnswer.session_id == ticket.session_id)).all()
    answers = {
        a.question_key.lower(): (
            a.answer_value.get("value") if isinstance(a.answer_value, dict) else a.answer_value
        )
        for a in answer_rows
    }
    if answers.get("vip") is True:
        score += 60
    if answers.get("has_appointment") is True or answers.get("tiene_cita") is True:
        score += 40
    if answers.get("is_senior") is True or answers.get("adulto_mayor") is True:
        score += 25
    return score


def _extract_ticket_customer_context(answer_rows: list[SessionAnswer]) -> tuple[str | None, dict[str, object], bool]:
    rut: str | None = None
    profile: dict[str, object] = {}
    for row in answer_rows:
        value = row.answer_value.get("value") if isinstance(row.answer_value, dict) else row.answer_value
        key = row.question_key.lower()
        if key in {"rut", "rut_cliente", "customer_rut", "document_rut"} and isinstance(value, str):
            candidate = value.strip()
            if candidate and candidate.lower() not in {"skip", "no", "none", "n/a", "na"}:
                rut = candidate
        else:
            profile[row.question_key] = value
    profiled = len(profile) > 0
    return rut, profile, profiled


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(payload: TicketCreateRequest, db: Session = Depends(get_db)):
    session = db.get(KioskSession, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    rut_answers = db.scalars(
        select(SessionAnswer)
        .where(
            and_(
                SessionAnswer.session_id == payload.session_id,
                SessionAnswer.question_key.in_(["rut", "rut_cliente", "customer_rut", "document_rut"]),
            )
        )
        .order_by(SessionAnswer.created_at.desc())
    ).all()
    rut_value = None
    for row in rut_answers:
        value = row.answer_value.get("value") if isinstance(row.answer_value, dict) else row.answer_value
        if isinstance(value, str):
            candidate = value.strip()
            if candidate and candidate.lower() not in {"skip", "no", "none", "n/a", "na"}:
                rut_value = candidate
                break
    if not rut_value:
        raise HTTPException(status_code=400, detail="RUT is required to create ticket")

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
                "rut": rut_value,
            },
        )
    )
    db.commit()

    create_or_update_lead(db, payload.session_id)

    return TicketResponse(ticket_number=ticket_number, eta_minutes=eta)


@router.get("/tickets")
def list_tickets(
    status: str | None = None,
    queue_scope: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(QueueTicket).order_by(QueueTicket.created_at.asc(), QueueTicket.id.asc())
    if status:
        query = query.where(QueueTicket.status == status)
    tickets = db.scalars(query).all()
    if queue_scope:
        session_map = {
            s.id: s.kiosk_device_id
            for s in db.scalars(select(KioskSession).where(KioskSession.id.in_([t.session_id for t in tickets]))).all()
        }
        tickets = [t for t in tickets if _scope_matches(queue_scope, session_map.get(t.session_id))]
    assignment_by_ticket: dict[int, str] = {}
    if tickets:
        ticket_ids = [t.id for t in tickets]
        assignments = db.scalars(
            select(QueueExecutiveAssignment).where(QueueExecutiveAssignment.ticket_id.in_(ticket_ids))
        ).all()
        assignment_by_ticket = {a.ticket_id: a.executive_id for a in assignments}
    session_ids = list({t.session_id for t in tickets})
    answers_by_session: dict[str, list[SessionAnswer]] = {sid: [] for sid in session_ids}
    if session_ids:
        for row in db.scalars(select(SessionAnswer).where(SessionAnswer.session_id.in_(session_ids))).all():
            answers_by_session[row.session_id].append(row)
    return {
        "items": [
            (lambda rut, profile, profiled: {
                "id": t.id,
                "ticket_number": t.ticket_number,
                "session_id": t.session_id,
                "status": t.status,
                "executive_id": assignment_by_ticket.get(t.id),
                "rut": rut,
                "profiled": profiled,
                "profile": profile,
                "estimated_wait_minutes": t.estimated_wait_minutes,
                "created_at": t.created_at,
            })(*_extract_ticket_customer_context(answers_by_session.get(t.session_id, [])))
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
        waiting = db.scalars(
            select(QueueTicket).where(QueueTicket.status == "waiting")
        ).all()
        if payload.queue_scope:
            sessions = {
                s.id: s.kiosk_device_id
                for s in db.scalars(
                    select(KioskSession).where(KioskSession.id.in_([t.session_id for t in waiting]))
                ).all()
            }
            waiting = [t for t in waiting if _scope_matches(payload.queue_scope, sessions.get(t.session_id))]

        if payload.priority_mode == "smart":
            waiting = sorted(waiting, key=lambda t: (-_priority_score(db, t), t.created_at, t.id))
        else:
            waiting = sorted(waiting, key=lambda t: (t.created_at, t.id))
        candidate = waiting[0] if waiting else None
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
                        "queue_scope": payload.queue_scope,
                        "priority_mode": payload.priority_mode,
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


@router.post("/tickets/{ticket_id}/transfer")
def transfer_ticket(
    ticket_id: int,
    payload: QueueTransferRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(QueueTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    assignment = db.scalar(
        select(QueueExecutiveAssignment).where(QueueExecutiveAssignment.ticket_id == ticket_id)
    )
    if not assignment:
        raise HTTPException(status_code=409, detail="Ticket has no active assignment")
    if assignment.executive_id != payload.from_executive_id:
        raise HTTPException(status_code=409, detail="Ticket is assigned to another executive")
    if payload.to_executive_id == payload.from_executive_id:
        raise HTTPException(status_code=400, detail="Destination executive must be different")

    target_active = db.scalar(
        select(QueueExecutiveAssignment).where(
            and_(
                QueueExecutiveAssignment.executive_id == payload.to_executive_id,
                QueueExecutiveAssignment.status.in_(["called", "in_service"]),
            )
        )
    )
    if target_active:
        raise HTTPException(status_code=409, detail="Destination executive already has an active ticket")

    old_executive = assignment.executive_id
    assignment.executive_id = payload.to_executive_id

    db.add(
        EventLog(
            session_id=ticket.session_id,
            event_type="queue_ticket_transferred",
            payload={
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "from_executive_id": old_executive,
                "to_executive_id": payload.to_executive_id,
            },
        )
    )
    db.commit()
    return {"ok": True, "ticket_id": ticket.id, "executive_id": assignment.executive_id}


@router.get("/metrics/summary")
def queue_metrics_summary(
    queue_scope: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    tickets = db.scalars(select(QueueTicket)).all()
    sessions = {
        s.id: s.kiosk_device_id
        for s in db.scalars(select(KioskSession).where(KioskSession.id.in_([t.session_id for t in tickets]))).all()
    }
    scoped = [t for t in tickets if _scope_matches(queue_scope, sessions.get(t.session_id))]

    waiting = [t for t in scoped if t.status == "waiting"]
    completed = [t for t in scoped if t.status == "completed"]
    no_show = [t for t in scoped if t.status == "no_show"]

    wait_avg = int(sum(max(0, int((datetime.utcnow() - t.created_at).total_seconds() / 60)) for t in waiting) / len(waiting)) if waiting else 0
    service_durations = []
    assignments = db.scalars(select(QueueExecutiveAssignment)).all()
    assignment_by_ticket = {a.ticket_id: a for a in assignments}
    for t in completed:
        a = assignment_by_ticket.get(t.id)
        if a and a.started_at and a.ended_at:
            service_durations.append(max(0, int((a.ended_at - a.started_at).total_seconds() / 60)))
    service_avg = int(sum(service_durations) / len(service_durations)) if service_durations else 0
    no_show_rate = round((len(no_show) / len(scoped)) * 100, 1) if scoped else 0.0

    return {
        "queue_scope": queue_scope or "global",
        "waiting_count": len(waiting),
        "completed_count": len(completed),
        "no_show_count": len(no_show),
        "avg_wait_minutes": wait_avg,
        "avg_service_minutes": service_avg,
        "no_show_rate_percent": no_show_rate,
    }


@router.get("/metrics/executives")
def queue_metrics_by_executive(
    queue_scope: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    assignments = db.scalars(select(QueueExecutiveAssignment)).all()
    tickets = {t.id: t for t in db.scalars(select(QueueTicket)).all()}
    sessions = {
        s.id: s.kiosk_device_id
        for s in db.scalars(select(KioskSession).where(KioskSession.id.in_([t.session_id for t in tickets.values()]))).all()
    }
    by_exec: dict[str, dict] = {}

    for a in assignments:
        t = tickets.get(a.ticket_id)
        if not t:
            continue
        if not _scope_matches(queue_scope, sessions.get(t.session_id)):
            continue
        row = by_exec.setdefault(
            a.executive_id,
            {
                "executive_id": a.executive_id,
                "called": 0,
                "in_service": 0,
                "completed": 0,
                "no_show": 0,
                "service_minutes_sum": 0,
                "service_samples": 0,
                "avg_service_minutes": 0,
            },
        )
        row["called"] += 1
        if a.status == "in_service":
            row["in_service"] += 1
        if a.status == "completed":
            row["completed"] += 1
            if a.started_at and a.ended_at:
                duration = max(0, int((a.ended_at - a.started_at).total_seconds() / 60))
                row["service_minutes_sum"] += duration
                row["service_samples"] += 1
        if a.status == "no_show":
            row["no_show"] += 1

    for row in by_exec.values():
        if row["service_samples"] > 0:
            row["avg_service_minutes"] = int(row["service_minutes_sum"] / row["service_samples"])
        else:
            row["avg_service_minutes"] = 0
        row.pop("service_minutes_sum", None)
        row.pop("service_samples", None)

    return {"items": sorted(by_exec.values(), key=lambda x: x["executive_id"])}


@router.post("/tickets/{ticket_id}/prioritize")
def prioritize_ticket(
    ticket_id: int,
    payload: QueuePrioritizeRequest,
    db: Session = Depends(get_db),
):
    ticket = db.get(QueueTicket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.status != "waiting":
        raise HTTPException(status_code=409, detail="Only waiting tickets can be prioritized")

    ticket.created_at = datetime.utcnow() - timedelta(minutes=max(1, payload.priority_minutes))
    db.add(
        EventLog(
            session_id=ticket.session_id,
            event_type="queue_ticket_prioritized",
            payload={
                "ticket_id": ticket.id,
                "ticket_number": ticket.ticket_number,
                "priority_minutes": payload.priority_minutes,
            },
        )
    )
    db.commit()
    return {"ok": True, "ticket_id": ticket.id}


@router.post("/admin/reset")
def reset_queue(payload: QueueAdminResetRequest, db: Session = Depends(get_db)):
    queue_scope = (payload.queue_scope or "").strip()

    tickets = db.scalars(select(QueueTicket)).all()
    if queue_scope:
        session_map = {
            s.id: s.kiosk_device_id
            for s in db.scalars(select(KioskSession).where(KioskSession.id.in_([t.session_id for t in tickets]))).all()
        }
        tickets = [t for t in tickets if _scope_matches(queue_scope, session_map.get(t.session_id))]

    ticket_ids = [t.id for t in tickets]
    assignments = []
    if ticket_ids:
        assignments = db.scalars(
            select(QueueExecutiveAssignment).where(QueueExecutiveAssignment.ticket_id.in_(ticket_ids))
        ).all()

    deleted_assignments = 0
    for a in assignments:
        db.delete(a)
        deleted_assignments += 1

    deleted_tickets = 0
    for t in tickets:
        db.delete(t)
        deleted_tickets += 1

    db.add(
        EventLog(
            session_id="admin",
            event_type="queue_reset",
            payload={
                "queue_scope": queue_scope or "global",
                "deleted_tickets": deleted_tickets,
                "deleted_assignments": deleted_assignments,
            },
        )
    )
    db.commit()
    return {
        "ok": True,
        "queue_scope": queue_scope or "global",
        "deleted_tickets": deleted_tickets,
        "deleted_assignments": deleted_assignments,
    }
