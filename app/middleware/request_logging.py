import json
import logging
import time
import uuid
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, log_file: Path) -> None:
        super().__init__(app)
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        started = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = int((time.perf_counter() - started) * 1000)
            client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
            if client_ip and "," in client_ip:
                client_ip = client_ip.split(",", 1)[0].strip()
            record = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": locals().get("status_code", 500),
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "query": str(request.url.query) if request.url.query else "",
            }
            with self.log_file.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.info("request=%s", record)
