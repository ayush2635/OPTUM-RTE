import re
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum
from app.schemas.member import MemberOut


class EligibilityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    NOT_FOUND = "NOT_FOUND"
    ERROR = "ERROR"


class ScrubStatus(str, Enum):
    APPROVED = "APPROVED"
    WARNING = "WARNING"
    DENIED = "DENIED"


class ScrubResult(BaseModel):
    model_config = ConfigDict(strict=True)
    cpt_code: str
    result: ScrubStatus
    message: str
    ncci_conflict_with: Optional[str] = None


class CoverageOut(BaseModel):
    model_config = ConfigDict(strict=True)
    plan_name: str
    effective_date: date
    termination_date: Optional[date] = None
    copay_amount: Decimal
    deductible_remaining: Decimal
    out_of_pocket_max: Decimal


class EligibilityRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    transaction_id: str
    member_id: str
    provider_npi: str
    date_of_birth: date = Field(default_factory=lambda: date.today())
    date_of_service: date = Field(default_factory=lambda: date.today())
    proposed_cpt_codes: List[str] = Field(default_factory=list)
    diagnosis_codes: List[str] = Field(default_factory=list)

    @field_validator("date_of_birth", "date_of_service", mode="before")
    @classmethod
    def parse_dates(cls, v):
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y-%m-%d").date()
            except ValueError:
                pass
        return v

    @field_validator("provider_npi")
    @classmethod
    def validate_npi(cls, v: str) -> str:
        if v and not re.match(r"^\d{10}$", v):
            raise ValueError("NPI must be exactly 10 digits")
        return v

    @field_validator("proposed_cpt_codes")
    @classmethod
    def validate_cpt_codes(cls, v: List[str]) -> List[str]:
        if len(v) > 10:
            raise ValueError("Maximum 10 CPT codes allowed")
        for code in v:
            if not re.match(r"^[A-Z0-9]{5}$", code):
                raise ValueError(f"Invalid CPT code format: {code}")
        return v


class EligibilityResponse(BaseModel):
    model_config = ConfigDict(strict=True)
    transaction_id: str
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: EligibilityStatus
    message: Optional[str] = None
    member_details: Optional[MemberOut] = None
    coverage_details: Optional[CoverageOut] = None
    scrubbing_results: List[ScrubResult] = Field(default_factory=list)
