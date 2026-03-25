from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_repository import ReservationRepository

class ReservationService:
    def __init__(self, repository: ReservationRepository):
        self.repository = repository

    def create_reservation(self, reservation: Reservation) -> Reservation:
        # Vérifier disponibilité avant de sauvegarder
        if not self.repository.verify_availability(reservation.category_id, reservation.start_date, reservation.end_date):
            raise ValueError("La réservation n'est pas disponible pour ces dates")
        return self.repository.save(reservation)

    def get_reservation(self, id: int) -> Reservation | None:
        return self.repository.find_by_id(id)

    def update_reservation(self, id: int, reservation: Reservation) -> Reservation | None:
        if not self.repository.find_by_id(id):
            return None
        return self.repository.save(reservation)

    def delete_reservation(self, id: int) -> bool:
        if not self.repository.find_by_id(id):
            return False
        self.repository.delete(id)
        return True