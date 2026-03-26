from abc import ABC, abstractmethod
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_status import ReservationStatus
from typing import Optional


class ReservationRepository(ABC):
    @abstractmethod
    def save(self, reservation: Reservation) -> Reservation:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Reservation]:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass

    @abstractmethod
    def update_status(self, id: int, status: ReservationStatus) -> None:
        """Met à jour uniquement le statut d'une réservation.

        Utilisé par le Saga pour confirmer ou annuler une réservation
        sans avoir à recharger et re-valider l'entité complète.
        """
        pass

    @abstractmethod
    def verify_availability(
        self, category_id: int, start_date: str, end_date: str
    ) -> bool:
        """Vérifie la disponibilité pour une catégorie durant une période."""
        pass
