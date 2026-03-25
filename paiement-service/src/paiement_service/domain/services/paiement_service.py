"""
Service domaine pour les règles métier transverses du paiement.

Contient les invariants qui ne relèvent pas d'une seule entité :
validation des paramètres d'entrée et éligibilité au remboursement.
"""

from decimal import Decimal

from paiement_service.domain.entities.paiement import Paiement, StatutPaiement


class PaiementDomainService:
    """Service domaine centralisant les règles métier de validation.

    Ce service n'a pas d'état : il ne stocke aucune donnée et ne dépend
    d'aucune infrastructure externe. Il peut être instancié librement.

    Règles métier gérées :
        - Plage de montant autorisée (0.01 → 100 000)
        - Devises acceptées (EUR, USD, GBP)
        - Éligibilité au remboursement (statut VALIDE uniquement)
    """

    MONTANT_MINIMUM: Decimal = Decimal("0.01")
    MONTANT_MAXIMUM: Decimal = Decimal("100000.00")
    DEVISES_ACCEPTEES: frozenset = frozenset({"EUR", "USD", "GBP"})

    def valider_parametres_creation(self, montant: Decimal, devise: str) -> None:
        """Vérifie les règles métier avant la création d'un paiement.

        Args:
            montant: Montant à valider.
            devise: Code devise ISO 4217 à valider (insensible à la casse).

        Raises:
            ValueError: Si le montant est hors plage autorisée.
            ValueError: Si la devise n'est pas acceptée.
        """
        # Vérification de la plage de montant
        if montant < self.MONTANT_MINIMUM:
            raise ValueError(
                f"Le montant {montant} est inférieur au minimum autorisé "
                f"({self.MONTANT_MINIMUM})."
            )
        if montant > self.MONTANT_MAXIMUM:
            raise ValueError(
                f"Le montant {montant} dépasse le maximum autorisé "
                f"({self.MONTANT_MAXIMUM})."
            )

        # Vérification de la devise (normalisation en majuscules)
        if devise.upper() not in self.DEVISES_ACCEPTEES:
            devises_triees = sorted(self.DEVISES_ACCEPTEES)
            raise ValueError(
                f"La devise '{devise}' n'est pas acceptée. "
                f"Devises disponibles : {devises_triees}."
            )

    def est_remboursable(self, paiement: Paiement) -> bool:
        """Détermine si un paiement peut faire l'objet d'un remboursement.

        Seul un paiement au statut VALIDE peut être remboursé.

        Args:
            paiement: Le paiement à évaluer.

        Returns:
            True si le paiement est remboursable, False sinon.
        """
        return paiement.statut == StatutPaiement.VALIDE
