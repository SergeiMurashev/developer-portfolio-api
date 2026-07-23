import logging

from fastapi import APIRouter, Depends

from app.api.dependencies import get_metrics_repository
from app.core.exceptions import DatabaseUnavailableError
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/api", tags=["metrics"])
logger = logging.getLogger(__name__)


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Получить статистику обращений.",
    description="Возвращает агрегированную статистику по контактам, AI-статусу и категориям запросов.",
)
async def metrics(repository: MetricsRepository = Depends(get_metrics_repository)) -> MetricsResponse:
    try:
        return MetricsResponse(**repository.get())
    except Exception as exc:
        logger.exception("metrics retrieval failed: %s", exc)
        raise DatabaseUnavailableError() from exc
