"""
Événements domaine liés au cycle de vie d'un paiement.

Les événements domaine permettent de notifier les autres composants
d'un changement d'état sans créer de couplage direct entre eux.
Chaque événement est immuable et horodaté.
"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EvenementDomaine:
    """Classe de base pour tous les événements domaine.

    Attributes:
        paiement_id: Identifiant du paiement concerné.
        survenu_a: Horodatage UTC de l'événement.
    """

    paiement_id: UUID
    survenu_a: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class PaiementInitie(EvenementDomaine):
    """Émis lorsqu'un nouveau paiement est créé avec le statut EN_ATTENTE."""

    pass


@dataclass(frozen=True)
class PaiementValide(EvenementDomaine):
    """Émis lorsqu'un paiement est accepté par le fournisseur de paiement."""

    pass


@dataclass(frozen=True)
class PaiementRefuse(EvenementDomaine):
    """Émis lorsqu'un paiement est rejeté par le fournisseur de paiement.

    Attributes:
        raison: Motif du refus fourni par le fournisseur.
    """

    raison: str = ""


@dataclass(frozen=True)
class PaiementRembourse(EvenementDomaine):
    """Émis lorsqu'un paiement validé est remboursé avec succès."""

    pass
