from fastapi import Header, HTTPException, status

from .config import settings


async def verify_kiosk_token(x_kiosk_token: str | None = Header(default=None)) -> None:
    if x_kiosk_token != settings.kiosk_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid kiosk token",
        )
