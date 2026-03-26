from enum import Enum
from .reservation_status import ReservationStatus
from datetime import datetime


class Reservation:
    def __init__(
        self,
        id: int,
        user_id: int,
        category_id: int,
        start_date: str,
        end_date: str,
        status: ReservationStatus = ReservationStatus.PENDING,
        expires_at: str = None,
        nb_persons: int = 1
    ):
        self._validate_user_id(user_id)
        self._validate_category_id(category_id)
        self._validate_dates(start_date, end_date)
        self._validate_status(status)
        self._validate_expires_at(expires_at)
        self._validate_nb_persons(nb_persons)

        self.id = id
        self.user_id = user_id
        self.category_id = category_id
        self.start_date = start_date
        self.end_date = end_date
        self.status = status
        self.expires_at = expires_at
        self.nb_persons = nb_persons

    def _validate_user_id(self, user_id: int):
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("L'ID de l'utilisateur doit être un entier positif")

    def _validate_category_id(self, category_id: int):
        if not isinstance(category_id, int) or category_id <= 0:
            raise ValueError("L'ID de la catégorie doit être un entier positif")

    def _validate_nb_persons(self, nb_persons: int):
        if not isinstance(nb_persons, int) or nb_persons <= 0:
            raise ValueError("Le nombre de personnes doit être un entier positif")

    def _validate_dates(self, start_date, end_date):
        if not start_date or not end_date:
            raise ValueError("Les dates de début et de fin sont requises")

        # Convertir si c'est un string
        if isinstance(start_date, str):
            start_dt = datetime.fromisoformat(start_date)
        else:
            start_dt = start_date

        if isinstance(end_date, str):
            end_dt = datetime.fromisoformat(end_date)
        else:
            end_dt = end_date

        if start_dt >= end_dt:
            raise ValueError("La date de début doit être antérieure à la date de fin")

        if start_dt < datetime.now():
            raise ValueError("La date de début doit être dans le futur")

        def _current_date(self):
            from datetime import datetime

            return datetime.now().isoformat()

    def _validate_status(self, status: ReservationStatus):
        if not isinstance(status, ReservationStatus):
            raise ValueError(
                "Le statut de la réservation doit être une instance de ReservationStatus"
            )

    def _validate_expires_at(self, expires_at: str):
        if expires_at and expires_at <= self._current_date():
            raise ValueError("La date d'expiration doit être dans le futur")
