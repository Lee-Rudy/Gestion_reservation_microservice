"""
Tests unitaires du Saga Réservation + Paiement.

Stratégie :
    - Repository en mémoire (pas de connexion MySQL)
    - PaiementServicePort mocké (pas d'appel HTTP réel)
    → Tests rapides, isolés, sans infrastructure externe

Cas couverts (ticket) :
    1. Paiement succès  → réservation CONFIRMED
    2. Paiement échec   → réservation CANCELLED
    3. Cohérence des états après chaque scénario
    4. Rollback si le paiement-service lève une exception
"""

from typing import Optional
from unittest.mock import MagicMock

import pytest

from reservation_service.application.saga.paiement_port import PaiementServicePort
from reservation_service.application.saga.saga_use_case import (
    SagaReservationPaiementUseCase,
)
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_repository import (
    ReservationRepository,
)
from reservation_service.domain.reservation.reservation_service import (
    ReservationService,
)
from reservation_service.domain.reservation.reservation_status import ReservationStatus


# ─── Repository en mémoire (remplace MySQL pour les tests) ───────────────────


class ReservationRepositoryInMemory(ReservationRepository):
    """Repository in-memory pour les tests unitaires.

    Simule le comportement du repository MySQL sans connexion base de
    données. Chaque instance est isolée et réinitialisée entre les tests.
    """

    def __init__(self):
        # Stockage interne : {id: Reservation}
        self._store: dict[int, Reservation] = {}
        self._next_id = 1

    def save(self, reservation: Reservation) -> Reservation:
        """INSERT si id=None, UPDATE sinon."""
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
        """Met à jour le statut sans recréer l'entité."""
        if id in self._store:
            self._store[id].status = status

    def verify_availability(self, category_id, start_date, end_date) -> bool:
        """Toujours disponible en tests (pas de logique de chevauchement)."""
        return True


# ─── Mock du paiement-service ─────────────────────────────────────────────────


class PaiementServiceMockOK(PaiementServicePort):
    """Simule un paiement-service qui accepte tous les paiements."""

    def creer_paiement(self, reservation_id, montant, devise, methode) -> dict:
        # Retourne un UUID fictif, comme le vrai paiement-service
        return {"id": "paiement-uuid-ok", "statut": "en_attente"}

    def valider_paiement(self, paiement_id) -> dict:
        # PSP accepte → statut valide
        return {"id": paiement_id, "statut": "valide"}


class PaiementServiceMockKO(PaiementServicePort):
    """Simule un paiement-service dont le PSP refuse le paiement."""

    def creer_paiement(self, reservation_id, montant, devise, methode) -> dict:
        return {"id": "paiement-uuid-ko", "statut": "en_attente"}

    def valider_paiement(self, paiement_id) -> dict:
        # PSP refuse → statut refuse
        return {"id": paiement_id, "statut": "refuse"}


class PaiementServiceMockError(PaiementServicePort):
    """Simule un paiement-service indisponible (erreur réseau)."""

    def creer_paiement(self, reservation_id, montant, devise, methode) -> dict:
        raise ConnectionError("paiement-service indisponible")

    def valider_paiement(self, paiement_id) -> dict:
        raise ConnectionError("paiement-service indisponible")


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _build_saga(paiement_mock: PaiementServicePort) -> SagaReservationPaiementUseCase:
    """Construit un SagaUseCase avec un repository in-memory et un mock PSP."""
    repo = ReservationRepositoryInMemory()
    service = ReservationService(repo)

    # Mock du category_repository : retourne toujours catégorie "hotel"
    # Note : MagicMock(name=...) définit le nom interne du mock, PAS
    # l'attribut .name. On assigne l'attribut explicitement.
    category_obj = MagicMock()
    category_obj.name = "hotel"
    category_mock = MagicMock()
    category_mock.find_by_id.return_value = category_obj

    return SagaReservationPaiementUseCase(
        reservation_service=service,
        paiement_service=paiement_mock,
        category_repository=category_mock,
    )


def _build_reservation() -> Reservation:
    """Crée une réservation valide avec des dates dans le futur."""
    return Reservation(
        id=None,
        user_id=1,
        category_id=1,
        start_date="2030-06-01T10:00:00",
        end_date="2030-06-03T10:00:00",
        status=ReservationStatus.PENDING,
        nb_persons=2,
    )


# ─── Tests : paiement succès ─────────────────────────────────────────────────


class TestSagaPaiementSucces:
    """Vérifie le chemin nominal : PSP accepte → réservation CONFIRMED."""

    def setup_method(self):
        self.saga = _build_saga(PaiementServiceMockOK())

    def test_reservation_confirmee_apres_paiement_valide(self):
        """La réservation doit être CONFIRMED quand le paiement est accepté."""
        result = self.saga.executer(_build_reservation(), "EUR", "carte")
        assert result["reservation_status"] == "CONFIRMED"

    def test_statut_paiement_est_valide(self):
        """Le statut retourné du paiement doit être 'valide'."""
        result = self.saga.executer(_build_reservation(), "EUR", "carte")
        assert result["paiement_status"] == "valide"

    def test_resultat_contient_reservation_id_et_paiement_id(self):
        """La réponse doit contenir les identifiants de la réservation et du paiement."""
        result = self.saga.executer(_build_reservation(), "EUR", "carte")
        assert "reservation_id" in result
        assert "paiement_id" in result
        assert result["reservation_id"] is not None

    def test_coherence_etat_reservation_en_base(self):
        """La réservation en base doit bien être CONFIRMED (pas seulement dans la réponse)."""
        saga_with_repo = _build_saga(PaiementServiceMockOK())
        # On accède au repository via le service pour vérifier l'état réel
        repo = saga_with_repo.reservation_service.repository
        result = saga_with_repo.executer(_build_reservation(), "EUR", "carte")
        reservation = repo.find_by_id(result["reservation_id"])
        assert reservation.status == ReservationStatus.CONFIRMED


# ─── Tests : paiement échec (rollback) ───────────────────────────────────────


class TestSagaPaiementEchec:
    """Vérifie le rollback : PSP refuse → réservation CANCELLED."""

    def setup_method(self):
        self.saga = _build_saga(PaiementServiceMockKO())

    def test_reservation_annulee_apres_paiement_refuse(self):
        """La réservation doit être CANCELLED quand le PSP refuse."""
        result = self.saga.executer(_build_reservation(), "EUR", "carte")
        assert result["reservation_status"] == "CANCELLED"

    def test_statut_paiement_est_refuse(self):
        """Le statut retourné du paiement doit être 'refuse'."""
        result = self.saga.executer(_build_reservation(), "EUR", "carte")
        assert result["paiement_status"] == "refuse"

    def test_coherence_etat_reservation_annulee_en_base(self):
        """La réservation en base doit bien être CANCELLED après rollback."""
        saga_with_repo = _build_saga(PaiementServiceMockKO())
        repo = saga_with_repo.reservation_service.repository
        result = saga_with_repo.executer(_build_reservation(), "EUR", "carte")
        reservation = repo.find_by_id(result["reservation_id"])
        assert reservation.status == ReservationStatus.CANCELLED


# ─── Tests : erreur inattendue (rollback) ────────────────────────────────────


class TestSagaErreurReseau:
    """Vérifie le rollback quand le paiement-service est injoignable."""

    def setup_method(self):
        self.saga = _build_saga(PaiementServiceMockError())

    def test_leve_une_erreur_apres_rollback(self):
        """Une ValueError doit être levée après que la réservation soit annulée."""
        with pytest.raises(ValueError):
            self.saga.executer(_build_reservation(), "EUR", "carte")

    def test_reservation_annulee_meme_en_cas_erreur_reseau(self):
        """La réservation doit être CANCELLED même si le paiement-service plante."""
        saga_with_repo = _build_saga(PaiementServiceMockError())
        repo = saga_with_repo.reservation_service.repository
        try:
            saga_with_repo.executer(_build_reservation(), "EUR", "carte")
        except ValueError:
            pass
        # La réservation doit exister avec le statut CANCELLED
        reservation = repo.find_by_id(1)
        assert reservation is not None
        assert reservation.status == ReservationStatus.CANCELLED
