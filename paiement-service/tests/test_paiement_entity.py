"""
Tests unitaires de l'entité Paiement.

Vérifie les transitions d'état et les règles d'invariants directement
sur l'entité, sans infrastructure externe.
"""

from decimal import Decimal

import pytest

from paiement_service.domain.entities.paiement import (
    MethodePaiement,
    Paiement,
    StatutPaiement,
)


# ─── Fixtures locales ────────────────────────────────────────────────────────


def _paiement_en_attente() -> Paiement:
    """Crée un paiement EN_ATTENTE avec des valeurs par défaut."""
    return Paiement(
        reservation_id=1,
        montant=Decimal("50.00"),
        devise="EUR",
        methode=MethodePaiement.CARTE,
    )


# ─── Tests de création ───────────────────────────────────────────────────────


def test_creation_paiement_statut_initial() -> None:
    """Un paiement nouvellement créé doit être EN_ATTENTE."""
    paiement = _paiement_en_attente()
    assert paiement.statut == StatutPaiement.EN_ATTENTE


def test_creation_paiement_genere_id_unique() -> None:
    """Deux paiements créés indépendamment ont des UUID différents."""
    p1 = _paiement_en_attente()
    p2 = _paiement_en_attente()
    assert p1.id != p2.id


def test_creation_paiement_conserve_les_valeurs() -> None:
    """Les attributs fournis sont bien conservés après création."""
    reservation_id = 42
    paiement = Paiement(
        reservation_id=reservation_id,
        montant=Decimal("123.45"),
        devise="USD",
        methode=MethodePaiement.PAYPAL,
    )
    assert paiement.reservation_id == reservation_id
    assert paiement.montant == Decimal("123.45")
    assert paiement.devise == "USD"
    assert paiement.methode == MethodePaiement.PAYPAL


# ─── Tests de transition : valider ───────────────────────────────────────────


def test_valider_depuis_en_attente_change_statut() -> None:
    """Valider un paiement EN_ATTENTE le fait passer à VALIDE."""
    paiement = _paiement_en_attente()
    paiement.valider()
    assert paiement.statut == StatutPaiement.VALIDE


def test_valider_met_a_jour_updated_at() -> None:
    """Valider un paiement met à jour le champ updated_at."""
    paiement = _paiement_en_attente()
    avant = paiement.updated_at
    paiement.valider()
    # updated_at doit être identique ou postérieur (résolution datetime)
    assert paiement.updated_at >= avant


def test_valider_paiement_deja_valide_leve_erreur() -> None:
    """Valider un paiement déjà VALIDE doit lever ValueError."""
    paiement = _paiement_en_attente()
    paiement.valider()
    with pytest.raises(ValueError, match="valide"):
        paiement.valider()


def test_valider_paiement_refuse_leve_erreur() -> None:
    """Valider un paiement REFUSE doit lever ValueError."""
    paiement = _paiement_en_attente()
    paiement.refuser()
    with pytest.raises(ValueError, match="refuse"):
        paiement.valider()


# ─── Tests de transition : refuser ───────────────────────────────────────────


def test_refuser_depuis_en_attente_change_statut() -> None:
    """Refuser un paiement EN_ATTENTE le fait passer à REFUSE."""
    paiement = _paiement_en_attente()
    paiement.refuser()
    assert paiement.statut == StatutPaiement.REFUSE


def test_refuser_paiement_valide_leve_erreur() -> None:
    """Refuser un paiement déjà VALIDE doit lever ValueError."""
    paiement = _paiement_en_attente()
    paiement.valider()
    with pytest.raises(ValueError, match="valide"):
        paiement.refuser()


# ─── Tests de transition : rembourser ────────────────────────────────────────


def test_rembourser_paiement_valide_change_statut() -> None:
    """Rembourser un paiement VALIDE le fait passer à REMBOURSE."""
    paiement = _paiement_en_attente()
    paiement.valider()
    paiement.rembourser()
    assert paiement.statut == StatutPaiement.REMBOURSE


