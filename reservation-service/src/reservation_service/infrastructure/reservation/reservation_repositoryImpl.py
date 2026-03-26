from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_repository import (
    ReservationRepository,
)
from reservation_service.infrastructure.database.database import get_connection
from reservation_service.domain.reservation.reservation_status import ReservationStatus


class ReservationRepositoryImpl(ReservationRepository):
    def verify_reservation_exists(self, id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM reservations WHERE id=%s", (id,))
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return exists

    def save(self, reservation: Reservation):
        conn = get_connection()
        cursor = conn.cursor()

        if reservation.id is None:
            query = """
            INSERT INTO reservations
            (user_id, category_id, start_date, end_date, status, nb_persons)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    reservation.user_id,
                    reservation.category_id,
                    reservation.start_date,
                    reservation.end_date,
                    reservation.status.value,
                    reservation.nb_persons,
                ),
            )
            conn.commit()
            reservation.id = cursor.lastrowid
        else:
            query = """
            UPDATE reservations
            SET user_id=%s, category_id=%s, start_date=%s, end_date=%s,
            status=%s, nb_persons=%s
            WHERE id=%s
            """
            cursor.execute(
                query,
                (
                    reservation.user_id,
                    reservation.category_id,
                    reservation.start_date,
                    reservation.end_date,
                    reservation.status.value,
                    reservation.id,
                    reservation.nb_persons,
                ),
            )
            conn.commit()
        cursor.close()
        conn.close()
        return reservation

    def verify_availability(
        self, category_id: int, start_date: str, end_date: str
    ) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
        SELECT id FROM reservations
        WHERE category_id=%s AND (
            (status='PENDING' OR status='CONFIRMED') AND
            NOT (end_date <= %s OR start_date >= %s)
        )
        """
        cursor.execute(query, (category_id, end_date, start_date))
        available = cursor.fetchone() is None
        cursor.close()
        conn.close()
        return available

    def delete(self, id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reservations WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()

    def update_status(self, id: int, status) -> None:
        """Met à jour uniquement le statut d'une réservation en base.

        Requête ciblée : évite de recharger l'entité complète et de
        déclencher les validations de dates (utile pour le Saga).
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reservations SET status=%s WHERE id=%s", (status.value, id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def find_by_id(self, id: int) -> Reservation:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reservations WHERE id=%s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return None

        reservation = Reservation(
            id=result["id"],
            user_id=result["user_id"],
            category_id=result["category_id"],
            start_date=result["start_date"],
            end_date=result["end_date"],
            status=ReservationStatus(result["status"]),
            nb_persons=result["nb_persons"],
        )
        reservation.id = result["id"]
        return reservation
