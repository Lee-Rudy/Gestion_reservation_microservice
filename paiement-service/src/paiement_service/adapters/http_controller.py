"""
Adaptateur HTTP — Contrôleur FastAPI pour l'API des paiements.

Rôle dans l'hexagone :
    Adaptateur primaire (driving side) : reçoit les requêtes HTTP,
    les traduit en commandes applicatives, puis renvoie les résultats
    sous forme de réponses HTTP.

Ce contrôleur ne contient aucune logique métier. Il délègue entièrement
aux cas d'usage et se limite à :
    - Valider les données d'entrée (Pydantic)
    - Convertir les commandes → use cases
    - Mapper les entités → schémas de réponse
    - Traduire les erreurs domaine en codes HTTP appropriés

Endpoints exposés :
    POST   /paiements/              → Initier un paiement
    POST   /paiements/{id}/valider  → Valider via le PSP
    POST   /paiements/{id}/rembourser → Rembourser
    GET    /paiements/{id}          → Lire un paiement
"""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from paiement_service.application.ports import IFournisseurPaiement, IPaiementRepository
from paiement_service.application.use_cases import (
    CommandeInitierPaiement,
    CommandeRembourserPaiement,
    CommandeValiderPaiement,
    InitierPaiementUseCase,
    ObtenirPaiementUseCase,
    RembourserPaiementUseCase,
    ValiderPaiementUseCase,
)
from paiement_service.domain.entities.paiement import (
    MethodePaiement,
    Paiement,
    StatutPaiement,
)
from paiement_service.domain.services.paiement_service import PaiementDomainService


# ─── Schémas Pydantic (DTOs HTTP) ────────────────────────────────────────────


class RequeteInitierPaiement(BaseModel):
    """Corps JSON attendu pour créer un paiement."""

    reservation_id: int = Field(
        ..., description="Identifiant entier de la réservation à payer"
    )
    montant: Decimal = Field(..., gt=0, description="Montant à payer (ex : 49.99)")
    devise: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Code ISO 4217 de la devise (ex : EUR, USD, GBP)",
    )
    methode: MethodePaiement = Field(..., description="Méthode de paiement choisie")


class ReponsePaiement(BaseModel):
    """Représentation JSON d'un paiement renvoyée par l'API."""

    id: UUID
    reservation_id: int
    montant: Decimal
    devise: str
    methode: MethodePaiement
    statut: StatutPaiement


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _vers_reponse(paiement: Paiement) -> ReponsePaiement:
    """Convertit une entité Paiement en schéma de réponse HTTP.

    Sépare la représentation externe (JSON) de la structure interne (entité).
    """
    return ReponsePaiement(
        id=paiement.id,
        reservation_id=paiement.reservation_id,
        montant=paiement.montant,
        devise=paiement.devise,
        methode=paiement.methode,
        statut=paiement.statut,
    )


# ─── Factory du routeur ───────────────────────────────────────────────────────


def creer_router(
    repository: IPaiementRepository,
    fournisseur: IFournisseurPaiement,
) -> APIRouter:
    """Fabrique le routeur FastAPI avec injection des dépendances.

    En recevant les ports en paramètres, le contrôleur reste indépendant
    des implémentations concrètes : en test on injecte un repository
    en mémoire, en production un repository PostgreSQL.

    Args:
        repository: Implémentation du port de persistance.
        fournisseur: Implémentation du port fournisseur PSP.

    Returns:
        Un APIRouter FastAPI configuré avec les quatre endpoints.
    """
    router = APIRouter(prefix="/paiements", tags=["Paiements"])
    domain_service = PaiementDomainService()

    # Instanciation des use cases avec injection des ports
    initier_uc = InitierPaiementUseCase(repository, domain_service)
    valider_uc = ValiderPaiementUseCase(repository, fournisseur)
    rembourser_uc = RembourserPaiementUseCase(repository, fournisseur, domain_service)
    obtenir_uc = ObtenirPaiementUseCase(repository)

    # ── Endpoints ────────────────────────────────────────────────────────────

    @router.post(
        "/",
        response_model=ReponsePaiement,
        status_code=status.HTTP_201_CREATED,
        summary="Initier un paiement",
        description=(
            "Crée un nouveau paiement au statut EN_ATTENTE après validation "
            "des règles métier (montant, devise)."
        ),
    )
    def initier_paiement(requete: RequeteInitierPaiement) -> ReponsePaiement:
        """Crée un paiement en attente de validation."""
        try:
            commande = CommandeInitierPaiement(
                reservation_id=requete.reservation_id,
                montant=requete.montant,
                devise=requete.devise,
                methode=requete.methode,
            )
            paiement, _ = initier_uc.executer(commande)
            return _vers_reponse(paiement)
        except ValueError as e:
            # Erreurs métier → 422 Unprocessable Entity
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

    @router.post(
        "/{paiement_id}/valider",
        response_model=ReponsePaiement,
        summary="Valider un paiement via le PSP",
        description=(
            "Soumet le paiement au fournisseur externe. "
            "Le statut devient VALIDE ou REFUSE selon la réponse du PSP."
        ),
    )
    def valider_paiement(paiement_id: UUID) -> ReponsePaiement:
        """Soumet un paiement EN_ATTENTE au fournisseur de paiement."""
        try:
            commande = CommandeValiderPaiement(paiement_id=paiement_id)
            paiement, _ = valider_uc.executer(commande)
            return _vers_reponse(paiement)
        except ValueError as e:
            # Paiement introuvable → 404 Not Found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    @router.post(
        "/{paiement_id}/rembourser",
        response_model=ReponsePaiement,
        summary="Rembourser un paiement validé",
        description=(
            "Demande le remboursement d'un paiement au statut VALIDE. "
            "Retourne une erreur si le paiement n'est pas remboursable."
        ),
    )
    def rembourser_paiement(paiement_id: UUID) -> ReponsePaiement:
        """Rembourse un paiement VALIDE via le fournisseur de paiement."""
        try:
            commande = CommandeRembourserPaiement(paiement_id=paiement_id)
            paiement, _ = rembourser_uc.executer(commande)
            return _vers_reponse(paiement)
        except ValueError as e:
            # Paiement introuvable ou non remboursable → 422
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

    @router.get(
        "/{paiement_id}",
        response_model=ReponsePaiement,
        summary="Obtenir un paiement",
        description="Récupère le détail complet d'un paiement par son identifiant.",
    )
    def obtenir_paiement(paiement_id: UUID) -> ReponsePaiement:
        """Retourne les informations d'un paiement."""
        try:
            paiement = obtenir_uc.executer(paiement_id)
            return _vers_reponse(paiement)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

    return router
