from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import Settings


class PostgresDatabase:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @contextmanager
    def connection(self) -> Iterator[psycopg2.extensions.connection]:
        conn = psycopg2.connect(
            self.settings.database_url,
            connect_timeout=self.settings.database_connect_timeout_seconds,
        )
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ping(self) -> None:
        with self.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

    def cursor(self, conn: psycopg2.extensions.connection):
        return conn.cursor(cursor_factory=RealDictCursor)

