"""Unit tests for MealBridge stop lifecycle, invariants, and database operations."""

import pytest
from src.lifecycle.database import (
    get_events_for_stop,
    get_stop,
    init_db,
    list_stops,
    load_seed_data,
    open_stops_by_owner,
    save_event,
    save_stop,
)
from src.lifecycle.state_machine import (
    InvariantViolationError,
    InvalidTransitionError,
    transition_stop,
)
from src.models.entities import DeliveryWindow, Stop


@pytest.fixture
def test_db(tmp_path):
    db_file = tmp_path / "test_mealbridge.db"
    init_db(db_file)
    load_seed_data(db_file)
    return db_file


def test_initial_seed_invariants(test_db):
    """Assert all stops loaded from seed data have exactly one owner."""
    stops = list_stops(test_db)
    assert len(stops) == 26
    for s in stops:
        assert s.current_owner_id is not None
        assert len(s.current_owner_id) > 0


def test_open_stops_by_owner_groups_properly(test_db):
    """Test grouping query powers the board without orphan stops."""
    by_owner = open_stops_by_owner(test_db)
    assert "V01" in by_owner
    assert len(by_owner["V01"]) == 21  # S01-S20 plus S26 duplicate
    assert "V02" in by_owner


def test_legal_stop_transition(test_db):
    """Test standard valid transition creates event and preserves single ownership."""
    stop = get_stop(test_db, "S01")
    assert stop.status == "scheduled"

    updated_stop, event = transition_stop(
        stop=stop,
        to_status="at_risk",
        actor="voice_parser",
        reason="Volunteer V01 vehicle breakdown",
        source_update_id="upd_1234",
    )
    save_stop(test_db, updated_stop)
    save_event(test_db, event)

    assert updated_stop.status == "at_risk"
    assert updated_stop.current_owner_id == "V01"  # Retains owner until reassignment
    assert event.from_status == "scheduled"
    assert event.to_status == "at_risk"

    # Verify event stored in DB
    events = get_events_for_stop(test_db, "S01")
    assert len(events) == 1
    assert events[0].reason == "Volunteer V01 vehicle breakdown"


def test_illegal_transition_raises_error(test_db):
    """Assert illegal jump raises InvalidTransitionError."""
    stop = get_stop(test_db, "S02")
    # Jumping from scheduled directly to closed is prohibited
    with pytest.raises(InvalidTransitionError):
        transition_stop(
            stop=stop,
            to_status="closed",
            actor="dispatcher",
            reason="Illegal jump",
        )


def test_closure_requires_both_delivery_and_contact_outcomes(test_db):
    """Enforce Invariant 3: Closing requires delivery outcome AND contact outcome."""
    stop = get_stop(test_db, "S03")
    stop.status = "delivered"
    stop.delivery_outcome = "Delivered on porch"
    stop.contact_outcome = None  # Missing contact outcome!

    # Attempt to close without contact outcome
    with pytest.raises(InvariantViolationError):
        transition_stop(
            stop=stop,
            to_status="closed",
            actor="dispatcher",
            reason="Deliver complete",
        )

    # Now add contact outcome and assert it closes successfully
    updated_stop, event = transition_stop(
        stop=stop,
        to_status="closed",
        actor="dispatcher",
        reason="Deliver complete and senior reached",
        contact_outcome="Reached by phone, senior confirmed meal received",
    )
    assert updated_stop.status == "closed"
    assert updated_stop.contact_outcome is not None
    assert updated_stop.delivery_outcome is not None


def test_no_orphan_stops_allowed(test_db):
    """Enforce Invariant 1: Stop cannot have an empty owner."""
    stop = get_stop(test_db, "S04")
    stop.current_owner_id = ""  # Orphan!

    with pytest.raises(InvariantViolationError):
        transition_stop(
            stop=stop,
            to_status="at_risk",
            actor="dispatcher",
            reason="Testing orphan prevention",
        )
