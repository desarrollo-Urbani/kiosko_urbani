from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import verify_kiosk_token
from ..database import get_db
from ..schemas import RecommendationRunRequest
from ..services.lead_service import create_or_update_lead
from ..services.recommender import get_latest_recommendations, run_recommendation

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
    dependencies=[Depends(verify_kiosk_token)],
)


@router.post("/run")
def run_recommender(payload: RecommendationRunRequest, db: Session = Depends(get_db)):
    results = run_recommendation(db, payload.session_id)
    create_or_update_lead(db, payload.session_id)
    return {"items": results}


@router.get("/{session_id}")
def get_recommendations(session_id: str, db: Session = Depends(get_db)):
    return {"items": get_latest_recommendations(db, session_id)}
