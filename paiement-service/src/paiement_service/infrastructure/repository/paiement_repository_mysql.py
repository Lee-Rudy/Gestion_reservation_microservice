"""
Adaptateur secondaire — Repository MySQL pour les paiements.

Rôle dans l'hexagone :
    Implémentation concrète du port IPaiementRepository pour MySQL.
    Traduit les entités du domaine en lignes SQL et inversement.
    Le domaine ne connaît jamais cette classe.

Table attendue (voir migrations/paiements.sql) :
    paiements(id CHAR(36), reservation_id CHAR(36), montant DECIMAL(10,2),
              devise CHAR(3), methode VARCHAR(50),
              statut ENUM('en_attente','valide','refuse','rembourse'),
              created_at TIMESTAMP, updated_at TIMESTAMP)
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from paiement_service.application.ports import IPaiementRepository
from paiement_service.domain.entities.paiement import (
    MethodePaiement,
    Paiement,
    StatutPaiement,
)
from paiement_service.infrastructure.database.database import get_connection


class PaiementRepositoryMySQL(IPaiementRepository):
    """Implémentation MySQL de IPaiementRepository.

    Chaque méthode ouvre sa propre connexion et la ferme en fin
    d'appel, ce qui est cohérent avec le pattern utilisé dans les
    autres services du projet (connexion à la demande, pas de pool).
    """

    # ─── Lecture ─────────────────────────────────────────────────────────────

    def obtenir_par_id(self, paiement_id: UUID) -> Optional[Paiement]:
        """Récupère un paiement par son UUID, ou None si absent."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM paiements WHERE id = %s", (str(paiement_id),))
            row = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

        return self._ligne_vers_entite(row) if row else None

    def lister_tous(self) -> list[Paiement]:
        """Retourne tous les paiements stockés."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM paiements ORDER BY created_at DESC")
            rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        return [self._ligne_vers_entite(row) for row in rows]

    # ─── Écriture ─────────────────────────────────────────────────────────────

    def sauvegarder(self, paiement: Paiement) -> None:
        """Insère ou met à jour un paiement (INSERT … ON DUPLICATE KEY UPDATE).

        La clause ON DUPLICATE KEY UPDATE évite de tester l'existence
        en amont et garantit l'atomicité de l'opération.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO paiements
                    (id, reservation_id, montant, devise, methode, statut,
                     created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    statut     = VALUES(statut),
                    updated_at = VALUES(updated_at)
            """
            cursor.execute(
                query,
                (
                    str(paiement.id),
                    str(paiement.reservation_id),
                    str(paiement.montant),
                    paiement.devise,
                    paiement.methode.value,
                    paiement.statut.value,
                    paiement.created_at,
                    paiement.updated_at,
                ),
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    # ─── Helpers privés ───────────────────────────────────────────────────────

    @staticmethod
    def _ligne_vers_entite(row: dict) -> Paiement:
        """Convertit une ligne MySQL (dict) en entité Paiement du domaine.

        Gère la conversion de types :
            CHAR(36)     → UUID
            DECIMAL      → Decimal
            VARCHAR      → MethodePaiement (enum)
            ENUM string  → StatutPaiement (enum)
            TIMESTAMP    → datetime
        """

        # MySQL retourne parfois les TIMESTAMP en str selon le driver version
        def _to_datetime(val: object) -> datetime:
            if isinstance(val, datetime):
                return val
            return datetime.fromisoformat(str(val))

        paiement = Paiement(
            id=UUID(row["id"]),
            reservation_id=UUID(row["reservation_id"]),
            montant=Decimal(str(row["montant"])),
            devise=row["devise"],
            methode=MethodePaiement(row["methode"]),
            statut=StatutPaiement(row["statut"]),
            created_at=_to_datetime(row["created_at"]),
            updated_at=_to_datetime(row["updated_at"]),
        )
        return paiement
