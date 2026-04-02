# Urbani Kiosco MVP (Spec-Driven)

MVP rapido alineado a los specs en `docs/specs`.

## Stack
- Backend: FastAPI + SQLAlchemy
- DB: SQLite (desarrollo rapido) / PostgreSQL 15 (produccion, con docker-compose)
- Front:
  - Kiosco: React/Vite en `apps/kiosk-web` (puerto 5173 en dev)
  - Dashboard: vista estatica servida por FastAPI (`/dashboard`)

## Frontend canonico
- Kiosco operativo: `apps/kiosk-web` (Vite dev server en `http://127.0.0.1:5173`).
- Dashboard operativo: `apps/api/app/static/dashboard/index.html` (servido en `/dashboard`).
- Ruta `/kiosk` en API queda **deprecada** y fuera de uso.

## Arranque rapido
1. Asegurate de tener Docker Desktop corriendo.
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
   - `cd apps/api`
   - `alembic upgrade head`
   - `cd ../..`
   - `python apps/api/scripts/seed_data.py`
5. Ejecutar API:
   - `uvicorn apps.api.app.main:app --reload --port 8000`

## Migraciones DB (Alembic)
- Crear nueva migracion:
  - `cd apps/api`
  - `alembic revision -m "descripcion_cambio"`
- Aplicar migraciones:
  - `cd apps/api`
  - `alembic upgrade head`
- Revertir una migracion:
  - `cd apps/api`
  - `alembic downgrade -1`

## URLs
- API docs: http://localhost:8000/docs
- Kiosk MVP (vigente): http://127.0.0.1:5173
- Dashboard MVP: http://localhost:8000/dashboard

## Token
Para endpoints del kiosco enviar header:
- `X-Kiosk-Token: dev-kiosk-token`

## Auth usuario (sin contraseña)
- Login:
  - `POST /api/v1/auth/login` con body `{"email":"usuario@dominio.cl"}`
- Perfil actual:
  - `GET /api/v1/auth/me` con header `Authorization: Bearer <token>`
- Roles soportados:
  - `executive`
  - `supervisor`
  - `admin`

## Cobertura MVP
- Sesiones, respuestas y eventos UX
- Emision de tickets con ETA simulado
- Recomendador deterministico con fallback
- Leads para dashboard y resumen ejecutivo basico
- Asistencia LLM mock segura (sin inventar stock)

## Cola de atencion (estados estandarizados)
- Estados soportados: `waiting`, `called`, `in_service`, `completed`, `no_show`.
- Endpoints:
  - `POST /api/v1/queue/tickets`
  - `GET /api/v1/queue/tickets`
  - `PATCH /api/v1/queue/tickets/{ticket_id}/status`
- Auditoria minima:
  - `queue_ticket_created`
  - `queue_ticket_status_changed`
