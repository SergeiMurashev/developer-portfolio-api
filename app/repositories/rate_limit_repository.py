import hashlib
import math
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.config import Settings
from app.core.exceptions import RateLimitExceededError
from app.infrastructure.database import PostgresDatabase


@dataclass
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


class RateLimitRepository:
    def __init__(self, settings: Settings, database: PostgresDatabase) -> None:
        self.settings = settings
        self.database = database

    def check_and_increment(self, client_ip: str) -> RateLimitDecision:
        client_key = self._hash_client_key(client_ip)
        now = datetime.now(timezone.utc)
        window_seconds = self.settings.rate_limit_window_seconds
        window_epoch = math.floor(now.timestamp() / window_seconds) * window_seconds
        window_start = datetime.fromtimestamp(window_epoch, tz=timezone.utc)

        with self.database.connection() as conn:
            with self.database.cursor(conn) as cursor:
                cursor.execute(
                    """
                    DELETE FROM rate_limits
                    WHERE updated_at < NOW() - INTERVAL '1 day'
                    """
                )
                cursor.execute(
                    """
                    INSERT INTO rate_limits (
                        client_key,
                        window_started_at,
                        request_count,
                        updated_at
                    ) VALUES (%s, %s, 1, NOW())
                    ON CONFLICT (client_key)
                    DO UPDATE SET
                        request_count = CASE
                            WHEN rate_limits.window_started_at = EXCLUDED.window_started_at
                                THEN rate_limits.request_count + 1
                            ELSE 1
                        END,
                        window_started_at = EXCLUDED.window_started_at,
                        updated_at = NOW()
                    RETURNING request_count
                    """,
                    (client_key, window_start),
                )
                row = cursor.fetchone()
                request_count = int(row["request_count"]) if row else 1
                if request_count > self.settings.rate_limit_requests:
                    raise RateLimitExceededError(retry_after_seconds=window_seconds)

        return RateLimitDecision(allowed=True)

    def _hash_client_key(self, client_ip: str) -> str:
        raw = f"{self.settings.rate_limit_hash_secret}:{client_ip}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()
