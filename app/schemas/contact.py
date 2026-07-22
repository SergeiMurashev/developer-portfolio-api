import re
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.ai import AIAnalysis


PHONE_PATTERN = re.compile(r"^[+()0-9\s\-]{7,32}$")


class ContactCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=32)
    email: EmailStr
    comment: str = Field(min_length=5, max_length=2000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name is required")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_PATTERN.match(value):
            raise ValueError("phone must contain only digits, spaces, parentheses, + and -")
        return value

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("comment is required")
        return value


class EmailDeliveryResult(BaseModel):
    status: Literal["pending", "sent", "failed"]
    error: Optional[str] = None


class WarningItem(BaseModel):
    code: str
    message: str


class ContactCreateResponse(BaseModel):
    request_id: str
    contact_id: str
    ai: AIAnalysis
    owner_email: EmailDeliveryResult
    user_email: EmailDeliveryResult
    notification_status: Literal["sent", "partial_failed"]
    warnings: List[WarningItem] = Field(default_factory=list)
