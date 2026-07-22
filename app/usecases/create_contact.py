import logging
import uuid
from dataclasses import dataclass
from typing import Optional

from app.models.contact import ContactRecord
from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.schemas.contact import ContactCreateRequest, ContactCreateResponse, EmailDeliveryResult, WarningItem
from app.services.ai_service import AIService
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


@dataclass
class CreateContactResult:
    response: ContactCreateResponse


class CreateContactUseCase:
    def __init__(
        self,
        *,
        rate_limit_repository: RateLimitRepository,
        contact_repository: ContactRepository,
        metrics_repository: MetricsRepository,
        ai_service: AIService,
        email_service: EmailService,
    ) -> None:
        self.rate_limit_repository = rate_limit_repository
        self.contact_repository = contact_repository
        self.metrics_repository = metrics_repository
        self.ai_service = ai_service
        self.email_service = email_service

    async def execute(self, *, payload: ContactCreateRequest, client_ip: str, request_id: str) -> CreateContactResult:
        self.rate_limit_repository.check_and_increment(client_ip)

        analysis = await self.ai_service.analyze(
            name=payload.name,
            email=str(payload.email),
            comment=payload.comment,
        )

        contact_id = str(uuid.uuid4())
        record = ContactRecord.new(
            id=contact_id,
            request_id=request_id,
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            comment=payload.comment,
            ai_provider=analysis.provider,
            ai_status=analysis.status,
            category=analysis.category,
            sentiment=analysis.sentiment,
            priority=analysis.priority,
            summary=analysis.summary,
            suggested_reply=analysis.suggested_reply,
        )

        self.contact_repository.create(record.to_dict())

        delivery = await self.email_service.send_contact_notifications(contact=record, analysis=analysis)

        self.contact_repository.update_delivery_statuses(
            contact_id,
            owner_status=delivery.owner_status,
            user_status=delivery.user_status,
            owner_error=delivery.owner_error,
            user_error=delivery.user_error,
        )

        # Metrics are recomputed from the source of truth, so the API always reports current totals.
        snapshot = self.metrics_repository.get()

        warnings = []
        if delivery.owner_status == "failed":
            warnings.append(
                WarningItem(
                    code="owner_email_failed",
                    message="Обращение сохранено, но письмо владельцу не доставлено",
                )
            )
        if delivery.user_status == "failed":
            warnings.append(
                WarningItem(
                    code="user_email_failed",
                    message="Обращение сохранено, но копия письма пользователю не доставлена",
                )
            )

        response = ContactCreateResponse(
            request_id=request_id,
            contact_id=contact_id,
            ai={
                "provider": analysis.provider,
                "status": analysis.status,
                "category": analysis.category,
                "sentiment": analysis.sentiment,
                "priority": analysis.priority,
                "summary": analysis.summary,
                "suggested_reply": analysis.suggested_reply,
                "fallback_reason": analysis.fallback_reason,
            },
            owner_email=EmailDeliveryResult(status=delivery.owner_status, error=delivery.owner_error),
            user_email=EmailDeliveryResult(status=delivery.user_status, error=delivery.user_error),
            notification_status="sent" if not warnings else "partial_failed",
            warnings=warnings,
        )
        logger.info("contact created: request_id=%s contact_id=%s metrics=%s", request_id, contact_id, snapshot)
        return CreateContactResult(response=response)
