from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from reservation_service.application.reservation.use_case import ReservationUseCase
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_status import ReservationStatus

# Pydantic model avec Enum pour status
class ReservationController(BaseModel):
    user_id: int
    category_id: int
    start_date: str
    end_date: str
    status: ReservationStatus = ReservationStatus.PENDING  # Enum directement
    nb_persons: int = 1  # Nouveau champ pour le nombre de personnes

def create_reservation_controller(use_case: ReservationUseCase):
    router = APIRouter()
    
    # CREATE
    @router.post("/reservations", status_code=201)
    def create(reservation_request: ReservationController):
        try:
            reservation_obj = Reservation(
                id=None,
                user_id=reservation_request.user_id,
                category_id=reservation_request.category_id,
                start_date=reservation_request.start_date,
                end_date=reservation_request.end_date,
                status=reservation_request.status,  # Enum déjà validé par Pydantic
                nb_persons=reservation_request.nb_persons  # Inclure le nombre de personnes
            )
            reservation = use_case.create_reservation(reservation_obj)
            return {
                "id": reservation.id,
                "user_id": reservation.user_id,
                "category_id": reservation.category_id,
                "start_date": reservation.start_date,
                "end_date": reservation.end_date,
                "status": reservation.status.value,  # Retourne le string pour Swagger
                "nb_persons": reservation.nb_persons  # Inclure le nombre de personnes dans la réponse
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # READ BY ID
    @router.get("/reservations/{id}")
    def get_by_id(id: int):
        reservation = use_case.get_reservation_by_id(id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Réservation non trouvée")
        return {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "category_id": reservation.category_id,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "status": reservation.status.value,
            "nb_persons": reservation.nb_persons
        }

    # UPDATE
    @router.put("/reservations/{id}")
    def update(id: int, reservation_request: ReservationController):
        try:
            reservation_obj = Reservation(
                id=id,
                user_id=reservation_request.user_id,
                category_id=reservation_request.category_id,
                start_date=reservation_request.start_date,
                end_date=reservation_request.end_date,
                status=reservation_request.status,
                nb_persons=reservation_request.nb_persons
            )
            updated = use_case.update_reservation(id, reservation_obj)
            if not updated:
                raise HTTPException(status_code=404, detail="Réservation non trouvée")
            return {
                "id": updated.id,
                "user_id": updated.user_id,
                "category_id": updated.category_id,
                "start_date": updated.start_date,
                "end_date": updated.end_date,
                "status": updated.status.value,
                "nb_persons": updated.nb_persons
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # DELETE
    @router.delete("/reservations/{id}", status_code=204)
    def delete(id: int):
        deleted = use_case.delete_reservation(id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Réservation non trouvée")
        return None
    
    # DEVIS
    @router.get("/reservations/{id}/quote")
    def get_quote(id: int):
        try:
            quote = use_case.generate_quote(id)
            return quote
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    # CONFIRMATION
    @router.put("/reservations/{id}/confirm")
    def confirm(id: int):
        reservation = use_case.confirm_reservation(id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Réservation non trouvée")
        return {
            "id": reservation.id,
            "user_id": reservation.user_id,
            "category_id": reservation.category_id,
            "start_date": reservation.start_date,
            "end_date": reservation.end_date,
            "status": reservation.status.value,
            "nb_persons": reservation.nb_persons
        }


    return router