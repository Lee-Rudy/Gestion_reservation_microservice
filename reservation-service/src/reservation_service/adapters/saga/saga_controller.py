"""
Contrôleur HTTP pour le Saga Réservation + Paiement.

Endpoint exposé :
    POST /reservations/saga
        → Crée une réservation et déclenche le paiement en une seule
          opération. Retourne l'état final (CONFIRMED ou CANCELLED).

Le montant est calculé automatiquement par le QuoteService selon la
catégorie (hotel, restaurant, salle). Le client fournit uniquement
la méthode de paiement et la devise.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from reservation_service.application.saga.saga_use_case import (
    SagaReservationPaiementUseCase,
)
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_status import ReservationStatus

router = APIRouter()


class SagaRequest(BaseModel):
    """Corps JSON attendu pour déclencher le Saga."""

    # Données de la réservation
    user_email: str
    category_id: int
    start_date: str
    end_date: str
    nb_persons: int = 1

    # Données du paiement
    devise: str = "EUR"
    methode: str = "carte"


def create_saga_controller(use_case: SagaReservationPaiementUseCase):
    """Fabrique le routeur du Saga avec injection de dépendances.

    Suit le même pattern factory que les autres contrôleurs de Christina
    (create_reservation_controller, create_category_controller).
    """

    @router.post("/reservations/saga", status_code=201)
    def run_saga(request: SagaRequest):
        """Déclenche le Saga : crée la réservation et traite le paiement.

        Réponse 201 : réservation CONFIRMED (paiement accepté)
        Réponse 201 : réservation CANCELLED (paiement refusé par le PSP)
        Réponse 400 : dates invalides, disponibilité, catégorie inconnue
        Réponse 503 : paiement-service injoignable
        """
        try:
            # Construction de l'entité Reservation (id=None → INSERT)
            reservation = Reservation(
                id=None,
                user_email=request.user_email,
                category_id=request.category_id,
                start_date=request.start_date,
                end_date=request.end_date,
                status=ReservationStatus.PENDING,
                nb_persons=request.nb_persons,
            )

            # Exécution du Saga
            result = use_case.executer(
                reservation=reservation,
                devise=request.devise,
                methode=request.methode,
            )
            return result

        except ValueError as e:
            # Erreurs métier : disponibilité, dates, catégorie inconnue
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            # Erreur réseau ou inattendue (paiement-service down…)
            raise HTTPException(
                status_code=503,
                detail=f"Service de paiement indisponible : {e}",
            )

    return router
