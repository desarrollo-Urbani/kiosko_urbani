import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..database import get_db
from ..models import KioskSession, SessionAnswer
from ..schemas import AnswerCreateRequest, SessionCreateRequest, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"], dependencies=[Depends(verify_kiosk_token)])


@router.post("/", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, db: Session = Depends(get_db)):
    session = KioskSession(
        kiosk_device_id=payload.kiosk_id,
        session_key=str(uuid.uuid4())[:8],
        status="active",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return SessionResponse(session_id=session.id, status=session.status)


@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.get(KioskSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    answers = db.scalars(
        select(SessionAnswer).where(SessionAnswer.session_id == session_id)
    ).all()
    return {
        "id": session.id,
        "status": session.status,
        "started_at": session.started_at,
        "last_activity_at": session.last_activity_at,
        "answers": [
            {
                "question_key": answer.question_key,
                "answer_value": answer.answer_value,
                "answer_label": answer.answer_label,
            }
            for answer in answers
        ],
    }


@router.post("/{session_id}/answers")
def post_answer(session_id: str, payload: AnswerCreateRequest, db: Session = Depends(get_db)):
    session = db.get(KioskSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answer = SessionAnswer(
        session_id=session_id,
        question_key=payload.question_key,
        answer_value={"value": payload.answer_value},
        answer_label=payload.answer_label,
    )
    session.last_activity_at = datetime.utcnow()
    db.add(answer)
    db.commit()
    return {"ok": True}
