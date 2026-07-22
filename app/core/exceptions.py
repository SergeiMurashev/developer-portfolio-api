class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 500) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class RateLimitExceededError(AppError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(
            code="rate_limit_exceeded",
            message="Слишком много запросов. Попробуйте позже.",
            status_code=429,
        )
        self.retry_after_seconds = retry_after_seconds

