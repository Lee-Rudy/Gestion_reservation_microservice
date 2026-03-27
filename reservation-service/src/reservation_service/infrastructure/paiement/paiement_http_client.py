"""
Adaptateur HTTP vers le paiement-service.

Rôle dans l'hexagone :
    Implémentation concrète du port PaiementServicePort.
    Communique avec le paiement-service via des appels HTTP (httpx).

Variable d'environnement :
    PAIEMENT_SERVICE_URL : URL de base du paiement-service
                           (défaut : http://localhost:8004)
"""

import os

import httpx

from reservation_service.application.saga.paiement_port import PaiementServicePort

# URL du paiement-service, configurable via variable d'environnement.
# En Docker : PAIEMENT_SERVICE_URL=http://paiement-service:8004
PAIEMENT_SERVICE_URL = os.getenv("PAIEMENT_SERVICE_URL", "http://localhost:8004")


class PaiementHttpClient(PaiementServicePort):
    """Appelle le paiement-service via HTTP.

    Chaque méthode crée une requête synchrone avec un timeout de 10s
    pour éviter de bloquer indéfiniment le saga en cas de défaillance
    du paiement-service.
    """

    def creer_paiement(
        self,
        reservation_id: int,
        montant: str,
        devise: str,
        methode: str,
    ) -> dict:
        """POST /paiements/ — crée un paiement EN_ATTENTE.

        Raises:
            httpx.HTTPStatusError: Si le paiement-service retourne une
                                   erreur HTTP (4xx, 5xx).
            httpx.TimeoutException: Si le service ne répond pas dans les
                                    délais impartis.
        """
        response = httpx.post(
            f"{PAIEMENT_SERVICE_URL}/paiements/",
            json={
                "reservation_id": reservation_id,
                "montant": montant,
                "devise": devise,
                "methode": methode,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def valider_paiement(self, paiement_id: str) -> dict:
        """POST /paiements/{id}/valider — soumet le paiement au PSP.

        Raises:
            httpx.HTTPStatusError: Si le paiement-service retourne une
                                   erreur HTTP (4xx, 5xx).
            httpx.TimeoutException: Si le service ne répond pas dans les
                                    délais impartis.
        """
        response = httpx.post(
            f"{PAIEMENT_SERVICE_URL}/paiements/{paiement_id}/valider",
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
