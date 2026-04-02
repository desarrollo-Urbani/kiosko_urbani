from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import and_, create_engine, select, text
from sqlalchemy.orm import Session
from sqlalchemy.engine import URL

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
    name: str | None
    role: str
    auth_type: str


_external_email_cache: set[str] = set()
_external_email_cache_until: datetime | None = None
_external_user_cache: dict[str, str | None] = {}


def _resolve_allowed_emails() -> set[str]:
    external = _load_active_users_from_mysql()
    if external:
        return set(external.keys())
    configured = _csv_to_set(settings.executive_allowed_emails)
    return configured or DEFAULT_ALLOWED_EMAILS


def _load_active_users_from_mysql() -> dict[str, str | None]:
    global _external_email_cache, _external_email_cache_until, _external_user_cache

    if not settings.auth_mysql_enabled:
        return {}

    now = datetime.utcnow()
    if _external_email_cache_until and _external_email_cache_until > now:
        return _external_user_cache

    if not all(
        [
            settings.auth_mysql_user,
            settings.auth_mysql_password,
            settings.auth_mysql_host,
            settings.auth_mysql_database,
        ]
    ):
        return {}

    try:
        url = URL.create(
            "mysql+pymysql",
            username=settings.auth_mysql_user,
            password=settings.auth_mysql_password,
            host=settings.auth_mysql_host,
            port=settings.auth_mysql_port,
            database=settings.auth_mysql_database,
        )
        engine = create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        query = text(
            f"SELECT {settings.auth_mysql_email_column} AS email, {settings.auth_mysql_name_column} AS nombre "
            f"FROM {settings.auth_mysql_users_view} "
            f"WHERE {settings.auth_mysql_active_column} = 1"
        )
        with engine.connect() as conn:
            rows = conn.execute(query).all()
        users = {
            str(row.email).strip().lower(): (str(row.nombre).strip() if row.nombre is not None else None)
            for row in rows
            if row.email
        }
        _external_user_cache = users
        _external_email_cache = set(users.keys())
        _external_email_cache_until = now + timedelta(minutes=5)
        return users
    except Exception:
        _external_user_cache = {}
        _external_email_cache = set()
        _external_email_cache_until = now + timedelta(minutes=2)
        return {}


def get_user_name_by_email(email: str) -> str | None:
    users = _load_active_users_from_mysql()
    return users.get(email.strip().lower())


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
    user_name = get_user_name_by_email(user.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": {"id": user.id, "email": user.email, "name": user_name, "role": user.role},
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
        return AuthPrincipal(user_id=None, email="kiosk@system", name="Kiosk", role="system", auth_type="kiosk_token")

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

    return AuthPrincipal(
        user_id=user.id,
        email=user.email,
        name=get_user_name_by_email(user.email),
        role=user.role,
        auth_type="user_session",
    )


def require_roles(*roles: str, allow_kiosk: bool = True):
    allowed = set(roles)

    def _dep(principal: AuthPrincipal = Depends(get_current_principal)) -> AuthPrincipal:
        if allow_kiosk and principal.auth_type == "kiosk_token":
            return principal
        if principal.role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return principal

    return _dep
