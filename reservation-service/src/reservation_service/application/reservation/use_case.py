from reservation_service.application.reservation.quote_service import QuoteService


class ReservationUseCase:
    def __init__(self, reservation_service, category_repository):
        self.reservation_service = reservation_service
        self.quote_service = QuoteService()
        self.category_repository = category_repository

    def create_reservation(self, reservation_data):
        return self.reservation_service.create_reservation(reservation_data)

    def get_reservation_by_id(self, id):
        return self.reservation_service.get_reservation(id)

    def update_reservation(self, id, reservation_data):
        return self.reservation_service.update_reservation(id, reservation_data)

    def delete_reservation(self, id):
        return self.reservation_service.delete_reservation(id)

    def generate_quote(self, id: int):
        reservation = self.reservation_service.get_reservation(id)
        if not reservation:
            raise ValueError("Reservation not found")

        category = self.category_repository.find_by_id(reservation.category_id)
        category_name = category.name if category else None
        if not category:
            raise ValueError("Category not found")

        return self.quote_service.generate_quote(reservation, category_name)
