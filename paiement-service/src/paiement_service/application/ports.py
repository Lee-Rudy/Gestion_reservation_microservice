"""
Ports (interfaces) de la couche application.

En architecture hexagonale, les ports définissent les contrats
que les adaptateurs externes doivent implémenter.
Ils permettent d'inverser les dépendances : le domaine ne dépend
jamais des détails d'infrastructure, c'est l'infrastructure qui
s'adapte au domaine.

Deux types de ports :
    - Port primaire (driving) : piloté par l'extérieur → HTTP, CLI…
    - Port secondaire (driven) : piloté par le domaine → BDD, PSP…
      C'est ce second type qui est défini ici.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from paiement_service.domain.entities.paiement import Paiement


class IPaiementRepository(ABC):
    """Port secondaire de persistance des paiements.

    Définit les opérations de lecture/écriture sans dépendre
    d'un moteur de stockage concret (PostgreSQL, Redis, mémoire…).
    """

    @abstractmethod
    def sauvegarder(self, paiement: Paiement) -> None:
        """Insère ou met à jour un paiement dans le stockage.

        Args:
            paiement: L'entité à persister.
        """
        ...

    @abstractmethod
    def obtenir_par_id(self, paiement_id: UUID) -> Paiement | None:
        """Retourne le paiement correspondant à l'identifiant.

        Args:
            paiement_id: UUID du paiement recherché.

        Returns:
            L'entité Paiement si trouvée, None sinon.
        """
        ...

    @abstractmethod
    def lister_tous(self) -> list[Paiement]:
        """Retourne la liste complète des paiements stockés.

        Returns:
            Liste de toutes les entités Paiement.
        """
        ...


class IFournisseurPaiement(ABC):
    """Port secondaire vers le fournisseur de paiement externe (PSP).

    Isole le domaine des détails d'intégration avec les APIs tierces
    (Stripe, PayPal, Adyen…). En changeant l'adaptateur, on change
    de PSP sans toucher au domaine ni aux cas d'usage.
    """

    @abstractmethod
    def traiter(self, paiement: Paiement) -> bool:
        """Soumet un paiement au PSP pour autorisation et capture.

        Args:
            paiement: Le paiement à traiter.

        Returns:
            True si le PSP accepte la transaction, False s'il la refuse.
        """
        ...

    @abstractmethod
    def rembourser(self, paiement: Paiement) -> bool:
        """Demande l'annulation et le remboursement d'une transaction.

        Args:
            paiement: Le paiement précédemment validé à rembourser.

        Returns:
            True si le remboursement est accepté par le PSP, False sinon.
        """
        ...
