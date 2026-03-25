class ReservationUseCase:
    def __init__(self, reservation_service):
        self.reservation_service = reservation_service

    def create_reservation(self, reservation_data):
        return self.reservation_service.create_reservation(reservation_data)

    def get_reservation_by_id(self, id):
        return self.reservation_service.get_reservation(id)

    def update_reservation(self, id, reservation_data):
        return self.reservation_service.update_reservation(id, reservation_data)

    def delete_reservation(self, id):
        return self.reservation_service.delete_reservation(id)