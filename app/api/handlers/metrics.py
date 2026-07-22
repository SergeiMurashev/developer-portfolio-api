from fastapi import APIRouter, Depends

from app.api.dependencies import get_metrics_repository
from app.repositories.metrics_repository import MetricsRepository
from app.schemas.metrics import MetricsResponse

router = APIRouter(prefix="/api", tags=["metrics"])


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Получить статистику обращений.",
    description="Возвращает агрегированную статистику по контактам, AI-статусу и категориям запросов.",
)
async def metrics(repository: MetricsRepository = Depends(get_metrics_repository)) -> MetricsResponse:
    return MetricsResponse(**repository.get())
