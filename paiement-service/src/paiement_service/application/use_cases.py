"""
Cas d'usage de la couche application.

Chaque cas d'usage orchestre les entités du domaine et les ports
secondaires pour réaliser une opération métier complète.
Ils constituent la frontière entre les adaptateurs primaires (HTTP, CLI)
et le cœur métier (domain).

Cas d'usage disponibles :
    - InitierPaiementUseCase    : créer un paiement EN_ATTENTE
    - ValiderPaiementUseCase    : soumettre au PSP et changer le statut
    - RembourserPaiementUseCase : rembourser un paiement VALIDE
    - ObtenirPaiementUseCase    : lire un paiement par son identifiant
"""

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from paiement_service.application.ports import IFournisseurPaiement, IPaiementRepository
from paiement_service.domain.entities.paiement import MethodePaiement, Paiement
from paiement_service.domain.events.paiement_events import (
    EvenementDomaine,
    PaiementInitie,
    PaiementRefuse,
    PaiementRembourse,
    PaiementValide,
)
from paiement_service.domain.services.paiement_service import PaiementDomainService


# ─── Commandes (DTOs d'entrée) ───────────────────────────────────────────────


@dataclass(frozen=True)
class CommandeInitierPaiement:
    """Données nécessaires pour initier un nouveau paiement."""

    reservation_id: UUID
    montant: Decimal
    devise: str
    methode: MethodePaiement


@dataclass(frozen=True)
class CommandeValiderPaiement:
    """Données nécessaires pour déclencher la validation d'un paiement."""

    paiement_id: UUID


@dataclass(frozen=True)
class CommandeRembourserPaiement:
    """Données nécessaires pour demander le remboursement d'un paiement."""

    paiement_id: UUID


# ─── Cas d'usage ─────────────────────────────────────────────────────────────


class InitierPaiementUseCase:
    """Crée un nouveau paiement et le persiste au statut EN_ATTENTE.

    Valide les règles métier (montant, devise) via le service domaine,
    puis crée et sauvegarde l'entité Paiement.
    """

    def __init__(
        self,
        repository: IPaiementRepository,
        domain_service: PaiementDomainService,
    ) -> None:
        # Injection des dépendances via les ports (pas d'implémentation concrète)
        self._repository = repository
        self._domain_service = domain_service

    def executer(
        self, commande: CommandeInitierPaiement
    ) -> tuple[Paiement, EvenementDomaine]:
        """Exécute la création d'un paiement.

        Args:
            commande: Les paramètres du paiement à créer.

        Returns:
            Un tuple (paiement créé, événement PaiementInitie).

        Raises:
            ValueError: Si les paramètres violent les règles métier.
        """
        # 1. Validation des invariants métier avant toute création
        self._domain_service.valider_parametres_creation(
            commande.montant, commande.devise
        )

        # 2. Construction de l'entité (la devise est normalisée en majuscules)
        paiement = Paiement(
            reservation_id=commande.reservation_id,
            montant=commande.montant,
            devise=commande.devise.upper(),
            methode=commande.methode,
        )

        # 3. Persistance via le port repository
        self._repository.sauvegarder(paiement)

        # 4. Émission de l'événement domaine
        evenement = PaiementInitie(paiement_id=paiement.id)
        return paiement, evenement


class ValiderPaiementUseCase:
    """Soumet un paiement EN_ATTENTE au PSP et met à jour son statut.

    Si le PSP accepte → statut VALIDE + événement PaiementValide.
    Si le PSP refuse  → statut REFUSE + événement PaiementRefuse.
    """

    def __init__(
        self,
        repository: IPaiementRepository,
        fournisseur: IFournisseurPaiement,
    ) -> None:
        self._repository = repository
        self._fournisseur = fournisseur

    def executer(
        self, commande: CommandeValiderPaiement
    ) -> tuple[Paiement, EvenementDomaine]:
        """Exécute la validation d'un paiement via le fournisseur externe.

        Args:
            commande: L'identifiant du paiement à valider.

        Returns:
            Un tuple (paiement mis à jour, événement émis).

        Raises:
            ValueError: Si le paiement est introuvable.
        """
        # 1. Récupération du paiement (lever une erreur explicite si absent)
        paiement = self._repository.obtenir_par_id(commande.paiement_id)
        if paiement is None:
            raise ValueError(f"Paiement '{commande.paiement_id}' introuvable.")

        # 2. Appel au port fournisseur (adaptateur externe : Stripe, PayPal…)
        succes = self._fournisseur.traiter(paiement)

        # 3. Transition d'état selon la réponse du PSP
        if succes:
            paiement.valider()
            evenement: EvenementDomaine = PaiementValide(paiement_id=paiement.id)
        else:
            paiement.refuser()
            evenement = PaiementRefuse(
                paiement_id=paiement.id,
                raison="Refusé par le fournisseur de paiement.",
            )

        # 4. Persistance de l'état mis à jour
        self._repository.sauvegarder(paiement)
        return paiement, evenement


class RembourserPaiementUseCase:
    """Rembourse un paiement VALIDE via le PSP.

    Vérifie l'éligibilité métier, contacte le PSP et met à jour
    l'entité au statut REMBOURSE.
    """

    def __init__(
        self,
        repository: IPaiementRepository,
        fournisseur: IFournisseurPaiement,
        domain_service: PaiementDomainService,
    ) -> None:
        self._repository = repository
        self._fournisseur = fournisseur
        self._domain_service = domain_service

    def executer(
        self, commande: CommandeRembourserPaiement
    ) -> tuple[Paiement, EvenementDomaine]:
        """Exécute le remboursement d'un paiement.

        Args:
            commande: L'identifiant du paiement à rembourser.

        Returns:
            Un tuple (paiement remboursé, événement PaiementRembourse).

        Raises:
            ValueError: Si le paiement est introuvable, non remboursable,
                        ou si le PSP refuse le remboursement.
        """
        # 1. Récupération du paiement
        paiement = self._repository.obtenir_par_id(commande.paiement_id)
        if paiement is None:
            raise ValueError(f"Paiement '{commande.paiement_id}' introuvable.")

        # 2. Vérification de l'éligibilité via le service domaine
        if not self._domain_service.est_remboursable(paiement):
            raise ValueError(
                f"Le paiement au statut '{paiement.statut.value}' n'est pas "
                "remboursable. Seuls les paiements VALIDES peuvent l'être."
            )

        # 3. Demande de remboursement au PSP
        succes = self._fournisseur.rembourser(paiement)
        if not succes:
            raise ValueError("Le fournisseur de paiement a refusé le remboursement.")

        # 4. Transition d'état et persistance
        paiement.rembourser()
        self._repository.sauvegarder(paiement)

        evenement = PaiementRembourse(paiement_id=paiement.id)
        return paiement, evenement


class ObtenirPaiementUseCase:
    """Récupère un paiement par son identifiant unique."""

    def __init__(self, repository: IPaiementRepository) -> None:
        self._repository = repository

    def executer(self, paiement_id: UUID) -> Paiement:
        """Retourne le paiement correspondant à l'identifiant.

        Args:
            paiement_id: UUID du paiement recherché.

        Returns:
            L'entité Paiement.

        Raises:
            ValueError: Si aucun paiement ne correspond à cet identifiant.
        """
        paiement = self._repository.obtenir_par_id(paiement_id)
        if paiement is None:
            raise ValueError(f"Paiement '{paiement_id}' introuvable.")
        return paiement
