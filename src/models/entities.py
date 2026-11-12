"""Domain entities and Pydantic schemas for MealBridge."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


class DeliveryWindow(BaseModel):
    start: str = Field(..., description="Start time in HH:MM format, e.g. '12:30'")
    end: str = Field(..., description="End time in HH:MM format, e.g. '13:30'")


class Volunteer(BaseModel):
    volunteer_id: str
    first_name: str
    phone: str
    primary_zone: str
    active_stops_count: int = 0
    spare_capacity: int = 0
    status: Literal["available", "active", "cancelled", "off_duty"] = "available"
    availability_window: DeliveryWindow
    notes: str = ""


class Stop(BaseModel):
    stop_id: str
    recipient_name: str
    address: str
    zone: str
    delivery_window: DeliveryWindow
    dietary_note: str = "Standard"
    mobility_note: str = ""
    phone: str
    preferred_contact: Literal["phone", "sms"] = "phone"
    current_owner_id: str = "dispatcher"
    status: Literal[
        "scheduled",
        "at_risk",
        "reassign_proposed",
        "reassigned",
        "out_for_delivery",
        "delivered",
        "unable_to_deliver",
        "recipient_declined",
        "needs_escalation",
        "closed",
    ] = "scheduled"
    contact_status: Literal[
        "not_attempted",
        "attempted_no_answer",
        "reached",
        "wrong_number",
        "unreachable_escalated",
    ] = "not_attempted"
    delivery_outcome: str | None = None
    contact_outcome: str | None = None
    contact_notes: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DispatchEvent(BaseModel):
    event_id: str
    stop_id: str
    from_status: str
    to_status: str
    actor: str
    reason: str
    source_update_id: str | None = None
    previous_owner_id: str | None = None
    new_owner_id: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoiceUpdate(BaseModel):
    update_id: str
    raw_transcript: str
    speaker_id: str | None = None
    speaker_name: str | None = None
    intent: Literal[
        "cancel",
        "delay",
        "swap",
        "partial_unavailable",
        "available",
        "delivered",
        "recipient_unreachable",
        "other",
    ] = "other"
    affected_stop_ids: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    ambiguities: list[str] = Field(default_factory=list)
    needs_confirmation: bool = False
    source_audio_path: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReassignmentProposal(BaseModel):
    stop_id: str
    current_owner_id: str
    proposed_owner_id: str
    candidate_name: str
    score: float
    reason: str
    safety_checked: bool = True
    safety_notes: str = ""
    status: Literal["proposed", "approved", "rejected", "escalated"] = "proposed"


class ContactAttempt(BaseModel):
    attempt_id: str
    stop_id: str
    recipient_name: str
    phone: str
    method: Literal["phone", "sms", "in_person"]
    outcome: Literal["reached", "no_answer", "wrong_number", "declined"]
    attempt_number: int = 1
    script_used: str = ""
    notes: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
