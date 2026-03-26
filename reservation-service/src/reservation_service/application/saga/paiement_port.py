"""
Port abstrait vers le service de paiement.

Rôle dans l'hexagone :
    Interface secondaire (driven side) que le Saga utilise pour
    communiquer avec le paiement-service.
    Le saga ne connaît jamais l'implémentation concrète (HTTP, mock…).
"""

from abc import ABC, abstractmethod


class PaiementServicePort(ABC):
    """Interface vers le paiement-service.

    Toute implémentation concrète (HTTP, mock pour les tests) doit
    hériter de cette classe et implémenter les deux méthodes.
    """

    @abstractmethod
    def creer_paiement(
        self,
        reservation_id: int,
        montant: str,
        devise: str,
        methode: str,
    ) -> dict:
        """Crée un paiement en statut EN_ATTENTE.

        Args:
            reservation_id: ID de la réservation associée.
            montant: Montant sous forme de chaîne (ex: "150.00").
            devise: Code ISO 4217 (ex: "EUR").
            methode: Méthode de paiement (carte, virement, paypal).

        Returns:
            Dict contenant au minimum {"id": "<paiement_uuid>"}.
        """
        pass

    @abstractmethod
    def valider_paiement(self, paiement_id: str) -> dict:
        """Soumet un paiement au PSP et retourne son nouveau statut.

        Args:
            paiement_id: UUID du paiement à valider.

        Returns:
            Dict contenant au minimum {"statut": "valide" | "refuse"}.
        """
        pass
