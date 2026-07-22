from functools import lru_cache

from app.core.config import Settings, get_settings
from app.infrastructure.database import PostgresDatabase
from app.infrastructure.openai_client import OpenAIClient
from app.infrastructure.smtp_client import SMTPClient
from app.repositories.contact_repository import ContactRepository
from app.repositories.metrics_repository import MetricsRepository
from app.repositories.rate_limit_repository import RateLimitRepository
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.usecases.create_contact import CreateContactUseCase


@lru_cache(maxsize=1)
def get_app_container() -> dict:
    settings = get_settings()
    database = PostgresDatabase(settings)

    contact_repository = ContactRepository(database)
    rate_limit_repository = RateLimitRepository(settings, database)
    metrics_repository = MetricsRepository(database)
    ai_service = AIService(OpenAIClient(settings))
    email_service = EmailService(settings, SMTPClient(settings))
    create_contact_usecase = CreateContactUseCase(
        rate_limit_repository=rate_limit_repository,
        contact_repository=contact_repository,
        metrics_repository=metrics_repository,
        ai_service=ai_service,
        email_service=email_service,
    )

    return {
        "settings": settings,
        "database": database,
        "contact_repository": contact_repository,
        "rate_limit_repository": rate_limit_repository,
        "metrics_repository": metrics_repository,
        "ai_service": ai_service,
        "email_service": email_service,
        "create_contact_usecase": create_contact_usecase,
    }


def get_settings_dependency() -> Settings:
    return get_app_container()["settings"]


def get_database() -> PostgresDatabase:
    return get_app_container()["database"]


def get_create_contact_usecase() -> CreateContactUseCase:
    return get_app_container()["create_contact_usecase"]


def get_metrics_repository() -> MetricsRepository:
    return get_app_container()["metrics_repository"]
