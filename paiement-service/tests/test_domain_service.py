"""
Tests unitaires du service domaine PaiementDomainService.

Vérifie les règles de validation métier (montant, devise)
et la logique d'éligibilité au remboursement.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from paiement_service.domain.entities.paiement import (
    MethodePaiement,
    Paiement,
    StatutPaiement,
)
from paiement_service.domain.services.paiement_service import PaiementDomainService


# ─── Fixture locale ──────────────────────────────────────────────────────────


def _service() -> PaiementDomainService:
    return PaiementDomainService()


# ─── Tests : valider_parametres_creation ─────────────────────────────────────


def test_parametres_valides_ne_leve_pas_derreur() -> None:
    """Des paramètres corrects ne doivent pas lever d'exception."""
    _service().valider_parametres_creation(Decimal("100.00"), "EUR")


def test_montant_zero_leve_erreur() -> None:
    """Un montant nul doit être rejeté (minimum = 0.01)."""
    with pytest.raises(ValueError, match="minimum"):
        _service().valider_parametres_creation(Decimal("0.00"), "EUR")


def test_montant_negatif_leve_erreur() -> None:
    """Un montant négatif doit être rejeté."""
    with pytest.raises(ValueError, match="minimum"):
        _service().valider_parametres_creation(Decimal("-10.00"), "EUR")


def test_montant_trop_eleve_leve_erreur() -> None:
    """Un montant supérieur à 100 000 doit être rejeté."""
    with pytest.raises(ValueError, match="maximum"):
        _service().valider_parametres_creation(Decimal("100000.01"), "EUR")


def test_montant_maximum_exact_est_accepte() -> None:
    """Le montant maximum exact (100 000) doit être accepté."""
    _service().valider_parametres_creation(Decimal("100000.00"), "EUR")


def test_montant_minimum_exact_est_accepte() -> None:
    """Le montant minimum exact (0.01) doit être accepté."""
    _service().valider_parametres_creation(Decimal("0.01"), "EUR")


def test_devise_inconnue_leve_erreur() -> None:
    """Une devise non supportée doit être rejetée."""
    with pytest.raises(ValueError, match="XYZ"):
        _service().valider_parametres_creation(Decimal("50.00"), "XYZ")


def test_devise_en_minuscules_est_acceptee() -> None:
    """La devise en minuscules doit être normalisée et acceptée."""
    _service().valider_parametres_creation(Decimal("50.00"), "eur")


@pytest.mark.parametrize("devise", ["EUR", "USD", "GBP"])
def test_toutes_les_devises_acceptees(devise: str) -> None:
    """Chaque devise supportée doit être acceptée sans erreur."""
    _service().valider_parametres_creation(Decimal("50.00"), devise)


# ─── Tests : est_remboursable ────────────────────────────────────────────────


def _paiement(statut: StatutPaiement) -> Paiement:
    """Crée un paiement avec le statut indiqué pour les tests."""
    p = Paiement(
        reservation_id=uuid4(),
        montant=Decimal("50.00"),
        devise="EUR",
        methode=MethodePaiement.CARTE,
    )
    # Forcer le statut directement pour le test
    object.__setattr__(p, "statut", statut)
    return p


def test_paiement_valide_est_remboursable() -> None:
    """Un paiement VALIDE doit être considéré comme remboursable."""
    p = _paiement(StatutPaiement.VALIDE)
    assert _service().est_remboursable(p) is True


def test_paiement_en_attente_non_remboursable() -> None:
    """Un paiement EN_ATTENTE ne doit pas être remboursable."""
    p = _paiement(StatutPaiement.EN_ATTENTE)
    assert _service().est_remboursable(p) is False


def test_paiement_refuse_non_remboursable() -> None:
    """Un paiement REFUSE ne doit pas être remboursable."""
    p = _paiement(StatutPaiement.REFUSE)
    assert _service().est_remboursable(p) is False


def test_paiement_deja_rembourse_non_remboursable() -> None:
    """Un paiement déjà REMBOURSE ne doit pas être remboursable à nouveau."""
    p = _paiement(StatutPaiement.REMBOURSE)
    assert _service().est_remboursable(p) is False
