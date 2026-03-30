from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Lead
from ..schemas import LeadStatusPatchRequest
from ..services.llm_service import generate_lead_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/leads")
def list_leads(
    lead_status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = select(Lead)
    if lead_status:
        query = query.where(Lead.lead_status == lead_status)
    if priority:
        query = query.where(Lead.priority == priority)
    leads = db.scalars(query.order_by(Lead.created_at.desc())).all()
    return {
        "items": [
            {
                "id": lead.id,
                "session_id": lead.session_id,
                "lead_status": lead.lead_status,
                "priority": lead.priority,
                "executive_summary": lead.executive_summary,
                "created_at": lead.created_at,
            }
            for lead in leads
        ]
    }


@router.patch("/leads/{lead_id}")
def update_lead_status(lead_id: str, payload: LeadStatusPatchRequest, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.lead_status = payload.lead_status
    db.commit()
    return {"ok": True}


@router.post("/leads/{lead_id}/summary")
def regenerate_summary(lead_id: str, db: Session = Depends(get_db)):
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    summary = generate_lead_summary(lead.raw_data or {})
    lead.executive_summary = "\n".join(f"- {item}" for item in summary["executive_summary"])
    db.commit()

    return summary
