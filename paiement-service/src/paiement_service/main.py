"""
Point d'entrée du service de paiement.

Initialise l'application FastAPI, instancie les adaptateurs secondaires
et enregistre le routeur des paiements avec injection de dépendances.

Sélection du repository (variable d'environnement USE_DATABASE) :
    USE_DATABASE=true  → PaiementRepositoryMySQL  (production)
    USE_DATABASE=false → PaiementRepositoryEnMemoire (défaut / tests)

Architecture hexagonale :
    - Les adaptateurs secondaires (repository, fournisseur) sont créés ici.
    - Ils sont injectés dans le routeur via creer_router().
    - Le domaine et les use cases ne connaissent jamais ces implémentations.
"""

import os

from fastapi import FastAPI

from paiement_service.adapters.http_controller import creer_router
from paiement_service.adapters.payment_provider import FournisseurPaiementSimule
from paiement_service.adapters.repository import PaiementRepositoryEnMemoire
from paiement_service.application.ports import IPaiementRepository

app = FastAPI(
    title="paiement_microservice",
    version="0.1.0",
    description="Service de gestion des paiements — Architecture Hexagonale",
)


def build_status() -> dict[str, str]:
    """Generate API status response.

    Returns:
        Dict containing the API status.
    """
    return {"status": "paiement-service"}


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint returning API health status.

    Returns:
        Dict with status information.
    """
    return build_status()


# ─── Composition root ─────────────────────────────────────────────────────────
# Sélection du repository selon la configuration d'environnement.
# USE_DATABASE=true active le repository MySQL (production).
# Par défaut, le repository en mémoire est utilisé (développement / tests).


def _creer_repository() -> IPaiementRepository:
    """Instancie le repository adapté à l'environnement courant."""
    if os.getenv("USE_DATABASE", "false").lower() == "true":
        from paiement_service.infrastructure.repository import (  # noqa: PLC0415
            paiement_repository_mysql as _mysql,
        )

        return _mysql.PaiementRepositoryMySQL()
    return PaiementRepositoryEnMemoire()


_repository = _creer_repository()
_fournisseur = FournisseurPaiementSimule()

# Enregistrement du routeur avec les dépendances injectées
app.include_router(creer_router(_repository, _fournisseur))
