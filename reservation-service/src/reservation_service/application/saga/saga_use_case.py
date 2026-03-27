"""
Saga : orchestration Réservation + Paiement.

Pattern Saga (choreography simplifiée) :
    1. Créer la réservation  → statut PENDING
    2. Calculer le montant   → via QuoteService
    3. Créer le paiement     → appel paiement-service
    4. Valider le paiement   → appel paiement-service (PSP)
    5a. Succès PSP           → réservation CONFIRMED
    5b. Échec PSP            → rollback : réservation CANCELLED
    5c. Erreur inattendue    → rollback : réservation CANCELLED

Garantie de cohérence : quoi qu'il arrive après l'étape 1,
la réservation ne reste jamais en PENDING indéfiniment.
"""

from reservation_service.application.reservation.quote_service import QuoteService
from reservation_service.application.saga.paiement_port import PaiementServicePort
from reservation_service.domain.reservation.reservation import Reservation
from reservation_service.domain.reservation.reservation_service import (
    ReservationService,
)


class SagaReservationPaiementUseCase:
    """Orchestre la création d'une réservation et son paiement.

    Injecte le service de réservation, le port paiement et le
    repository catégorie (nécessaire pour calculer le montant via
    le QuoteService).
    """

    def __init__(
        self,
        reservation_service: ReservationService,
        paiement_service: PaiementServicePort,
        category_repository,  # duck-typing : find_by_id(id) → category
    ):
        self.reservation_service = reservation_service
        self.paiement_service = paiement_service
        # QuoteService calcule le montant à partir de la catégorie
        self.quote_service = QuoteService()
        self.category_repository = category_repository

    def executer(
        self,
        reservation: Reservation,
        devise: str,
        methode: str,
    ) -> dict:
        """Exécute la saga complète et retourne le résultat final.

        Args:
            reservation: Entité Reservation à créer (sans id).
            devise: Code ISO 4217 pour le paiement (ex: "EUR").
            methode: Méthode de paiement (carte, virement, paypal).

        Returns:
            Dict résumant l'état final de la réservation et du paiement.

        Raises:
            ValueError: Si la réservation n'est pas disponible,
                        si la catégorie est inconnue, ou si une
                        erreur réseau survient (après rollback).
        """

        # ── Étape 1 : Créer la réservation (statut PENDING) ──────────────
        # La disponibilité est vérifiée par ReservationService.
        reservation = self.reservation_service.create_reservation(reservation)
        assert (
            reservation.id is not None
        ), "Reservation.id should not be None after save"

        try:
            # ── Étape 2 : Calculer le montant via le QuoteService ─────────
            # On récupère le nom de la catégorie pour le calcul tarifaire.
            category = self.category_repository.find_by_id(reservation.category_id)
            if not category:
                raise ValueError(f"Catégorie {reservation.category_id} introuvable.")
            quote = self.quote_service.generate_quote(reservation, category.name)
            montant = str(quote["amount"])

            # ── Étape 3 : Créer le paiement EN_ATTENTE ───────────────────
            paiement = self.paiement_service.creer_paiement(
                reservation_id=reservation.id,
                montant=montant,
                devise=devise,
                methode=methode,
            )
            paiement_id = paiement["id"]

            # ── Étape 4 : Soumettre au PSP ───────────────────────────────
            paiement_valide = self.paiement_service.valider_paiement(paiement_id)
            paiement_statut = paiement_valide["statut"]

            # ── Étape 5a : Succès → confirmer la réservation ─────────────
            if paiement_statut == "valide":
                self.reservation_service.confirm_reservation(reservation.id)
                return {
                    "reservation_id": reservation.id,
                    "reservation_status": "CONFIRMED",
                    "paiement_id": paiement_id,
                    "paiement_status": paiement_statut,
                    "montant": montant,
                    "devise": devise,
                }

            # ── Étape 5b : PSP refuse → rollback (annuler la réservation)
            self.reservation_service.cancel_reservation(reservation.id)
            return {
                "reservation_id": reservation.id,
                "reservation_status": "CANCELLED",
                "paiement_id": paiement_id,
                "paiement_status": paiement_statut,
                "montant": montant,
                "devise": devise,
            }

        except ValueError:
            # ── Étape 5c : Erreur métier → rollback ──────────────────────
            # On propage l'erreur après avoir annulé la réservation.
            self.reservation_service.cancel_reservation(reservation.id)
            raise

        except Exception as e:
            # ── Étape 5c : Erreur inattendue (réseau…) → rollback ────────
            self.reservation_service.cancel_reservation(reservation.id)
            raise ValueError(
                f"Saga échouée, réservation {reservation.id} annulée : {e}"
            )
