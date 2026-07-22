from fastapi import APIRouter, Depends

from app.api.dependencies import get_database, get_settings_dependency
from app.core.config import Settings
from app.infrastructure.database import PostgresDatabase
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Проверить статус сервиса и базы данных.",
    description="Возвращает состояние приложения и доступность PostgreSQL для smoke-check.",
)
async def health(
    settings: Settings = Depends(get_settings_dependency),
    database: PostgresDatabase = Depends(get_database),
) -> HealthResponse:
    db_status = "ok"
    overall_status = "ok"
    try:
        database.ping()
    except Exception:
        db_status = "down"
        overall_status = "degraded"

    return HealthResponse(status=overall_status, service=settings.app_name, env=settings.app_env, database=db_status)
