from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


# Supabase free tier pooler (Session mode) limita a 15 conexiones totales.
# Con 2 workers gunicorn: pool_size=5 → máx 10 conexiones + 2 overflow = 12 total (seguro bajo el límite).
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=2,
    pool_timeout=30,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
