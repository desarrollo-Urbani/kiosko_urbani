import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class KioskSession(Base):
    __tablename__ = "kiosk_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kiosk_device_id: Mapped[str | None] = mapped_column(String, nullable=True)
    session_key: Mapped[str] = mapped_column(String, unique=True)
    status: Mapped[str] = mapped_column(String, default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    answers: Mapped[list["SessionAnswer"]] = relationship(back_populates="session")


class SessionAnswer(Base):
    __tablename__ = "session_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("kiosk_sessions.id"))
    question_key: Mapped[str] = mapped_column(String)
    answer_value: Mapped[dict] = mapped_column(JSON)
    answer_label: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[KioskSession] = relationship(back_populates="answers")


class QueueTicket(Base):
    __tablename__ = "queue_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("kiosk_sessions.id"))
    ticket_number: Mapped[str] = mapped_column(String, unique=True)
    customer_name: Mapped[str | None] = mapped_column(String, nullable=True)
    customer_phone: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="waiting")
    estimated_wait_minutes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String)
    commune: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    delivery_status: Mapped[str] = mapped_column(String)
    subsidy_available: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    properties: Mapped[list["Property"]] = relationship(back_populates="project")


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    property_type: Mapped[str] = mapped_column(String)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    area_total_m2: Mapped[float] = mapped_column(Float)
    price_uf: Mapped[float] = mapped_column(Float)
    dividend_est_clp: Mapped[int] = mapped_column(Integer)
    stock_status: Mapped[str] = mapped_column(String, default="available")
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)

    project: Mapped[Project] = relationship(back_populates="properties")


class RecommendationRun(Base):
    __tablename__ = "recommendation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("kiosk_sessions.id"))
    engine_version: Mapped[str] = mapped_column(String, default="mvp-v1")
    match_params: Mapped[dict] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RecommendationItem(Base):
    __tablename__ = "recommendation_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("recommendation_runs.id"))
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.id"))
    match_score: Mapped[int] = mapped_column(Integer)
    match_tags: Mapped[list[str]] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(Text)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(ForeignKey("kiosk_sessions.id"), unique=True)
    lead_status: Mapped[str] = mapped_column(String, default="new")
    priority: Mapped[str] = mapped_column(String, default="medium")
    raw_data: Mapped[dict] = mapped_column(JSON)
    executive_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
