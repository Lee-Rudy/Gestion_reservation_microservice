from typing import List

from reservation_service.infrastructure.database.database import get_connection


class LogsRepository:
    def add_log(self, user_email: str, action: str, details: str = "") -> None:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO logs (user_email, action, details) VALUES (%s, %s, %s)",
                (user_email, action, details),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_recent_logs(self, limit: int = 50) -> List[dict]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, user_email, action, details, created_at FROM logs ORDER BY created_at DESC LIMIT %s",
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
