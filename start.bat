@echo off
echo Iniciando Urbani Kiosco...

REM Crear entorno virtual si no existe
if not exist .venv (
    python -m venv .venv
)

REM Activar entorno
call .\.venv\Scripts\activate

REM Instalar dependencias
pip install -r apps/api/requirements.txt

REM Copiar .env si no existe
if not exist .env (
    copy .env.example .env
)

REM Levantar DB
docker compose up -d db

REM Esperar a que DB esté lista
timeout /t 10 /nobreak > nul

REM Ejecutar seed
python apps/api/scripts/seed_data.py

REM Ejecutar API
uvicorn apps.api.app.main:app --reload --port 8000

pause