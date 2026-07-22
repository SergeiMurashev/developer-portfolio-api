import logging
from typing import Any, Dict

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError, RateLimitExceededError

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    payload: Dict[str, Any] = {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "request_id": getattr(request.state, "request_id", None),
        }
    }
    headers = {}
    if isinstance(exc, RateLimitExceededError):
        headers["Retry-After"] = str(exc.retry_after_seconds)
    return JSONResponse(status_code=exc.status_code, content=payload, headers=headers)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    payload = {
        "error": {
            "code": "validation_error",
            "message": "Некорректные данные запроса.",
            "request_id": getattr(request.state, "request_id", None),
            "details": exc.errors(),
        }
    }
    return JSONResponse(status_code=422, content=payload)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    payload = {
        "error": {
            "code": "internal_server_error",
            "message": "Внутренняя ошибка сервиса.",
            "request_id": getattr(request.state, "request_id", None),
        }
    }
    return JSONResponse(status_code=500, content=payload)

