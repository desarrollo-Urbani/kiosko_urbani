FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema para psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Crear directorio de estáticos si no existe
RUN mkdir -p app/static/dashboard app/static/kiosk app/static/tools

ENV PYTHONUNBUFFERED=1

# 4 workers uvicorn gestionados por gunicorn
# Fórmula: 2 * núcleos + 1  (en VPS 2 vCPU → 5 workers)
CMD ["gunicorn", "app.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-"]
