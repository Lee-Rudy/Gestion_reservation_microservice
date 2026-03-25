"""
Tests des cas d'usage de la couche application.

Utilise les adaptateurs in-memory (repository, fournisseur simulé)
pour tester l'orchestration sans infrastructure externe.
Ces tests vérifient la logique d'application, pas les détails d'entité.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from paiement_service.adapters.payment_provider import FournisseurPaiementSimule
from paiement_service.adapters.repository import PaiementRepositoryEnMemoire
from paiement_service.application.use_cases import (
    CommandeInitierPaiement,
    CommandeRembourserPaiement,
    CommandeValiderPaiement,
    InitierPaiementUseCase,
    ObtenirPaiementUseCase,
    RembourserPaiementUseCase,
    ValiderPaiementUseCase,
)
from paiement_service.domain.entities.paiement import MethodePaiement, StatutPaiement
from paiement_service.domain.events.paiement_events import (
    PaiementInitie,
    PaiementRefuse,
    PaiementRembourse,
    PaiementValide,
)
from paiement_service.domain.services.paiement_service import PaiementDomainService


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _commande_base(
    montant: Decimal = Decimal("100.00"),
    devise: str = "EUR",
    methode: MethodePaiement = MethodePaiement.CARTE,
) -> CommandeInitierPaiement:
    """Crée une commande d'initiation avec des valeurs par défaut."""
    return CommandeInitierPaiement(
        reservation_id=uuid4(),
        montant=montant,
        devise=devise,
        methode=methode,
    )


# ─── InitierPaiementUseCase ──────────────────────────────────────────────────


class TestInitierPaiementUseCase:
    def setup_method(self) -> None:
        self.repo = PaiementRepositoryEnMemoire()
        self.svc = PaiementDomainService()
        self.uc = InitierPaiementUseCase(self.repo, self.svc)

    def test_cree_paiement_en_attente(self) -> None:
        """Le paiement créé doit avoir le statut EN_ATTENTE."""
        paiement, _ = self.uc.executer(_commande_base())
        assert paiement.statut == StatutPaiement.EN_ATTENTE

    def test_emet_evenement_paiement_initie(self) -> None:
        """L'événement retourné doit être de type PaiementInitie."""
        paiement, evenement = self.uc.executer(_commande_base())
        assert isinstance(evenement, PaiementInitie)
        assert evenement.paiement_id == paiement.id

    def test_persiste_le_paiement(self) -> None:
        """Le paiement créé doit être retrouvable via le repository."""
        paiement, _ = self.uc.executer(_commande_base())
        trouve = self.repo.obtenir_par_id(paiement.id)
        assert trouve is not None
        assert trouve.id == paiement.id

    def test_normalise_la_devise_en_majuscules(self) -> None:
        """La devise doit être normalisée en majuscules."""
        paiement, _ = self.uc.executer(_commande_base(devise="eur"))
        assert paiement.devise == "EUR"

    def test_montant_invalide_leve_erreur(self) -> None:
        """Un montant nul doit lever ValueError sans créer de paiement."""
        with pytest.raises(ValueError):
            self.uc.executer(_commande_base(montant=Decimal("0")))
        assert len(self.repo.lister_tous()) == 0

    def test_devise_invalide_leve_erreur(self) -> None:
        """Une devise inconnue doit lever ValueError."""
        with pytest.raises(ValueError, match="XYZ"):
            self.uc.executer(_commande_base(devise="XYZ"))


# ─── ValiderPaiementUseCase ──────────────────────────────────────────────────


class TestValiderPaiementUseCase:
    def setup_method(self) -> None:
        self.repo = PaiementRepositoryEnMemoire()
        self.fournisseur_ok = FournisseurPaiementSimule(traitement_accepte=True)
        self.fournisseur_ko = FournisseurPaiementSimule(traitement_accepte=False)
        initier_uc = InitierPaiementUseCase(self.repo, PaiementDomainService())
        paiement, _ = initier_uc.executer(_commande_base())
        self.paiement_id = paiement.id

    def test_validation_reussie_change_statut_en_valide(self) -> None:
        """Si le PSP accepte, le statut doit passer à VALIDE."""
        uc = ValiderPaiementUseCase(self.repo, self.fournisseur_ok)
        paiement, _ = uc.executer(CommandeValiderPaiement(self.paiement_id))
        assert paiement.statut == StatutPaiement.VALIDE

    def test_validation_reussie_emet_evenement_valide(self) -> None:
        """Un PSP qui accepte doit émettre PaiementValide."""
        uc = ValiderPaiementUseCase(self.repo, self.fournisseur_ok)
        _, evenement = uc.executer(CommandeValiderPaiement(self.paiement_id))
        assert isinstance(evenement, PaiementValide)

    def test_validation_echouee_change_statut_en_refuse(self) -> None:
        """Si le PSP refuse, le statut doit passer à REFUSE."""
        uc = ValiderPaiementUseCase(self.repo, self.fournisseur_ko)
        paiement, _ = uc.executer(CommandeValiderPaiement(self.paiement_id))
        assert paiement.statut == StatutPaiement.REFUSE

    def test_validation_echouee_emet_evenement_refuse(self) -> None:
        """Un PSP qui refuse doit émettre PaiementRefuse."""
        uc = ValiderPaiementUseCase(self.repo, self.fournisseur_ko)
        _, evenement = uc.executer(CommandeValiderPaiement(self.paiement_id))
        assert isinstance(evenement, PaiementRefuse)

    def test_paiement_introuvable_leve_erreur(self) -> None:
        """Valider un paiement inexistant doit lever ValueError."""
        uc = ValiderPaiementUseCase(self.repo, self.fournisseur_ok)
        with pytest.raises(ValueError, match="introuvable"):
            uc.executer(CommandeValiderPaiement(uuid4()))


# ─── RembourserPaiementUseCase ───────────────────────────────────────────────


class TestRembourserPaiementUseCase:
    def setup_method(self) -> None:
        self.repo = PaiementRepositoryEnMemoire()
        self.domain_svc = PaiementDomainService()
        fournisseur_ok = FournisseurPaiementSimule(
            traitement_accepte=True, remboursement_accepte=True
        )
        # Prépare un paiement VALIDE
        initier_uc = InitierPaiementUseCase(self.repo, self.domain_svc)
        paiement, _ = initier_uc.executer(_commande_base())
        valider_uc = ValiderPaiementUseCase(self.repo, fournisseur_ok)
        valider_uc.executer(CommandeValiderPaiement(paiement.id))
        self.paiement_id = paiement.id

    def test_remboursement_reussi_change_statut_en_rembourse(self) -> None:
        """Un remboursement réussi doit changer le statut en REMBOURSE."""
        fournisseur = FournisseurPaiementSimule(remboursement_accepte=True)
        uc = RembourserPaiementUseCase(self.repo, fournisseur, self.domain_svc)
        paiement, _ = uc.executer(CommandeRembourserPaiement(self.paiement_id))
        assert paiement.statut == StatutPaiement.REMBOURSE

    def test_remboursement_reussi_emet_evenement(self) -> None:
        """Un remboursement réussi doit émettre PaiementRembourse."""
        fournisseur = FournisseurPaiementSimule(remboursement_accepte=True)
        uc = RembourserPaiementUseCase(self.repo, fournisseur, self.domain_svc)
        _, evenement = uc.executer(CommandeRembourserPaiement(self.paiement_id))
        assert isinstance(evenement, PaiementRembourse)

    def test_psp_refuse_remboursement_leve_erreur(self) -> None:
        """Si le PSP refuse le remboursement, ValueError doit être levée."""
        fournisseur = FournisseurPaiementSimule(remboursement_accepte=False)
        uc = RembourserPaiementUseCase(self.repo, fournisseur, self.domain_svc)
        with pytest.raises(ValueError, match="refusé"):
            uc.executer(CommandeRembourserPaiement(self.paiement_id))

    def test_paiement_introuvable_leve_erreur(self) -> None:
        """Rembourser un paiement inexistant doit lever ValueError."""
        fournisseur = FournisseurPaiementSimule()
        uc = RembourserPaiementUseCase(self.repo, fournisseur, self.domain_svc)
        with pytest.raises(ValueError, match="introuvable"):
            uc.executer(CommandeRembourserPaiement(uuid4()))

    def test_paiement_non_valide_leve_erreur(self) -> None:
        """Rembourser un paiement EN_ATTENTE doit lever ValueError."""
        initier_uc = InitierPaiementUseCase(self.repo, self.domain_svc)
        p_en_attente, _ = initier_uc.executer(_commande_base())
        fournisseur = FournisseurPaiementSimule()
        uc = RembourserPaiementUseCase(self.repo, fournisseur, self.domain_svc)
        with pytest.raises(ValueError, match="remboursable"):
            uc.executer(CommandeRembourserPaiement(p_en_attente.id))


# ─── ObtenirPaiementUseCase ──────────────────────────────────────────────────


class TestObtenirPaiementUseCase:
    def setup_method(self) -> None:
        self.repo = PaiementRepositoryEnMemoire()
        initier_uc = InitierPaiementUseCase(self.repo, PaiementDomainService())
        paiement, _ = initier_uc.executer(_commande_base())
        self.paiement_id = paiement.id
        self.uc = ObtenirPaiementUseCase(self.repo)

    def test_retourne_le_paiement_existant(self) -> None:
        """Doit retourner le paiement correspondant à l'identifiant."""
        paiement = self.uc.executer(self.paiement_id)
        assert paiement.id == self.paiement_id

    def test_paiement_inexistant_leve_erreur(self) -> None:
        """Chercher un UUID inexistant doit lever ValueError."""
        with pytest.raises(ValueError, match="introuvable"):
            self.uc.executer(uuid4())
