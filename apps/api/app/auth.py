from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import AppUser, AppUserSession


def _csv_to_set(raw: str) -> set[str]:
    return {item.strip().lower() for item in raw.split(",") if item.strip()}


DEFAULT_ALLOWED_EMAILS = {
    "notificaciones@mobysuite.com",
    "eflores@urbani.cl",
    "agallegos@urbani.cl",
    "mmunoz@urbani.cl",
    "poyarce@urbani.cl",
    "gbasualto@urbani.cl",
    "gtorres@constructoragarcia.cl",
    "dinostroza@urbani.cl",
    "urbani@mobysuite.cl",
    "cbasualto@urbani.cl",
    "fcastillo@urbani.cl",
    "aperez@urbani.cl",
    "esanzana@constructoragarcia.cl",
    "despinoza@constructoragarcia.cl",
    "respinoza@constructoragarcia.cl",
    "aespinoza@constructoragarcia.cl",
    "vambiado@urbani.cl",
    "fadams@urbani.cl",
    "lquinones@urbani.cl",
    "varias@urbani.cl",
    "fulloa@urbani.cl",
    "squiroz@urbani.cl",
    "econtreras@urbani.cl",
    "ageneral@urbani.cl",
    "agreene@grupopatagual.cl",
    "tcontreras@urbani.cl",
    "mburgos@urbani.cl",
    "kpiedra@urbani.cl",
    "chschussler@me.com",
    "lsandoval@urbani.cl",
    "crodriguez@urbani.cl",
    "lnavarrete@urbani.cl",
    "hmolina@evainmobiliaria.com",
    "pcruz@sebamar.cl",
    "nmonsalves@urbani.cl",
    "chernandez@urbani.cl",
    "pcabrera@grupopatagual.cl",
    "vvillegas@urbani.cl",
    "vendedorexterno@urbani.cl",
    "lcabezas@urbani.cl",
    "dmardones@urbani.cl",
    "ideruyt@urbani.cl",
    "desarrollo@urbani.cl",
    "pezweb@gmail.com",
    "pgoldberg@urbani.cl",
    "idonoso@urbani.cl",
    "dhernandez@grupopatagual.cl",
    "pcampos@grupopatagual.cl",
    "jtoledo@grupopatagual.cl",
    "rachata@grupopatagual.cl",
    "nicomonsalves18@gmail.com",
    "mibacache@urbani.cl",
    "amontecino@urbani.cl",
    "fmunoz@urbani.cl",
    "comercial@urbani.cl",
    "mpvera@urbani.cl",
    "fgarciah@urbani.cl",
    "amatamalainzunza@gmail.com",
    "anahi.albnornoz.g@gmail.com",
    "jhernandez@urbani.cl",
    "aviveros@urbani.cl",
    "moisesvenegasmontt@gmail.com",
    "cgaticaf@icomercial.ucsc.cl",
    "camilapetermannv@gmail.com",
    "galletti443@gmail.com",
    "alianzas@grupounity.cl",
    "munozantonia296@gmail.com",
    "espinoza.paula.c@gmail.com",
    "pgodoy@urbani.cl",
    "pordenes@jce.cl",
    "diegoaarojas@gmail.com",
    "practicasubsidio@urbani.cl",
}


@dataclass
class AuthPrincipal:
    user_id: int | None
    email: str
    role: str
    auth_type: str


def _resolve_allowed_emails() -> set[str]:
    configured = _csv_to_set(settings.executive_allowed_emails)
    return configured or DEFAULT_ALLOWED_EMAILS


def _resolve_role(email: str) -> str:
    email_l = email.lower()
    if email_l in _csv_to_set(settings.admin_emails):
        return "admin"
    if email_l in _csv_to_set(settings.supervisor_emails):
        return "supervisor"
    return "executive"


def verify_kiosk_token(x_kiosk_token: str | None = Header(default=None)) -> None:
    if x_kiosk_token != settings.kiosk_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid kiosk token",
        )


def create_user_session(email: str, db: Session) -> dict[str, object]:
    normalized = email.strip().lower()
    if not normalized:
        raise HTTPException(status_code=400, detail="Email is required")
    if normalized not in _resolve_allowed_emails():
        raise HTTPException(status_code=403, detail="User is not allowed")

    user = db.scalar(select(AppUser).where(AppUser.email == normalized))
    if not user:
        user = AppUser(email=normalized, role=_resolve_role(normalized), is_active=True)
        db.add(user)
        db.flush()
    elif not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")
    else:
        user.role = _resolve_role(normalized)

    expires_at = datetime.utcnow() + timedelta(minutes=settings.auth_session_ttl_minutes)
    token = secrets.token_urlsafe(32)
    session = AppUserSession(user_id=user.id, token=token, expires_at=expires_at)
    db.add(session)
    db.commit()
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": {"id": user.id, "email": user.email, "role": user.role},
    }


def _bearer_from_header(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def get_current_principal(
    authorization: str | None = Header(default=None),
    x_kiosk_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> AuthPrincipal:
    if x_kiosk_token and x_kiosk_token == settings.kiosk_token:
        return AuthPrincipal(user_id=None, email="kiosk@system", role="system", auth_type="kiosk_token")

    token = _bearer_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication")

    session = db.scalar(
        select(AppUserSession).where(
            and_(
                AppUserSession.token == token,
                AppUserSession.expires_at > datetime.utcnow(),
            )
        )
    )
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    user = db.get(AppUser, session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid session user")

    return AuthPrincipal(user_id=user.id, email=user.email, role=user.role, auth_type="user_session")


def require_roles(*roles: str, allow_kiosk: bool = True):
    allowed = set(roles)

    def _dep(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
        if allow_kiosk and principal.auth_type == "kiosk_token":
            return principal
        if principal.role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return principal

    return _dep
