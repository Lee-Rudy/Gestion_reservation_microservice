"""
Fixtures partagées entre tous les fichiers de tests.

Fournit des objets préconfigurés (repository, fournisseur, use cases)
pour éviter la duplication dans chaque fichier de test.
"""

import pytest

from paiement_service.adapters.payment_provider import FournisseurPaiementSimule
from paiement_service.adapters.repository import PaiementRepositoryEnMemoire
from paiement_service.domain.services.paiement_service import PaiementDomainService


@pytest.fixture
def repository() -> PaiementRepositoryEnMemoire:
    """Repository in-memory vide, réinitialisé à chaque test."""
    return PaiementRepositoryEnMemoire()


@pytest.fixture
def fournisseur_ok() -> FournisseurPaiementSimule:
    """PSP simulé qui accepte tous les paiements et remboursements."""
    return FournisseurPaiementSimule(
        traitement_accepte=True, remboursement_accepte=True
    )


@pytest.fixture
def fournisseur_ko() -> FournisseurPaiementSimule:
    """PSP simulé qui refuse tous les paiements."""
    return FournisseurPaiementSimule(
        traitement_accepte=False, remboursement_accepte=False
    )


@pytest.fixture
def domain_service() -> PaiementDomainService:
    """Instance du service domaine sans état."""
    return PaiementDomainService()
