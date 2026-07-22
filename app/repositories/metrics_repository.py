from typing import Any, Dict

from app.infrastructure.database import PostgresDatabase


class MetricsRepository:
    def __init__(self, database: PostgresDatabase) -> None:
        self.database = database

    def get(self) -> Dict[str, Any]:
        with self.database.connection() as conn:
            with self.database.cursor(conn) as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM contacts")
                total_contacts = int(cursor.fetchone()["count"])

                cursor.execute("SELECT COUNT(*) AS count FROM contacts WHERE ai_status = 'success'")
                ai_success = int(cursor.fetchone()["count"])

                cursor.execute("SELECT COUNT(*) AS count FROM contacts WHERE ai_status = 'fallback'")
                ai_fallback = int(cursor.fetchone()["count"])

                cursor.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM contacts
                    WHERE owner_email_status = 'failed'
                       OR user_email_status = 'failed'
                    """
                )
                email_failures = int(cursor.fetchone()["count"])

                cursor.execute(
                    """
                    SELECT COALESCE(jsonb_object_agg(category, category_count), '{}'::jsonb) AS categories
                    FROM (
                        SELECT COALESCE(category, 'general') AS category, COUNT(*) AS category_count
                        FROM contacts
                        GROUP BY COALESCE(category, 'general')
                    ) AS grouped_categories
                    """
                )
                categories = cursor.fetchone()["categories"] or {}

        return {
            "total_contacts": total_contacts,
            "ai_success": ai_success,
            "ai_fallback": ai_fallback,
            "email_failures": email_failures,
            "categories": categories,
        }
