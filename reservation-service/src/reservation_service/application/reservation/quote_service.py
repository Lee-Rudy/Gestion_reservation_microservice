from datetime import datetime


class QuoteService:

    def generate_quote(self, reservation, category_name: str):

        start = reservation.start_date
        end = reservation.end_date

        # sécurité si c’est string
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)

        if category_name == "hotel":
            nights = (end - start).days
            if nights == 0:
                nights = 1  # Minimum 1 nuit
            amount = nights * 100

        elif category_name == "restaurant":
            amount = reservation.nb_persons * 20

        elif category_name == "salle":
            hours = (end - start).total_seconds() / 3600
            amount = hours * 50

        else:
            raise ValueError("Catégorie inconnue")

        return {
            "reservation_id": reservation.id,
            "amount": round(amount, 2),
            "currency": "EUR",
        }
