from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..database import get_db
from ..schemas import AssistRequest, AssistResponse
from ..services.llm_service import assist_message

router = APIRouter(prefix="/llm", tags=["llm"], dependencies=[Depends(verify_kiosk_token)])


@router.post("/assist", response_model=AssistResponse)
def assist(payload: AssistRequest, db: Session = Depends(get_db)):
    return assist_message(db, payload.session_id, payload.current_screen, payload.user_query)
