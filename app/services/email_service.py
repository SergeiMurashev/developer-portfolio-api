import asyncio
from dataclasses import dataclass
from typing import Optional

from app.core.config import Settings
from app.infrastructure.smtp_client import SMTPClient
from app.models.contact import ContactRecord, EmailStatus
from app.services.ai_service import AIAnalysisResult


@dataclass
class EmailDeliveryOutcome:
    owner_status: str
    user_status: str
    owner_error: Optional[str] = None
    user_error: Optional[str] = None


class EmailService:
    def __init__(self, settings: Settings, client: SMTPClient) -> None:
        self.settings = settings
        self.client = client

    async def send_contact_notifications(self, *, contact: ContactRecord, analysis: AIAnalysisResult) -> EmailDeliveryOutcome:
        owner_subject = f"Новое обращение: {contact.name}"
        owner_body = self._build_owner_message(contact=contact, analysis=analysis)
        user_subject = "Мы получили ваше обращение"
        user_body = self._build_user_message(contact=contact, analysis=analysis)

        owner_status, owner_error = await self._send_message(self.settings.owner_email, owner_subject, owner_body)
        user_status, user_error = await self._send_message(contact.email, user_subject, user_body)

        return EmailDeliveryOutcome(
            owner_status=owner_status,
            user_status=user_status,
            owner_error=owner_error,
            user_error=user_error,
        )

    async def _send_message(self, to_email: str, subject: str, body: str) -> tuple[str, Optional[str]]:
        try:
            await asyncio.to_thread(self.client.send, to_email=to_email, subject=subject, body=body)
            return EmailStatus.SENT.value, None
        except Exception as exc:
            return EmailStatus.FAILED.value, str(exc)

    def _build_owner_message(self, *, contact: ContactRecord, analysis: AIAnalysisResult) -> str:
        return (
            f"Имя: {contact.name}\n"
            f"Email: {contact.email}\n"
            f"Телефон: {contact.phone}\n"
            f"Комментарий: {contact.comment}\n\n"
            f"AI category: {analysis.category}\n"
            f"AI sentiment: {analysis.sentiment}\n"
            f"AI priority: {analysis.priority}\n"
            f"AI summary: {analysis.summary}\n"
            f"Suggested reply: {analysis.suggested_reply}\n"
        )

    def _build_user_message(self, *, contact: ContactRecord, analysis: AIAnalysisResult) -> str:
        return (
            f"Здравствуйте, {contact.name}.\n\n"
            "Спасибо за ваше обращение. Мы получили ваш комментарий и скоро ответим.\n\n"
            f"Кратко по AI: {analysis.summary}\n"
        )

