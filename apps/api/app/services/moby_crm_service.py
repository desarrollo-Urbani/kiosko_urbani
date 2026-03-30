import re
from typing import Any

import httpx

from ..config import settings


def _normalize_base_url(url: str) -> str:
    clean = (url or "").strip().rstrip("/")
    if not clean:
        return "https://app-api.mobysuite.com"
    if clean.startswith("http://") or clean.startswith("https://"):
        return clean
    return f"https://{clean}"


def normalize_rut(rut: str) -> str:
    compact = re.sub(r"[^0-9kK-]", "", str(rut or "")).upper()
    if "-" in compact:
        return compact
    if len(compact) >= 2:
        return f"{compact[:-1]}-{compact[-1]}"
    return compact


def _extract_token(payload: dict[str, Any]) -> str | None:
    nested = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    return (
        payload.get("access_token")
        or payload.get("token")
        or payload.get("accessToken")
        or payload.get("id_token")
        or nested.get("access_token")
        or nested.get("accessToken")
        or nested.get("token")
    )


def _extract_customer(payload: Any, expected_rut: str) -> dict[str, Any] | None:
    expected = normalize_rut(expected_rut)

    if isinstance(payload, dict):
        candidate_rut = normalize_rut(
            str(
                payload.get("rut")
                or payload.get("customer_rut")
                or payload.get("document_number")
                or payload.get("document")
                or ""
            )
        )

        has_name = any(
            payload.get(key)
            for key in ("name", "full_name", "customer_name", "first_name", "nombres", "nombre", "razonSocial")
        )
        has_contact = any(
            payload.get(key)
            for key in ("email", "mail", "phone", "mobile", "telefono", "telefonoUno", "telefonoDos")
        )

        if candidate_rut and (candidate_rut == expected or has_name or has_contact):
            name = (
                payload.get("name")
                or payload.get("full_name")
                or payload.get("customer_name")
                or f"{payload.get('first_name', '')} {payload.get('last_name', '')}".strip()
                or payload.get("nombres")
                or f"{payload.get('nombre', '')} {payload.get('apellido', '')}".strip()
                or payload.get("razonSocial")
                or "Cliente"
            )
            email = payload.get("email") or payload.get("mail") or payload.get("correo")
            phone = (
                payload.get("phone")
                or payload.get("mobile")
                or payload.get("telefono")
                or payload.get("cellphone")
                or payload.get("telefonoUno")
                or payload.get("telefonoDos")
            )
            return {
                "rut": candidate_rut or expected,
                "name": str(name).strip(),
                "email": str(email).strip() if email else "",
                "phone": str(phone).strip() if phone else "",
                "raw": payload,
            }

        for value in payload.values():
            found = _extract_customer(value, expected_rut)
            if found:
                return found

    if isinstance(payload, list):
        for value in payload:
            found = _extract_customer(value, expected_rut)
            if found:
                return found

    return None


def find_customer_by_rut(rut: str) -> dict[str, Any]:
    if not settings.moby_client_id or not settings.moby_client_secret:
        return {"found": False, "message": "Moby CRM credentials not configured."}

    base_url = _normalize_base_url(settings.moby_base_url)
    normalized_rut = normalize_rut(rut)
    timeout = httpx.Timeout(12.0, connect=8.0)

    with httpx.Client(timeout=timeout) as client:
        token_res = client.post(
            f"{base_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.moby_client_id,
                "client_secret": settings.moby_client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_res.status_code >= 400:
            return {"found": False, "message": f"Auth error with CRM ({token_res.status_code})."}

        token_payload = token_res.json()
        access_token = _extract_token(token_payload)
        if not access_token:
            return {"found": False, "message": "CRM token not received."}

        customer_res = client.get(
            f"{base_url}/v1/api/integrations/customers/rut/{normalized_rut}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if customer_res.status_code == 404:
            return {"found": False, "message": "No se encontro cliente con ese RUT."}
        if customer_res.status_code >= 400:
            return {
                "found": False,
                "message": f"CRM search error ({customer_res.status_code}).",
            }

        customer_payload = customer_res.json()
        customer = _extract_customer(customer_payload, normalized_rut)
        if not customer:
            return {"found": False, "message": "Cliente no encontrado en CRM."}

        return {"found": True, "message": "Cliente encontrado.", "customer": customer}
