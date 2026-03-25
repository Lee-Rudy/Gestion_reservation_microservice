"""
Adaptateur de persistance en mémoire pour les paiements.

Implémente le port IPaiementRepository avec un simple dictionnaire Python.
Avantages : aucune dépendance externe, démarrage instantané, idéal pour
les tests et les démonstrations.
Limites : les données sont perdues à chaque redémarrage du service.

En production, cet adaptateur serait remplacé par une implémentation
PostgreSQL, MongoDB ou autre sans toucher au domaine ni aux use cases.
"""

from uuid import UUID

from paiement_service.application.ports import IPaiementRepository
from paiement_service.domain.entities.paiement import Paiement


class PaiementRepositoryEnMemoire(IPaiementRepository):
    """Repository in-memory implémentant le port IPaiementRepository.

    Stocke les paiements dans un dictionnaire UUID → Paiement.
    Thread-safety non garantie (suffisant pour le contexte du TP).
    """

    def __init__(self) -> None:
        # Dictionnaire servant de store : clé = UUID du paiement
        self._paiements: dict[UUID, Paiement] = {}

    def sauvegarder(self, paiement: Paiement) -> None:
        """Insère ou écrase le paiement dans le store en mémoire.

        Args:
            paiement: L'entité à persister.
        """
        self._paiements[paiement.id] = paiement

    def obtenir_par_id(self, paiement_id: UUID) -> Paiement | None:
        """Recherche un paiement par son UUID.

        Args:
            paiement_id: L'identifiant du paiement recherché.

        Returns:
            L'entité Paiement si présente, None sinon.
        """
        return self._paiements.get(paiement_id)

    def lister_tous(self) -> list[Paiement]:
        """Retourne une copie de la liste de tous les paiements stockés.

        Returns:
            Liste de toutes les entités Paiement.
        """
        return list(self._paiements.values())
