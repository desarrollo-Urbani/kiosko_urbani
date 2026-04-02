from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import create_user_session, get_current_principal
from ..database import get_db
from ..schemas import AuthLoginRequest, AuthLoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthLoginResponse)
def login(payload: AuthLoginRequest, db: Session = Depends(get_db)):
    return create_user_session(payload.email, db)


@router.get("/me")
def me(principal=Depends(get_current_principal)):
    return {
        "user_id": principal.user_id,
        "email": principal.email,
        "role": principal.role,
        "auth_type": principal.auth_type,
    }
