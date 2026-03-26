"""
Tests unitaires de la couche Reservation.

Couvre :
    - Entité Reservation (validations du domaine)
    - ReservationService (règles métier avec repo mock)
    - ReservationUseCase (orchestration)
    - ReservationController (endpoints HTTP via TestClient)
    - QuoteService (calcul du montant par catégorie)
"""

from typing import Optional
from unittest.mock import MagicMock

import importlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from reservation_service.application.reservation.quote_service import QuoteService
from reservation_service.application.reservation.use_case import ReservationUseCase
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_repository import (
    ReservationRepository,
)
from reservation_service.domain.reservation.reservation_service import (
    ReservationService,
)
from reservation_service.domain.reservation.reservation_status import ReservationStatus


# ─── Repository in-memory ─────────────────────────────────────────────────────


class ReservationRepositoryInMemory(ReservationRepository):
    """Repository in-memory pour les tests — pas de connexion MySQL."""

    def __init__(self):
        self._store: dict[int, Reservation] = {}
        self._next_id = 1

    def save(self, reservation: Reservation) -> Reservation:
        if reservation.id is None:
            reservation.id = self._next_id
            self._next_id += 1
        self._store[reservation.id] = reservation
        return reservation

    def find_by_id(self, id: int) -> Optional[Reservation]:
        return self._store.get(id)

    def delete(self, id: int) -> None:
        self._store.pop(id, None)

    def update_status(self, id: int, status: ReservationStatus) -> None:
        if id in self._store:
            self._store[id].status = status

    def verify_availability(self, category_id, start_date, end_date) -> bool:
        """Toujours disponible dans les tests unitaires."""
        return True


# ─── Helpers ──────────────────────────────────────────────────────────────────

# Dates toujours dans le futur pour éviter les erreurs de validation
START = "2030-06-01T10:00:00"
END = "2030-06-03T10:00:00"


def _build_reservation(**kwargs) -> Reservation:
    defaults = dict(
        id=None,
        user_id=1,
        category_id=1,
        start_date=START,
        end_date=END,
        status=ReservationStatus.PENDING,
        nb_persons=2,
    )
    defaults.update(kwargs)
    return Reservation(**defaults)


def _build_client() -> TestClient:
    """Crée un TestClient avec repo in-memory et category_repository mocké.

    Reload du module contrôleur pour obtenir un APIRouter vierge à chaque
    appel (le router est module-level dans le code de Christina).
    """
    import reservation_service.adapters.reservation.reservation_controller as mod

    importlib.reload(mod)
    app = FastAPI()
    repo = ReservationRepositoryInMemory()
    service = ReservationService(repo)
    category_repo = MagicMock()
    category_repo.find_by_id.return_value = None
    use_case = ReservationUseCase(service, category_repo)
    app.include_router(mod.create_reservation_controller(use_case))
    return TestClient(app)


# ─── Tests : entité Reservation ───────────────────────────────────────────────


class TestReservationEntity:
    def test_creation_valide(self):
        r = _build_reservation()
        assert r.user_id == 1
        assert r.status == ReservationStatus.PENDING

    def test_user_id_invalide(self):
        with pytest.raises(ValueError, match="utilisateur"):
            _build_reservation(user_id=0)

    def test_category_id_invalide(self):
        with pytest.raises(ValueError, match="catégorie"):
            _build_reservation(category_id=-1)

    def test_nb_persons_invalide(self):
        with pytest.raises(ValueError, match="personnes"):
            _build_reservation(nb_persons=0)

    def test_dates_manquantes(self):
        with pytest.raises(ValueError):
            _build_reservation(start_date=None, end_date=None)

    def test_date_debut_apres_fin(self):
        with pytest.raises(ValueError, match="antérieure"):
            _build_reservation(
                start_date="2030-06-03T10:00:00", end_date="2030-06-01T10:00:00"
            )

    def test_statut_invalide(self):
        with pytest.raises(ValueError, match="statut"):
            _build_reservation(status="INVALID")


# ─── Tests : ReservationService ───────────────────────────────────────────────


class TestReservationService:
    def setup_method(self):
        self.repo = ReservationRepositoryInMemory()
        self.service = ReservationService(self.repo)

    def test_create_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        assert r.id is not None
        assert r.status == ReservationStatus.PENDING

    def test_get_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        found = self.service.get_reservation(r.id)
        assert found.id == r.id

    def test_get_reservation_inexistante(self):
        assert self.service.get_reservation(999) is None

    def test_update_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        updated = self.service.update_reservation(
            r.id, _build_reservation(nb_persons=5)
        )
        assert updated.nb_persons == 5

    def test_update_reservation_inexistante(self):
        result = self.service.update_reservation(999, _build_reservation())
        assert result is None

    def test_delete_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        assert self.service.delete_reservation(r.id) is True
        assert self.service.get_reservation(r.id) is None

    def test_delete_reservation_inexistante(self):
        assert self.service.delete_reservation(999) is False

    def test_confirm_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        self.service.confirm_reservation(r.id)
        assert self.repo.find_by_id(r.id).status == ReservationStatus.CONFIRMED

    def test_cancel_reservation(self):
        r = self.service.create_reservation(_build_reservation())
        self.service.cancel_reservation(r.id)
        assert self.repo.find_by_id(r.id).status == ReservationStatus.CANCELLED


# ─── Tests : QuoteService ─────────────────────────────────────────────────────


class TestQuoteService:
    def setup_method(self):
        self.qs = QuoteService()
        self.reservation = _build_reservation()

    def test_hotel_2_nuits(self):
        quote = self.qs.generate_quote(self.reservation, "hotel")
        assert quote["amount"] == 200.0  # 2 nuits * 100€

    def test_restaurant(self):
        quote = self.qs.generate_quote(self.reservation, "restaurant")
        assert quote["amount"] == 40.0  # 2 personnes * 20€

    def test_salle(self):
        quote = self.qs.generate_quote(self.reservation, "salle")
        assert quote["amount"] == 2400.0  # 48h * 50€

    def test_categorie_inconnue_leve_erreur(self):
        with pytest.raises(ValueError, match="Catégorie inconnue"):
            self.qs.generate_quote(self.reservation, "inconnu")

    def test_devise_retournee(self):
        quote = self.qs.generate_quote(self.reservation, "hotel")
        assert quote["currency"] == "EUR"


# ─── Tests : ReservationController (HTTP) ─────────────────────────────────────


class TestReservationController:
    def setup_method(self):
        self.client = _build_client()

    def _payload(self, **kwargs) -> dict:
        base = {
            "user_id": 1,
            "category_id": 1,
            "start_date": START,
            "end_date": END,
            "nb_persons": 2,
        }
        base.update(kwargs)
        return base

    def test_create_retourne_201(self):
        r = self.client.post("/reservations", json=self._payload())
        assert r.status_code == 201
        assert r.json()["status"] == "PENDING"

    def test_create_user_id_invalide_retourne_400(self):
        r = self.client.post("/reservations", json=self._payload(user_id=0))
        assert r.status_code == 400

    def test_get_by_id_existant(self):
        created = self.client.post("/reservations", json=self._payload()).json()
        r = self.client.get(f"/reservations/{created['id']}")
        assert r.status_code == 200

    def test_get_by_id_inexistant_retourne_404(self):
        r = self.client.get("/reservations/9999")
        assert r.status_code == 404

    def test_update_existant(self):
        created = self.client.post("/reservations", json=self._payload()).json()
        r = self.client.put(
            f"/reservations/{created['id']}", json=self._payload(nb_persons=5)
        )
        assert r.status_code == 200

    def test_update_inexistant_retourne_404(self):
        r = self.client.put("/reservations/9999", json=self._payload())
        assert r.status_code == 404

    def test_delete_existant_retourne_204(self):
        created = self.client.post("/reservations", json=self._payload()).json()
        r = self.client.delete(f"/reservations/{created['id']}")
        assert r.status_code == 204

    def test_delete_inexistant_retourne_404(self):
        r = self.client.delete("/reservations/9999")
        assert r.status_code == 404
