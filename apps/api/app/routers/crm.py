from fastapi import APIRouter, Depends

from ..auth import verify_kiosk_token
from ..services.moby_crm_service import find_customer_by_rut

router = APIRouter(prefix="/crm", tags=["crm"], dependencies=[Depends(verify_kiosk_token)])


@router.get("/customers/by-rut/{rut}")
def get_customer_by_rut(rut: str):
    return find_customer_by_rut(rut)
