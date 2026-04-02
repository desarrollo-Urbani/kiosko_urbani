from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SessionCreateRequest(BaseModel):
    kiosk_id: str


class SessionResponse(BaseModel):
    session_id: str
    status: str


class AnswerCreateRequest(BaseModel):
    question_key: str
    answer_value: Any
    answer_label: str = ""


class TicketCreateRequest(BaseModel):
    session_id: str
    name: str | None = None
    phone: str | None = None


class TicketResponse(BaseModel):
    ticket_number: str
    eta_minutes: int


class QueueTicketStatusPatchRequest(BaseModel):
    status: str
    executive_id: str | None = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {"waiting", "called", "in_service", "completed", "no_show"}
        if value not in allowed:
            raise ValueError(f"status must be one of: {', '.join(sorted(allowed))}")
        return value


class QueueCallNextRequest(BaseModel):
    executive_id: str


class RecommendationRunRequest(BaseModel):
    session_id: str


class RecommendationItemResponse(BaseModel):
    property_id: str
    project_name: str
    commune: str
    property_type: str
    price_uf: float
    bedrooms: int
    bathrooms: int
    total_score: int
    match_level: str
    match_tags: list[str]
    explanation: str
    match_debug: dict[str, Any]


class AssistRequest(BaseModel):
    session_id: str
    current_screen: str
    user_query: str | None = None


class AssistResponse(BaseModel):
    message: str
    intent: str
    hint: str
    safe_fallback: str


class EventCreateRequest(BaseModel):
    session_id: str
    event_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class LeadResponse(BaseModel):
    id: str
    session_id: str
    lead_status: str
    priority: str
    executive_summary: str | None
    created_at: datetime


class LeadStatusPatchRequest(BaseModel):
    lead_status: str

    @field_validator("lead_status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {
            "listo",
            "casi listo",
            "falta ahorro",
            "falta credito",
            "sin datos suficientes",
        }
        if value not in allowed:
            raise ValueError(f"lead_status must be one of: {', '.join(sorted(allowed))}")
        return value


class LeadSummaryResponse(BaseModel):
    executive_summary: list[str]
    suggested_approach: str
