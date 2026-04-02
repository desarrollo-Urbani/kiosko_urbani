from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import crm, dashboard, events, llm, queue, recommendations, sessions

app = FastAPI(title="Urbani Kiosco API", version="0.1.0")

Base.metadata.create_all(bind=engine)

app.include_router(sessions.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(llm.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(crm.router, prefix="/api/v1")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/kiosk", include_in_schema=False)
def kiosk_page():
    return FileResponse(static_dir / "kiosk" / "index.html")


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(static_dir / "dashboard" / "index.html")


@app.get("/executive-dashboard", include_in_schema=False)
def executive_dashboard_page():
    return FileResponse(static_dir / "executive" / "index.html")
