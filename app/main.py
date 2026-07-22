import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.handlers.contact import router as contact_router
from app.api.handlers.health import router as health_router
from app.api.handlers.metrics import router as metrics_router
from app.core.config import get_settings
from app.core.exception_handlers import (
    app_error_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware

settings = get_settings()
configure_logging(settings.log_dir)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Бэкенд-сервис для формы обратной связи в портфолио разработчика с резервным механизмом на базе ИИ и хранением данных в PostgreSQL.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_list(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware, log_file=settings.data_dir / "request_logs.jsonl")

app.include_router(contact_router)
app.include_router(health_router)
app.include_router(metrics_router)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": settings.app_name,
            "status": "ok",
            "docs": "/docs",
        }
    )
