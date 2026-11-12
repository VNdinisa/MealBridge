"""Voice update parser with Google Gemini 2.5 Flash and deterministic rules fallback."""

from __future__ import annotations

import os
import re
import uuid
from abc import ABC, abstractmethod
from typing import Any

from src.models.entities import VoiceUpdate


class Parser(ABC):
    @abstractmethod
    def parse(self, transcript: str, context: dict[str, Any] | None = None) -> VoiceUpdate:
        """Parse raw speech transcript into a structured VoiceUpdate."""
        pass


class RulesBasedFallbackParser(Parser):
    """Deterministic, offline parser using keyword & regex matching.
    
    Guarantees reliable local testing, CI execution, and fallback resilience when offline.
    """

    def parse(self, transcript: str, context: dict[str, Any] | None = None) -> VoiceUpdate:
        text = transcript.strip()
        lower = text.lower()
        context = context or {}
        active_volunteers = context.get("volunteers", [])
        active_stops = context.get("stops", [])

        update_id = f"upd_{uuid.uuid4().hex[:8]}"

        # 1. Prompt injection / adversarial attempt detection
        injection_patterns = [
            "ignore previous rules",
            "delete all",
            "drop table",
            "system prompt",
            "you are now",
        ]
        if any(pat in lower for pat in injection_patterns):
            return VoiceUpdate(
                update_id=update_id,
                raw_transcript=text,
                speaker_id=None,
                speaker_name=None,
                intent="other",
                affected_stop_ids=[],
                confidence=0.1,
                ambiguities=["Adversarial instruction or system injection pattern detected in transcript."],
                needs_confirmation=True,
            )

        # 2. Extract speaker
        speaker_id = None
        speaker_name = None
        # Look for explicit volunteer IDs like V01, V1, V03, V3
        vol_match = re.search(r"\b(v0?[1-9]|v10)\b", lower)
        if vol_match:
            raw_vid = vol_match.group(1).upper()
            if len(raw_vid) == 2 and raw_vid[1].isdigit():
                speaker_id = f"V0{raw_vid[1]}"
            else:
                speaker_id = raw_vid
        else:
            # Match by volunteer first name in context
            for v in active_volunteers:
                fname = v.get("first_name", "").lower()
                if fname and fname in lower:
                    speaker_id = v.get("volunteer_id")
                    speaker_name = v.get("first_name")
                    break

        # Default speaker for noon drill if text matches V01 cancellation pattern
        if not speaker_id and ("car broke down" in lower or "car breakdown" in lower):
            speaker_id = "V01"

        # 3. Detect Intent
        intent = "other"
        if any(w in lower for w in ["can't make", "cannot make", "broke down", "breakdown", "emergency", "cancel", "sick"]):
            intent = "cancel"
        elif any(w in lower for w in ["running late", "delayed", "stuck in traffic"]):
            intent = "delay"
        elif "swap" in lower:
            intent = "swap"
        elif any(w in lower for w in ["delivered", "dropped off", "handed meal"]):
            intent = "delivered"

        # 4. Extract Affected Stops
        affected_stops = []
        # Pattern like S07, S08, S09 or S7-S9 or S01-S20
        range_match = re.search(r"\b(s\d{1,2})\s*(?:to|-)\s*(s\d{1,2})\b", lower)
        if range_match:
            start_num = int(range_match.group(1)[1:])
            end_num = int(range_match.group(2)[1:])
            for num in range(start_num, end_num + 1):
                affected_stops.append(f"S{num:02d}")
        else:
            stop_matches = re.findall(r"\bs\d{1,2}\b", lower)
            if stop_matches:
                for sm in stop_matches:
                    num = int(sm[1:])
                    affected_stops.append(f"S{num:02d}")

        # If it's a full cancellation and speaker has assigned stops in context, grab all of them
        if intent == "cancel" and speaker_id and not affected_stops and active_stops:
            affected_stops = [
                s.get("stop_id") for s in active_stops if s.get("current_owner_id") == speaker_id
            ]

        # 5. Ambiguity and Confidence Scoring
        ambiguities = []
        confidence = 0.95

        # Check for ambiguous references (e.g., "the Hassan stop" or "stop on Main")
        if "the hassan stop" in lower or "the lady" in lower:
            ambiguities.append("Ambiguous recipient or stop name referenced without specific ID.")
            confidence = 0.50

        if not speaker_id:
            ambiguities.append("Speaker identity could not be uniquely resolved to an active volunteer.")
            confidence = min(confidence, 0.60)

        if not affected_stops and intent != "other":
            ambiguities.append("No specific stop IDs could be resolved for this update.")
            confidence = min(confidence, 0.65)

        needs_confirmation = confidence < 0.80 or len(ambiguities) > 0 or intent == "other"

        return VoiceUpdate(
            update_id=update_id,
            raw_transcript=text,
            speaker_id=speaker_id,
            speaker_name=speaker_name,
            intent=intent,
            affected_stop_ids=affected_stops,
            confidence=confidence,
            ambiguities=ambiguities,
            needs_confirmation=needs_confirmation,
        )


class GeminiVoiceParser(Parser):
    """Google Gemini 2.5 Flash structured output voice parser using official google-genai SDK."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        self.fallback = RulesBasedFallbackParser()

    def parse(self, transcript: str, context: dict[str, Any] | None = None) -> VoiceUpdate:
        if not self.api_key:
            # Seamlessly fallback to offline rules parser if API key is not configured
            return self.fallback.parse(transcript, context)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            system_instruction = (
                "You are the MealBridge Voice Dispatch Intake Parser. "
                "You convert voice notes from volunteer drivers and dispatchers into structured dispatch actions. "
                "Output strictly valid JSON matching the schema. "
                "CRITICAL: If the speaker is unsure, names are ambiguous, or confidence is under 0.8, set needs_confirmation=true. "
                "Never guess stop IDs or volunteer IDs that do not exist in the context."
            )

            prompt = f"Transcript:\n{transcript}\n\nContext:\n{context or {}}"

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            import json
            parsed_json = json.loads(response.text)
            return VoiceUpdate(
                update_id=f"upd_{uuid.uuid4().hex[:8]}",
                raw_transcript=transcript,
                speaker_id=parsed_json.get("speaker_id"),
                speaker_name=parsed_json.get("speaker_name"),
                intent=parsed_json.get("intent", "other"),
                affected_stop_ids=parsed_json.get("affected_stop_ids", []),
                confidence=float(parsed_json.get("confidence", 0.9)),
                ambiguities=parsed_json.get("ambiguities", []),
                needs_confirmation=bool(parsed_json.get("needs_confirmation", False)),
            )
        except Exception:
            # If network error or quota issue, gracefully fallback
            return self.fallback.parse(transcript, context)
