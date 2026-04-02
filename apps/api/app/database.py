from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


# pool_size: conexiones permanentes al pool  (4 workers × 5 = 20 conexiones)
# max_overflow: conexiones extra en picos    (total máx = 40)
# pool_timeout: segundos esperando una conexión antes de error
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
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
