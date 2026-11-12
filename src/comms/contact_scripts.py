"""Empathetic, plain-language communications generator for older adults and volunteers."""

from __future__ import annotations

import os
from typing import Any

from src.models.entities import Stop, Volunteer


def generate_senior_contact_script(
    stop: Stop,
    new_volunteer_name: str,
    dispatcher_phone: str = "+1-555-0100",
) -> dict[str, str]:
    """Generate calm, accessible communication scripts tailored to older adults.
    
    Adheres strictly to Omotayo's older-adult UX checklist:
    - Short, clear sentences.
    - Calm, reassuring tone.
    - Zero urgency pressure or anxiety-inducing language.
    - Never asks for money, credentials, or sensitive information.
    - Reassures that their meal is on the way.
    """
    first_name = stop.recipient_name.split()[0]
    window = f"{stop.delivery_window.start} to {stop.delivery_window.end}"

    # Phone call spoken script
    phone_script = (
        f"Hello {first_name}, this is your community MealBridge program. "
        f"We are calling to let you know your meal is safely on its way today. "
        f"Our friendly volunteer, {new_volunteer_name}, will be delivering your meal "
        f"between {window}. "
        f"There is no action needed from you—just answer your door when they arrive. "
        f"If you have any questions, you can always reach our dispatch team at {dispatcher_phone}. "
        f"Have a wonderful afternoon!"
    )

    # SMS / Text message script (concise, high clarity)
    sms_script = (
        f"Hi {first_name}, your MealBridge meal is on the way today! "
        f"{new_volunteer_name} will arrive between {window}. "
        f"No action needed. Questions? Call us at {dispatcher_phone}."
    )

    # Voicemail script if no answer
    voicemail_script = (
        f"Hello {first_name}, this is MealBridge checking in. "
        f"Your meal is coming today between {window}, brought by {new_volunteer_name}. "
        f"No need to call us back unless you have a question. Our number is {dispatcher_phone}."
    )

    return {
        "phone_script": phone_script,
        "sms_script": sms_script,
        "voicemail_script": voicemail_script,
    }


def generate_volunteer_assignment_script(
    stops: list[Stop],
    volunteer: Volunteer,
) -> str:
    """Generate assignment briefing message for a backup volunteer."""
    lines = [
        f"Hello {volunteer.first_name},",
        f"Thank you for helping cover route updates today. Here are the stops assigned to you:",
        "",
    ]
    for s in stops:
        special = []
        if s.dietary_note and s.dietary_note != "Standard":
            special.append(f"Diet: {s.dietary_note}")
        if s.mobility_note:
            special.append(f"Note: {s.mobility_note}")
        extra = f" ({'; '.join(special)})" if special else ""
        lines.append(f"- {s.stop_id}: {s.recipient_name} at {s.address} [{s.delivery_window.start}-{s.delivery_window.end}]{extra}")

    lines.append("")
    lines.append("Please reply 'ACCEPT' to confirm these stops. Safe driving!")
    return "\n".join(lines)


def format_closure_note(
    stop_id: str,
    volunteer_id: str,
    delivery_time: str,
    contact_method: str,
    contact_time: str,
    notes: str = "Meal delivered safely, recipient confirmed doing well.",
) -> str:
    """Create a standardized, factual audit closure note."""
    return (
        f"Stop {stop_id} | Delivered at {delivery_time} by {volunteer_id} | "
        f"Recipient reached via {contact_method} at {contact_time} | {notes}"
    )
