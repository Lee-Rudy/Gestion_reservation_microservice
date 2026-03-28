from fastapi import APIRouter

from reservation_service.infrastructure.reservation.reservation_repositoryImpl import (
    ReservationRepositoryImpl,
)


def create_get_all_reservations_controller():
    router = APIRouter()

    @router.get("/reservations")
    def get_all_reservations():
        repo = ReservationRepositoryImpl()
        try:
            conn = repo.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT r.id, r.user_email, r.category_id, r.start_date, r.end_date, 
                       r.status, r.nb_persons, c.name as category_name
                FROM reservations r
                LEFT JOIN categories c ON r.category_id = c.id
                ORDER BY r.created_at DESC
                """
            )
            reservations = cursor.fetchall()
            cursor.close()
            conn.close()
            return reservations
        except Exception:
            return []

    return router
