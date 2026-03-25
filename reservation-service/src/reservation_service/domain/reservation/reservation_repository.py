from abc import ABC, abstractmethod
from reservation_service.domain.reservation.reservation import Reservation
from typing import Optional

class ReservationRepository(ABC):
    @abstractmethod
    def save(self, reservation: Reservation) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Reservation]:
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        pass