# Urbani Kiosco MVP (Spec-Driven)

MVP rapido alineado a los specs en `docs/specs`.

## Stack
- Backend: FastAPI + SQLAlchemy
- DB: SQLite (desarrollo rápido) / PostgreSQL 15 (producción, con docker-compose)
- Front: vistas estaticas servidas por FastAPI (`/kiosk`, `/dashboard`)

## Arranque rapido
1. Asegúrate de tener Docker Desktop corriendo.
2. Ejecuta `start.bat` (Windows) o sigue los pasos manuales abajo.

### Pasos manuales
1. Copiar variables de entorno:
   - `copy .env.example .env`
2. Levantar base de datos:
   - `docker compose up -d db`
3. Crear entorno e instalar dependencias:
   - `python -m venv .venv`
   - `.\.venv\Scripts\Activate.ps1`
   - `pip install -r apps/api/requirements.txt`
4. Seed de datos:
   - `python apps/api/scripts/seed_data.py`
5. Ejecutar API:
   - `uvicorn apps.api.app.main:app --reload --port 8000`

## URLs
- API docs: http://localhost:8000/docs
- Kiosk MVP: http://localhost:8000/kiosk
- Dashboard MVP: http://localhost:8000/dashboard

## Token
Para endpoints del kiosco enviar header:
- `X-Kiosk-Token: dev-kiosk-token`

## Cobertura MVP
- Sesiones, respuestas y eventos UX
- Emision de tickets con ETA simulado
- Recomendador deterministico con fallback
- Leads para dashboard y resumen ejecutivo basico
- Asistencia LLM mock segura (sin inventar stock)
