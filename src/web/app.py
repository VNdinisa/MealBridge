"""FastAPI Dispatcher Web Dashboard for MealBridge."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from src.comms.contact_scripts import (
    format_closure_note,
    generate_senior_contact_script,
)
from src.dispatch.reassign import generate_reassignment_proposal
from src.intake.parser import GeminiVoiceParser, RulesBasedFallbackParser
from src.intake.transcriber import SidecarTranscriber
from src.lifecycle.database import (
    get_events_for_stop,
    get_stop,
    init_db,
    list_stops,
    list_volunteers,
    load_seed_data,
    open_stops_by_owner,
    save_event,
    save_stop,
    update_volunteer_capacity,
)
from src.lifecycle.state_machine import transition_stop
from scripts.check_data import audit_seed_data

app = FastAPI(title="MealBridge Dispatcher Hub", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent

# Resolve template directory across standard and serverless deployment layouts
possible_template_dirs = [
    BASE_DIR / "templates",
    ROOT_DIR / "src" / "web" / "templates",
    Path("src/web/templates"),
    Path("/var/task/src/web/templates"),
]
TEMPLATES_DIR = next((d for d in possible_template_dirs if d.exists()), BASE_DIR / "templates")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Serverless (Vercel) vs Local / Cloud Run filesystem handling
IS_SERVERLESS = bool(
    os.getenv("VERCEL")
    or os.getenv("VERCEL_ENV")
    or os.getenv("AWS_LAMBDA_FUNCTION_NAME")
    or os.getenv("LAMBDA_TASK_ROOT")
    or not os.access(str(ROOT_DIR), os.W_OK)
)

if IS_SERVERLESS:
    DB_PATH = Path(tempfile.gettempdir()) / "mealbridge.db"
    UPLOAD_DIR = Path(tempfile.gettempdir()) / "uploads"
else:
    DB_PATH = ROOT_DIR / "mealbridge.db"
    UPLOAD_DIR = ROOT_DIR / "data" / "uploads"

try:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass

# Resolve seed files path reliably
SEED_VOLUNTEERS = ROOT_DIR / "data" / "seed" / "volunteers.json"
SEED_STOPS = ROOT_DIR / "data" / "seed" / "stops.json"


def ensure_db():
    try:
        if not DB_PATH.exists():
            init_db(DB_PATH)
            load_seed_data(DB_PATH, SEED_VOLUNTEERS, SEED_STOPS)
    except Exception as e:
        print(f"Warning during DB ensure: {e}")


ensure_db()

# Global in-memory cache for pending proposals
PENDING_PROPOSALS: dict[str, Any] = {}
LAST_PARSE: dict[str, Any] = {}


@app.get("/api/health")
async def health():
    """Lightweight server health probe."""
    return JSONResponse({
        "status": "healthy",
        "service": "MealBridge",
        "serverless": IS_SERVERLESS,
        "db_path": str(DB_PATH),
    })


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    ensure_db()
    stops_by_owner = open_stops_by_owner(DB_PATH)
    volunteers = list_volunteers(DB_PATH)
    all_stops = list_stops(DB_PATH)
    total_stops = len(all_stops)
    at_risk_count = sum(1 for s in all_stops if s.status == "at_risk")
    escalated_count = sum(1 for s in all_stops if s.status == "needs_escalation")
    closed_count = sum(1 for s in all_stops if s.status == "closed")

    ctx = {
        "stops_by_owner": stops_by_owner,
        "volunteers": volunteers,
        "total_stops": total_stops,
        "at_risk_count": at_risk_count,
        "escalated_count": escalated_count,
        "closed_count": closed_count,
        "last_parse": LAST_PARSE,
        "pending_proposals": list(PENDING_PROPOSALS.values()),
    }

    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context=ctx,
        )
    except Exception:
        # Resilient fallback if Jinja directory loader failed in serverless bundle
        for candidate in [
            TEMPLATES_DIR / "index.html",
            BASE_DIR / "templates" / "index.html",
            ROOT_DIR / "src" / "web" / "templates" / "index.html",
            Path("src/web/templates/index.html"),
        ]:
            if candidate.exists():
                from jinja2 import Template
                tmpl = Template(candidate.read_text(encoding="utf-8"))
                return HTMLResponse(tmpl.render(request=request, **ctx))
        raise


@app.post("/api/reset")
async def reset_db():
    """Reset the database to initial clean seed data."""
    global PENDING_PROPOSALS, LAST_PARSE
    PENDING_PROPOSALS.clear()
    LAST_PARSE.clear()
    init_db(DB_PATH)
    load_seed_data(DB_PATH, SEED_VOLUNTEERS, SEED_STOPS)
    return JSONResponse({"status": "reset_successful", "message": "Database reset to initial state."})


@app.post("/api/voice-intake")
async def voice_intake(
    transcript: str = Form(None),
    audio_file: UploadFile = File(None),
    use_gemini: bool = Form(False),
):
    """Process uploaded audio or transcribed voice note."""
    global LAST_PARSE, PENDING_PROPOSALS
    PENDING_PROPOSALS.clear()

    raw_text = transcript
    if audio_file and audio_file.filename:
        dest = UPLOAD_DIR / audio_file.filename
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        try:
            transcriber = SidecarTranscriber()
            raw_text = transcriber.transcribe(dest)
        except Exception:
            raw_text = f"Voice note uploaded: {audio_file.filename}"

    if not raw_text:
        raw_text = "Hi dispatch, this is Marcus V01. I can't make my stops today, my car broke down on 4th street."

    # Parse using Gemini or fallback
    volunteers = list_volunteers(DB_PATH)
    stops = list_stops(DB_PATH)
    context = {
        "volunteers": [v.model_dump() for v in volunteers],
        "stops": [s.model_dump() for s in stops],
    }

    if use_gemini and os.getenv("GEMINI_API_KEY"):
        parser = GeminiVoiceParser()
    else:
        parser = RulesBasedFallbackParser()

    update = parser.parse(raw_text, context)
    LAST_PARSE = update.model_dump()

    # If parse is low confidence or ambiguous, do not mutate silently (Invariant 4)
    if update.needs_confirmation:
        return JSONResponse({
            "status": "needs_confirmation",
            "message": "Parse has ambiguities or low confidence. Routed to Confirmation Queue.",
            "update": LAST_PARSE,
            "proposals": [],
        })

    # Transition affected stops to at_risk
    affected_stops = [s for s in stops if s.current_owner_id == update.speaker_id]
    for s in affected_stops:
        updated, ev = transition_stop(
            stop=s,
            to_status="at_risk",
            actor="voice_intake",
            reason=f"Volunteer {update.speaker_id} reported '{update.intent}'",
            source_update_id=update.update_id,
        )
        save_stop(DB_PATH, updated)
        save_event(DB_PATH, ev)

    # Generate reassignment proposals
    remaining_vols = {v.volunteer_id: v for v in volunteers}
    proposals = []
    for s in affected_stops:
        prop = generate_reassignment_proposal(
            stop=s,
            available_volunteers=list(remaining_vols.values()),
            cancelling_volunteer_id=update.speaker_id,
        )
        proposals.append(prop)
        PENDING_PROPOSALS[prop.stop_id] = prop
        if prop.proposed_owner_id != "dispatcher":
            cand = remaining_vols[prop.proposed_owner_id]
            cand.spare_capacity -= 1
            cand.active_stops_count += 1

    return JSONResponse({
        "status": "success",
        "update": LAST_PARSE,
        "proposals_count": len(proposals),
        "proposals": [p.model_dump() for p in proposals],
    })


@app.post("/api/approve-all")
async def approve_all_proposals():
    """1-Click Dispatcher Approval for all pending proposals."""
    global PENDING_PROPOSALS
    if not PENDING_PROPOSALS:
        return JSONResponse({"status": "no_proposals", "message": "No pending proposals to approve."})

    approved_count = 0
    escalated_count = 0
    generated_scripts = {}

    for stop_id, prop in list(PENDING_PROPOSALS.items()):
        stop = get_stop(DB_PATH, stop_id)
        if not stop:
            continue

        if prop.proposed_owner_id == "dispatcher":
            target_status = "needs_escalation"
            escalated_count += 1
        else:
            target_status = "reassigned"
            approved_count += 1
            update_volunteer_capacity(DB_PATH, prop.proposed_owner_id, active_stops_delta=1, spare_capacity_delta=-1)

        reassigned_stop, ev = transition_stop(
            stop=stop,
            to_status=target_status,
            actor="dispatcher",
            reason=f"Dispatcher approved proposal: {prop.reason}",
            new_owner_id=prop.proposed_owner_id,
            source_update_id=LAST_PARSE.get("update_id"),
        )
        save_stop(DB_PATH, reassigned_stop)
        save_event(DB_PATH, ev)

        # Generate older-adult contact script
        scripts = generate_senior_contact_script(reassigned_stop, new_volunteer_name=prop.candidate_name)
        generated_scripts[stop_id] = scripts

    PENDING_PROPOSALS.clear()
    return JSONResponse({
        "status": "success",
        "reassigned_count": approved_count,
        "escalated_count": escalated_count,
        "scripts": generated_scripts,
    })


@app.post("/api/simulate-delivery/{stop_id}")
async def simulate_delivery(stop_id: str):
    """Simulate delivery + welfare check outcome and close the stop."""
    stop = get_stop(DB_PATH, stop_id)
    if not stop:
        return JSONResponse({"error": "Stop not found"}, status_code=404)

    # 1. Out for delivery
    s_out, ev1 = transition_stop(stop, "out_for_delivery", actor=stop.current_owner_id, reason="Volunteer en route")
    save_stop(DB_PATH, s_out)
    save_event(DB_PATH, ev1)

    # 2. Delivered
    s_del, ev2 = transition_stop(
        s_out,
        "delivered",
        actor=stop.current_owner_id,
        reason="Meal handed to senior",
        delivery_outcome="Handed directly to recipient, warm container verified",
    )
    save_stop(DB_PATH, s_del)
    save_event(DB_PATH, ev2)

    # 3. Close with dual outcomes
    closure_note = format_closure_note(
        stop_id=stop_id,
        volunteer_id=stop.current_owner_id,
        delivery_time="1:30 PM",
        contact_method="phone",
        contact_time="1:40 PM",
        notes="Senior confirmed meal received and in great spirits.",
    )
    s_closed, ev3 = transition_stop(
        s_del,
        "closed",
        actor="dispatcher",
        reason="Delivery and phone welfare check confirmed",
        contact_outcome="Phone contact verified by volunteer",
        contact_status="reached",
        metadata={"closure_note": closure_note},
    )
    save_stop(DB_PATH, s_closed)
    save_event(DB_PATH, ev3)

    return JSONResponse({
        "status": "closed",
        "stop_id": stop_id,
        "closure_note": closure_note,
    })


@app.get("/api/audit")
async def run_audit():
    """Run data quality auditor live."""
    report = audit_seed_data(SEED_VOLUNTEERS, SEED_STOPS)
    return JSONResponse(report)
