import logging

from fastapi import APIRouter, Depends, Request, status

from app.api.dependencies import get_create_contact_usecase
from app.schemas.error import ErrorResponse
from app.schemas.contact import ContactCreateRequest, ContactCreateResponse
from app.usecases.create_contact import CreateContactUseCase

router = APIRouter(prefix="/api", tags=["contact"])
logger = logging.getLogger(__name__)


@router.post(
    "/contact",
    response_model=ContactCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Сохранить обращение и отправить уведомления.",
    description=(
        "Принимает форму обратной связи, валидирует данные, проверяет rate limit, "
        "выполняет AI-анализ комментария, сохраняет контакт в PostgreSQL и отправляет email "
        "владельцу и пользователю."
    ),
    responses={
        422: {"model": ErrorResponse, "description": "Некорректные данные запроса"},
        429: {"model": ErrorResponse, "description": "Превышен лимит запросов"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервиса"},
    },
)
async def create_contact(
    payload: ContactCreateRequest,
    request: Request,
    usecase: CreateContactUseCase = Depends(get_create_contact_usecase),
) -> ContactCreateResponse:
    request_id = getattr(request.state, "request_id", "")
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    result = await usecase.execute(payload=payload, client_ip=client_ip, request_id=request_id)
    return result.response
