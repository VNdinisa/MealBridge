import re
from pydantic import BaseModel, Field, field_validator

# PII detection patterns (preserve synthetic 555 numbers used in pretend datasets)
NON_555_PHONE_RE = re.compile(r"\b(?!555[\s\-]?\d{4})(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ID_NUMBER_RE = re.compile(r"\b(?:\d{3}-\d{2}-\d{4}|\d{13})\b")  # SSN or 13-digit ID numbers
STREET_ADDRESS_RE = re.compile(
    r"\b\d{1,5}\s+(?!Pretend\b)[A-Za-z0-9\s]{2,30}\b(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)\b",
    re.IGNORECASE,
)

# Basic prompt-injection guardrails before sending transcripts to LLMs (NVIDIA / Gemini)
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"reveal\s+(?:all\s+)?(?:neighbor|database|secret|api\s*key)", re.IGNORECASE),
]


class VoiceTranscriptRequest(BaseModel):
    stop_id: str = Field(..., min_length=3, max_length=32, pattern=r"^[A-Za-z0-9\-_]+$")
    raw_transcript: str = Field(..., min_length=2, max_length=2000)
    is_pretend_data: bool = True

    @field_validator("is_pretend_data")
    @classmethod
    def enforce_pretend_flag(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Privacy Policy Violation: Voice transcripts must use pretend datasets.")
        return v

    @field_validator("raw_transcript")
    @classmethod
    def sanitize_control_and_injection(cls, v: str) -> str:
        # Remove null bytes and non-printable control characters
        cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", v).strip()
        if not cleaned:
            raise ValueError("Transcript cannot be empty after control-character stripping.")

        for pattern in INJECTION_PATTERNS:
            if pattern.search(cleaned):
                raise ValueError("Security Guardrail: Potential prompt-injection phrase detected.")
        return cleaned


def scrub_transcript_pii(transcript: str) -> tuple[str, list[str]]:
    """
    Redacts real-looking PII while preserving synthetic 'Pretend' / '555' test tokens.
    Returns (scrubbed_text, list_of_redacted_categories).
    """
    redactions: list[str] = []
    scrubbed = transcript

    rules = [
        ("EMAIL", EMAIL_RE, "[REDACTED_EMAIL]"),
        ("ID_NUMBER", ID_NUMBER_RE, "[REDACTED_ID]"),
        ("PHONE", NON_555_PHONE_RE, "[REDACTED_PHONE]"),
        ("ADDRESS", STREET_ADDRESS_RE, "[REDACTED_ADDRESS]"),
    ]

    for label, pattern, placeholder in rules:
        scrubbed, count = pattern.subn(placeholder, scrubbed)
        if count > 0:
            redactions.append(f"{label}:{count}")

    return scrubbed, redactions
