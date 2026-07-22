from typing import Any, Dict, Optional

from app.infrastructure.database import PostgresDatabase


class ContactRepository:
    def __init__(self, database: PostgresDatabase) -> None:
        self.database = database

    def create(self, record: Dict[str, Any]) -> Dict[str, Any]:
        with self.database.connection() as conn:
            with self.database.cursor(conn) as cursor:
                cursor.execute(
                    """
                    INSERT INTO contacts (
                        id,
                        request_id,
                        name,
                        email,
                        phone,
                        comment,
                        ai_provider,
                        ai_status,
                        category,
                        sentiment,
                        priority,
                        summary,
                        suggested_reply,
                        owner_email_status,
                        user_email_status,
                        owner_email_error,
                        user_email_error
                    ) VALUES (
                        %(id)s,
                        %(request_id)s,
                        %(name)s,
                        %(email)s,
                        %(phone)s,
                        %(comment)s,
                        %(ai_provider)s,
                        %(ai_status)s,
                        %(category)s,
                        %(sentiment)s,
                        %(priority)s,
                        %(summary)s,
                        %(suggested_reply)s,
                        %(owner_email_status)s,
                        %(user_email_status)s,
                        %(owner_email_error)s,
                        %(user_email_error)s
                    )
                    RETURNING *
                    """,
                    record,
                )
                row = cursor.fetchone()
                return dict(row) if row else record

    def update_delivery_statuses(
        self,
        contact_id: str,
        *,
        owner_status: str,
        user_status: str,
        owner_error: Optional[str],
        user_error: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        with self.database.connection() as conn:
            with self.database.cursor(conn) as cursor:
                cursor.execute(
                    """
                    UPDATE contacts
                    SET owner_email_status = %s,
                        user_email_status = %s,
                        owner_email_error = %s,
                        user_email_error = %s
                    WHERE id = %s
                    RETURNING *
                    """,
                    (owner_status, user_status, owner_error, user_error, contact_id),
                )
                row = cursor.fetchone()
                return dict(row) if row else None

