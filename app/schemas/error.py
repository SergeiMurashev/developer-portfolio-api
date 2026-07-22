from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: Optional[str] = None
    details: Any | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail

