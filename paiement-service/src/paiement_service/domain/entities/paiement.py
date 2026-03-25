"""
Entité centrale du domaine Paiement.

Encapsule l'état et les règles de transition d'un paiement.
Aucune dépendance externe : cette couche est pure logique métier.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class StatutPaiement(Enum):
    """Cycle de vie d'un paiement.

    Transitions autorisées :
        EN_ATTENTE → VALIDE
        EN_ATTENTE → REFUSE
        VALIDE     → REMBOURSE
    """

    EN_ATTENTE = "en_attente"
    VALIDE = "valide"
    REFUSE = "refuse"
    REMBOURSE = "rembourse"


class MethodePaiement(Enum):
    """Modes de paiement acceptés par le service."""

    CARTE = "carte"
    VIREMENT = "virement"
    PAYPAL = "paypal"


@dataclass
class Paiement:
    """Entité Paiement — agrégat racine du domaine.

    Regroupe les données et les règles de transition propres à un paiement.
    L'identifiant est généré automatiquement à la création.

    Attributes:
        reservation_id: Identifiant de la réservation associée.
        montant: Montant à payer (Decimal pour éviter les erreurs de virgule flottante).
        devise: Code ISO 4217 de la devise (ex : EUR, USD, GBP).
        methode: Mode de paiement choisi par le client.
        id: Identifiant unique du paiement (UUID v4, généré automatiquement).
        statut: État courant dans le cycle de vie du paiement.
        created_at: Horodatage de création (UTC).
        updated_at: Horodatage de la dernière modification (UTC).
    """

    reservation_id: UUID
    montant: Decimal
    devise: str
    methode: MethodePaiement
    id: UUID = field(default_factory=uuid4)
    statut: StatutPaiement = field(default=StatutPaiement.EN_ATTENTE)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def valider(self) -> None:
        """Fait passer le paiement au statut VALIDE.

        Seuls les paiements EN_ATTENTE peuvent être validés.

        Raises:
            ValueError: Si le statut courant interdit la validation.
        """
        if self.statut != StatutPaiement.EN_ATTENTE:
            raise ValueError(
                f"Impossible de valider un paiement au statut '{self.statut.value}'. "
                "Seuls les paiements EN_ATTENTE peuvent être validés."
            )
        self.statut = StatutPaiement.VALIDE
        self.updated_at = datetime.utcnow()

    def refuser(self) -> None:
        """Fait passer le paiement au statut REFUSE.

        Seuls les paiements EN_ATTENTE peuvent être refusés.

        Raises:
            ValueError: Si le statut courant interdit le refus.
        """
        if self.statut != StatutPaiement.EN_ATTENTE:
            raise ValueError(
                f"Impossible de refuser un paiement au statut '{self.statut.value}'. "
                "Seuls les paiements EN_ATTENTE peuvent être refusés."
            )
        self.statut = StatutPaiement.REFUSE
        self.updated_at = datetime.utcnow()

    def rembourser(self) -> None:
        """Fait passer le paiement au statut REMBOURSE.

        Seuls les paiements VALIDES peuvent être remboursés.

        Raises:
            ValueError: Si le statut courant interdit le remboursement.
        """
        if self.statut != StatutPaiement.VALIDE:
            raise ValueError(
                f"Impossible de rembourser un paiement au statut "
                f"'{self.statut.value}'. "
                "Seuls les paiements VALIDES peuvent être remboursés."
            )
        self.statut = StatutPaiement.REMBOURSE
        self.updated_at = datetime.utcnow()
