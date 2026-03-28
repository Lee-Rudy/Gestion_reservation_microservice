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

        category_lower = category_name.lower()

        if "hotel" in category_lower or "hôtel" in category_lower:
            nights = (end - start).days
            if nights == 0:
                nights = 1
            amount = nights * 120

        elif "restaurant" in category_lower:
            amount = reservation.nb_persons * 50

        elif "salle" in category_lower or "conference" in category_lower:
            hours = (end - start).total_seconds() / 3600
            if hours == 0:
                hours = 1
            amount = hours * 200

        else:
            raise ValueError(f"Catégorie inconnue: {category_name}")

        return {
            "reservation_id": reservation.id,
            "amount": round(amount, 2),
            "currency": "EUR",
        }
