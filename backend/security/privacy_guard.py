import re
from pydantic import BaseModel, field_validator

# Enforce synthetic/pretend data rules (e.g., 555 test numbers or "Pretend" prefix)
REAL_PHONE_PATTERN = re.compile(r"^(?!.*555)\+?\d[\d\s\-]{7,14}$")

class DeliveryStopPayload(BaseModel):
    stop_id: str
    neighbor_alias: str
    pretend_address: str
    pretend_phone: str
    is_pretend_data: bool = True

    @field_validator("is_pretend_data")
    @classmethod
    def must_be_pretend(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Privacy Policy Violation: Only pretend datasets are permitted.")
        return v

    @field_validator("pretend_phone")
    @classmethod
    def reject_real_phone(cls, v: str) -> str:
        if REAL_PHONE_PATTERN.match(v.strip()):
            raise ValueError("PII Guardrail: Use synthetic 555 test phone numbers only.")
        return v
