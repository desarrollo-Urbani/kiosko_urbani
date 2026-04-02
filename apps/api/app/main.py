from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import auth, crm, dashboard, events, llm, queue, recommendations, sessions

app = FastAPI(title="Urbani Kiosco API", version="0.1.0")

app.include_router(sessions.router, prefix="/api/v1")
app.include_router(queue.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
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
    raise HTTPException(
        status_code=410,
        detail="Kiosk static route is deprecated. Use the kiosk-web app (Vite) on port 5173.",
    )


@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(static_dir / "dashboard" / "index.html")


@app.get("/executive-dashboard", include_in_schema=False)
def executive_dashboard_page():
    return FileResponse(static_dir / "executive" / "index.html")


@app.get("/supervisor-dashboard", include_in_schema=False)
def supervisor_dashboard_page():
    return FileResponse(static_dir / "supervisor" / "index.html")
