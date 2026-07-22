from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Dict, Optional


class AIStatus(StrEnum):
    SUCCESS = "success"
    FALLBACK = "fallback"


class EmailStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


@dataclass
class ContactRecord:
    id: str
    request_id: str
    name: str
    email: str
    phone: str
    comment: str
    ai_provider: str
    ai_status: str
    category: str
    sentiment: str
    priority: str
    summary: str
    suggested_reply: str
    owner_email_status: str
    user_email_status: str
    owner_email_error: Optional[str]
    user_email_error: Optional[str]
    created_at: str

    @classmethod
    def new(
        cls,
        *,
        id: str,
        request_id: str,
        name: str,
        email: str,
        phone: str,
        comment: str,
        ai_provider: str,
        ai_status: AIStatus,
        category: str,
        sentiment: str,
        priority: str,
        summary: str,
        suggested_reply: str,
    ) -> "ContactRecord":
        ai_status_value = ai_status.value if hasattr(ai_status, "value") else str(ai_status)
        return cls(
            id=id,
            request_id=request_id,
            name=name,
            email=email,
            phone=phone,
            comment=comment,
            ai_provider=ai_provider,
            ai_status=ai_status_value,
            category=category,
            sentiment=sentiment,
            priority=priority,
            summary=summary,
            suggested_reply=suggested_reply,
            owner_email_status=EmailStatus.PENDING.value,
            user_email_status=EmailStatus.PENDING.value,
            owner_email_error=None,
            user_email_error=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
