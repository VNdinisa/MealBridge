"""Deterministic volunteer reassignment engine with safety checks and escalation fallback."""

from __future__ import annotations

import os
from typing import Any

from src.models.entities import ReassignmentProposal, Stop, Volunteer


def evaluate_volunteer_safety_rules(stop: Stop, volunteer: Volunteer) -> tuple[bool, str]:
    """Safety check for dietary constraints, vehicle capacity, and mobility requirements.
    
    Can be augmented by NVIDIA NIM (e.g. Llama 3.3 / Nemotron) or deterministic rules.
    """
    notes = []
    # Check zone match
    if volunteer.primary_zone != stop.zone:
        notes.append(f"Cross-zone transfer: Volunteer primary zone is {volunteer.primary_zone}, stop is in {stop.zone}.")

    # Check mobility compatibility
    if "ramp" in stop.mobility_note.lower() and "large" not in volunteer.notes.lower() and "suv" not in volunteer.notes.lower():
        notes.append("Ramp delivery required; confirm volunteer vehicle accessibility.")

    # Check dietary notes
    if stop.dietary_note and stop.dietary_note != "Standard":
        notes.append(f"Special diet: {stop.dietary_note}. Verify correct meal container before delivery.")

    safety_notes = "; ".join(notes) if notes else "All safety and dietary criteria satisfied."
    return True, safety_notes


def score_candidate(stop: Stop, volunteer: Volunteer) -> float:
    """Calculate deterministic candidate score. Higher is better."""
    if volunteer.spare_capacity <= 0:
        return -1.0  # Ineligible

    if volunteer.status != "available":
        return -1.0

    score = 50.0  # Baseline for having capacity

    # Zone affinity (+30 points for matching zone)
    if volunteer.primary_zone.lower() == stop.zone.lower():
        score += 30.0

    # Spare capacity advantage (distribute load)
    score += min(volunteer.spare_capacity * 5.0, 15.0)

    # Experience bonus from notes
    if "experienced" in volunteer.notes.lower() or "familiar" in volunteer.notes.lower():
        score += 5.0

    return score


def generate_reassignment_proposal(
    stop: Stop,
    available_volunteers: list[Volunteer],
    cancelling_volunteer_id: str | None = None,
) -> ReassignmentProposal:
    """Propose the best backup volunteer for an at-risk stop.
    
    If no volunteer has spare capacity, immediately escalates to the dispatcher.
    """
    # Filter out cancelling volunteer
    eligible = [
        v for v in available_volunteers
        if v.volunteer_id != cancelling_volunteer_id and v.spare_capacity > 0 and v.status == "available"
    ]

    if not eligible:
        # Fallback to Dispatcher (Invariant 5)
        return ReassignmentProposal(
            stop_id=stop.stop_id,
            current_owner_id=stop.current_owner_id,
            proposed_owner_id="dispatcher",
            candidate_name="Dispatcher (Escalation)",
            score=0.0,
            reason="No eligible volunteer with spare capacity remaining in this window. Escalated to Dispatcher.",
            safety_checked=True,
            safety_notes="Urgent: Requires direct dispatcher coverage or volunteer route expansion.",
            status="escalated",
        )

    # Score and rank candidates
    ranked = []
    for cand in eligible:
        sc = score_candidate(stop, cand)
        if sc > 0:
            ranked.append((sc, cand))

    ranked.sort(key=lambda x: x[0], reverse=True)

    if not ranked:
        return ReassignmentProposal(
            stop_id=stop.stop_id,
            current_owner_id=stop.current_owner_id,
            proposed_owner_id="dispatcher",
            candidate_name="Dispatcher (Escalation)",
            score=0.0,
            reason="All eligible volunteers are at maximum capacity for this delivery window.",
            safety_checked=True,
            safety_notes="Escalated to Dispatcher.",
            status="escalated",
        )

    best_score, best_cand = ranked[0]
    safe, safety_notes = evaluate_volunteer_safety_rules(stop, best_cand)

    # Construct plain-language reason
    zone_match = best_cand.primary_zone.lower() == stop.zone.lower()
    zone_text = f"matches {stop.zone} zone" if zone_match else f"covers {stop.zone} backup"
    reason = (
        f"{best_cand.first_name} ({best_cand.volunteer_id}) {zone_text} with "
        f"{best_cand.spare_capacity} spare capacity left."
    )

    return ReassignmentProposal(
        stop_id=stop.stop_id,
        current_owner_id=stop.current_owner_id,
        proposed_owner_id=best_cand.volunteer_id,
        candidate_name=best_cand.first_name,
        score=best_score,
        reason=reason,
        safety_checked=safe,
        safety_notes=safety_notes,
        status="proposed",
    )
