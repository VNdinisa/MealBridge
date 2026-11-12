"""State machine and invariant enforcement for MealBridge stops."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.models.entities import DispatchEvent, Stop


class InvariantViolationError(Exception):
    """Raised when an action violates a non-negotiable MealBridge invariant."""
    pass


class InvalidTransitionError(Exception):
    """Raised when an illegal status transition is attempted."""
    pass


# Allowed state transitions graph
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "scheduled": {"at_risk", "reassign_proposed", "out_for_delivery", "needs_escalation"},
    "at_risk": {"reassign_proposed", "reassigned", "needs_escalation", "scheduled"},
    "reassign_proposed": {"reassigned", "at_risk", "needs_escalation"},
    "reassigned": {"out_for_delivery", "at_risk", "needs_escalation"},
    "out_for_delivery": {"delivered", "unable_to_deliver", "recipient_declined", "at_risk"},
    "delivered": {"closed"},
    "unable_to_deliver": {"closed", "needs_escalation"},
    "recipient_declined": {"closed"},
    "needs_escalation": {"reassign_proposed", "reassigned", "closed", "out_for_delivery"},
    "closed": set(),  # Terminal state
}

# Allowed contact statuses
VALID_CONTACT_STATUSES = {
    "not_attempted",
    "attempted_no_answer",
    "reached",
    "wrong_number",
    "unreachable_escalated",
}


def validate_single_ownership(stop: Stop) -> None:
    """Enforces Invariant 1: Every non-closed stop must have exactly 1 owner."""
    if stop.status != "closed":
        if not stop.current_owner_id or not stop.current_owner_id.strip():
            raise InvariantViolationError(
                f"Invariant 1 Violated: Non-closed stop {stop.stop_id} has no owner (orphan)."
            )


def validate_closure_criteria(stop: Stop) -> None:
    """Enforces Invariant 3: Closing requires both a delivery outcome and a contact outcome."""
    if not stop.delivery_outcome or not stop.delivery_outcome.strip():
        raise InvariantViolationError(
            f"Invariant 3 Violated: Stop {stop.stop_id} cannot close without a delivery outcome."
        )
    if not stop.contact_outcome or not stop.contact_outcome.strip():
        raise InvariantViolationError(
            f"Invariant 3 Violated: Stop {stop.stop_id} cannot close without a contact outcome."
        )


def transition_stop(
    stop: Stop,
    to_status: str,
    actor: str,
    reason: str,
    new_owner_id: str | None = None,
    source_update_id: str | None = None,
    delivery_outcome: str | None = None,
    contact_outcome: str | None = None,
    contact_status: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> tuple[Stop, DispatchEvent]:
    """Execute a state transition on a stop, enforcing invariants and returning an audit event."""
    from_status = stop.status

    # Idempotent transition check: if already in target state, gracefully allow update without error
    if from_status == to_status:
        now_iso = datetime.now(timezone.utc).isoformat()
        prev_owner = stop.current_owner_id
        if new_owner_id and stop.current_owner_id != new_owner_id:
            stop.current_owner_id = new_owner_id
        if contact_status:
            stop.contact_status = contact_status
        if delivery_outcome:
            stop.delivery_outcome = delivery_outcome
        if contact_outcome:
            stop.contact_outcome = contact_outcome
        stop.updated_at = now_iso
        validate_single_ownership(stop)

        event = DispatchEvent(
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            stop_id=stop.stop_id,
            from_status=from_status,
            to_status=to_status,
            actor=actor,
            reason=reason,
            source_update_id=source_update_id,
            previous_owner_id=prev_owner,
            new_owner_id=new_owner_id if new_owner_id != prev_owner else None,
            timestamp=now_iso,
            metadata=metadata or {},
        )
        return stop, event

    # Check allowed transitions
    allowed = ALLOWED_TRANSITIONS.get(from_status, set())
    if to_status not in allowed:
        raise InvalidTransitionError(
            f"Illegal state transition for stop {stop.stop_id}: cannot transition from '{from_status}' to '{to_status}'."
        )

    # Update delivery/contact outcomes if provided
    if delivery_outcome:
        stop.delivery_outcome = delivery_outcome
    if contact_outcome:
        stop.contact_outcome = contact_outcome

    # Check closure requirements
    if to_status == "closed":
        effective_delivery = delivery_outcome or stop.delivery_outcome
        effective_contact = contact_outcome or stop.contact_outcome
        if not effective_delivery:
            raise InvariantViolationError(
                f"Cannot close stop {stop.stop_id}: missing delivery outcome."
            )
        if not effective_contact:
            raise InvariantViolationError(
                f"Cannot close stop {stop.stop_id}: missing contact outcome."
            )
        stop.delivery_outcome = effective_delivery
        stop.contact_outcome = effective_contact

    # Handle ownership updates
    previous_owner = stop.current_owner_id
    effective_owner = previous_owner
    if new_owner_id:
        effective_owner = new_owner_id
        stop.current_owner_id = new_owner_id

    # If transitioning to needs_escalation and no new owner given, default to dispatcher
    if to_status == "needs_escalation" and (not new_owner_id or new_owner_id == previous_owner):
        stop.current_owner_id = "dispatcher"
        effective_owner = "dispatcher"

    # Enforce Invariant 1: Single ownership on non-closed stops
    stop.status = to_status
    if contact_status:
        if contact_status not in VALID_CONTACT_STATUSES:
            raise ValueError(f"Invalid contact status: {contact_status}")
        stop.contact_status = contact_status

    validate_single_ownership(stop)

    now_iso = datetime.now(timezone.utc).isoformat()
    stop.updated_at = now_iso

    # Create immutable event record
    event = DispatchEvent(
        event_id=f"evt_{uuid.uuid4().hex[:10]}",
        stop_id=stop.stop_id,
        from_status=from_status,
        to_status=to_status,
        actor=actor,
        reason=reason,
        source_update_id=source_update_id,
        previous_owner_id=previous_owner,
        new_owner_id=effective_owner if effective_owner != previous_owner else None,
        timestamp=now_iso,
        metadata=metadata or {},
    )

    return stop, event
