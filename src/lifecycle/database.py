"""SQLite database persistence for MealBridge with strict audit logging."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.models.entities import DeliveryWindow, DispatchEvent, Stop, VoiceUpdate, Volunteer


def get_connection(db_path: str | Path = "mealbridge.db") -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | Path = "mealbridge.db") -> None:
    """Initialize SQLite tables for volunteers, stops, events, and voice updates."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Volunteers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS volunteers (
                volunteer_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                primary_zone TEXT NOT NULL,
                active_stops_count INTEGER DEFAULT 0,
                spare_capacity INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'available',
                availability_start TEXT NOT NULL,
                availability_end TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)

        # Stops table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stops (
                stop_id TEXT PRIMARY KEY,
                recipient_name TEXT NOT NULL,
                address TEXT NOT NULL,
                zone TEXT NOT NULL,
                window_start TEXT NOT NULL,
                window_end TEXT NOT NULL,
                dietary_note TEXT DEFAULT 'Standard',
                mobility_note TEXT DEFAULT '',
                phone TEXT NOT NULL,
                preferred_contact TEXT DEFAULT 'phone',
                current_owner_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'scheduled',
                contact_status TEXT NOT NULL DEFAULT 'not_attempted',
                delivery_outcome TEXT,
                contact_outcome TEXT,
                contact_notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Immutable Append-Only Event Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispatch_events (
                event_id TEXT PRIMARY KEY,
                stop_id TEXT NOT NULL,
                from_status TEXT NOT NULL,
                to_status TEXT NOT NULL,
                actor TEXT NOT NULL,
                reason TEXT NOT NULL,
                source_update_id TEXT,
                previous_owner_id TEXT,
                new_owner_id TEXT,
                timestamp TEXT NOT NULL,
                metadata_json TEXT DEFAULT '{}'
            )
        """)

        # Voice updates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voice_updates (
                update_id TEXT PRIMARY KEY,
                raw_transcript TEXT NOT NULL,
                speaker_id TEXT,
                speaker_name TEXT,
                intent TEXT NOT NULL,
                affected_stop_ids_json TEXT NOT NULL,
                confidence REAL NOT NULL,
                ambiguities_json TEXT NOT NULL,
                needs_confirmation INTEGER NOT NULL DEFAULT 0,
                source_audio_path TEXT,
                created_at TEXT NOT NULL
            )
        """)

        conn.commit()


def load_seed_data(
    db_path: str | Path = "mealbridge.db",
    volunteers_json: str | Path = "data/seed/volunteers.json",
    stops_json: str | Path = "data/seed/stops.json",
) -> tuple[int, int]:
    """Load JSON seed data into SQLite."""
    init_db(db_path)

    with open(volunteers_json, "r", encoding="utf-8") as f:
        vols_data = json.load(f)
    with open(stops_json, "r", encoding="utf-8") as f:
        stops_data = json.load(f)

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for v in vols_data:
            cursor.execute("""
                INSERT OR REPLACE INTO volunteers (
                    volunteer_id, first_name, phone, primary_zone, active_stops_count,
                    spare_capacity, status, availability_start, availability_end, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                v["volunteer_id"],
                v["first_name"],
                v["phone"],
                v["primary_zone"],
                v.get("active_stops_count", 0),
                v.get("spare_capacity", 0),
                v.get("status", "available"),
                v["availability_window"]["start"],
                v["availability_window"]["end"],
                v.get("notes", ""),
            ))

        for s in stops_data:
            cursor.execute("""
                INSERT OR REPLACE INTO stops (
                    stop_id, recipient_name, address, zone, window_start, window_end,
                    dietary_note, mobility_note, phone, preferred_contact, current_owner_id,
                    status, contact_status, delivery_outcome, contact_outcome, contact_notes,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                s["stop_id"],
                s["recipient_name"],
                s["address"],
                s["zone"],
                s["delivery_window"]["start"],
                s["delivery_window"]["end"],
                s.get("dietary_note", "Standard"),
                s.get("mobility_note", ""),
                s["phone"],
                s.get("preferred_contact", "phone"),
                s["current_owner_id"],
                s.get("status", "scheduled"),
                s.get("contact_status", "not_attempted"),
                s.get("delivery_outcome"),
                s.get("contact_outcome"),
                s.get("contact_notes"),
            ))

        conn.commit()

    return len(vols_data), len(stops_data)


def save_stop(db_path: str | Path, stop: Stop) -> None:
    """Save an updated Stop record."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO stops (
                stop_id, recipient_name, address, zone, window_start, window_end,
                dietary_note, mobility_note, phone, preferred_contact, current_owner_id,
                status, contact_status, delivery_outcome, contact_outcome, contact_notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stop.stop_id,
            stop.recipient_name,
            stop.address,
            stop.zone,
            stop.delivery_window.start,
            stop.delivery_window.end,
            stop.dietary_note,
            stop.mobility_note,
            stop.phone,
            stop.preferred_contact,
            stop.current_owner_id,
            stop.status,
            stop.contact_status,
            stop.delivery_outcome,
            stop.contact_outcome,
            stop.contact_notes,
            stop.created_at,
            stop.updated_at,
        ))
        conn.commit()


def save_event(db_path: str | Path, event: DispatchEvent) -> None:
    """Append an event to the immutable dispatch log."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dispatch_events (
                event_id, stop_id, from_status, to_status, actor, reason,
                source_update_id, previous_owner_id, new_owner_id, timestamp, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.stop_id,
            event.from_status,
            event.to_status,
            event.actor,
            event.reason,
            event.source_update_id,
            event.previous_owner_id,
            event.new_owner_id,
            event.timestamp,
            json.dumps(event.metadata),
        ))
        conn.commit()


def get_stop(db_path: str | Path, stop_id: str) -> Stop | None:
    """Retrieve a stop by its ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stops WHERE stop_id = ?", (stop_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return Stop(
            stop_id=row["stop_id"],
            recipient_name=row["recipient_name"],
            address=row["address"],
            zone=row["zone"],
            delivery_window=DeliveryWindow(start=row["window_start"], end=row["window_end"]),
            dietary_note=row["dietary_note"],
            mobility_note=row["mobility_note"],
            phone=row["phone"],
            preferred_contact=row["preferred_contact"],
            current_owner_id=row["current_owner_id"],
            status=row["status"],
            contact_status=row["contact_status"],
            delivery_outcome=row["delivery_outcome"],
            contact_outcome=row["contact_outcome"],
            contact_notes=row["contact_notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


def list_stops(
    db_path: str | Path,
    owner_id: str | None = None,
    status: str | None = None,
) -> list[Stop]:
    """List stops with optional filters."""
    query = "SELECT * FROM stops WHERE 1=1"
    params: list[Any] = []
    if owner_id:
        query += " AND current_owner_id = ?"
        params.append(owner_id)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY stop_id ASC"

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            Stop(
                stop_id=row["stop_id"],
                recipient_name=row["recipient_name"],
                address=row["address"],
                zone=row["zone"],
                delivery_window=DeliveryWindow(start=row["window_start"], end=row["window_end"]),
                dietary_note=row["dietary_note"],
                mobility_note=row["mobility_note"],
                phone=row["phone"],
                preferred_contact=row["preferred_contact"],
                current_owner_id=row["current_owner_id"],
                status=row["status"],
                contact_status=row["contact_status"],
                delivery_outcome=row["delivery_outcome"],
                contact_outcome=row["contact_outcome"],
                contact_notes=row["contact_notes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]


def open_stops_by_owner(db_path: str | Path) -> dict[str, list[Stop]]:
    """Group all non-closed stops by owner (powers the dispatch board and proves Invariant 1)."""
    stops = list_stops(db_path)
    result: dict[str, list[Stop]] = {}
    for s in stops:
        if s.status != "closed":
            owner = s.current_owner_id
            if owner not in result:
                result[owner] = []
            result[owner].append(s)
    return result


def list_volunteers(db_path: str | Path) -> list[Volunteer]:
    """Retrieve all volunteers."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM volunteers ORDER BY volunteer_id ASC")
        rows = cursor.fetchall()
        return [
            Volunteer(
                volunteer_id=row["volunteer_id"],
                first_name=row["first_name"],
                phone=row["phone"],
                primary_zone=row["primary_zone"],
                active_stops_count=row["active_stops_count"],
                spare_capacity=row["spare_capacity"],
                status=row["status"],
                availability_window=DeliveryWindow(
                    start=row["availability_start"], end=row["availability_end"]
                ),
                notes=row["notes"],
            )
            for row in rows
        ]


def update_volunteer_capacity(
    db_path: str | Path,
    volunteer_id: str,
    active_stops_delta: int,
    spare_capacity_delta: int,
    status: str | None = None,
) -> None:
    """Update a volunteer's live active stops count and remaining spare capacity."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute("""
                UPDATE volunteers
                SET active_stops_count = active_stops_count + ?,
                    spare_capacity = spare_capacity + ?,
                    status = ?
                WHERE volunteer_id = ?
            """, (active_stops_delta, spare_capacity_delta, status, volunteer_id))
        else:
            cursor.execute("""
                UPDATE volunteers
                SET active_stops_count = active_stops_count + ?,
                    spare_capacity = spare_capacity + ?
                WHERE volunteer_id = ?
            """, (active_stops_delta, spare_capacity_delta, volunteer_id))
        conn.commit()


def get_events_for_stop(db_path: str | Path, stop_id: str) -> list[DispatchEvent]:
    """Retrieve the audit event trail for a specific stop."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM dispatch_events WHERE stop_id = ? ORDER BY timestamp ASC",
            (stop_id,),
        )
        rows = cursor.fetchall()
        return [
            DispatchEvent(
                event_id=row["event_id"],
                stop_id=row["stop_id"],
                from_status=row["from_status"],
                to_status=row["to_status"],
                actor=row["actor"],
                reason=row["reason"],
                source_update_id=row["source_update_id"],
                previous_owner_id=row["previous_owner_id"],
                new_owner_id=row["new_owner_id"],
                timestamp=row["timestamp"],
                metadata=json.loads(row["metadata_json"] or "{}"),
            )
            for row in rows
        ]
