from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class RateLimitState:
    client_key: str
    window_started_at: str
    request_count: int

    @classmethod
    def new(cls, client_key: str) -> "RateLimitState":
        return cls(
            client_key=client_key,
            window_started_at=datetime.now(timezone.utc).isoformat(),
            request_count=1,
        )

