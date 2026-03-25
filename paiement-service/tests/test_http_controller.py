"""
Tests d'intégration du contrôleur HTTP via FastAPI TestClient.

Vérifie l'intégration complète de la stack HTTP → use cases → domaine
en utilisant les adaptateurs in-memory.
Ces tests couvrent les codes de statut, les corps de réponse et
les cas d'erreur HTTP.
"""

from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from paiement_service.adapters.http_controller import creer_router
from paiement_service.adapters.payment_provider import FournisseurPaiementSimule
from paiement_service.adapters.repository import PaiementRepositoryEnMemoire


# ─── Fixtures ────────────────────────────────────────────────────────────────


def _creer_app(
    traitement_accepte: bool = True,
    remboursement_accepte: bool = True,
) -> FastAPI:
    """Crée une application FastAPI isolée avec des adaptateurs frais."""
    app = FastAPI()
    repo = PaiementRepositoryEnMemoire()
    fournisseur = FournisseurPaiementSimule(
        traitement_accepte=traitement_accepte,
        remboursement_accepte=remboursement_accepte,
    )
    app.include_router(creer_router(repo, fournisseur))
    return app


@pytest.fixture
def client() -> TestClient:
    """Client de test avec un PSP qui accepte tout."""
    return TestClient(_creer_app())


@pytest.fixture
def client_psp_ko() -> TestClient:
    """Client de test avec un PSP qui refuse tout."""
    return TestClient(_creer_app(traitement_accepte=False))


@pytest.fixture
def client_remboursement_ko() -> TestClient:
    """Client de test avec un PSP qui refuse les remboursements."""
    return TestClient(_creer_app(remboursement_accepte=False))


def _payload_base(montant: str = "99.99", devise: str = "EUR") -> dict:
    """Corps JSON valide pour créer un paiement."""
    return {
        "reservation_id": str(uuid4()),
        "montant": montant,
        "devise": devise,
        "methode": "carte",
    }


# ─── POST /paiements/ ────────────────────────────────────────────────────────


class TestInitierPaiement:
    def test_retourne_201_avec_statut_en_attente(self, client: TestClient) -> None:
        """Créer un paiement valide doit retourner 201 et statut en_attente."""
        response = client.post("/paiements/", json=_payload_base())
        assert response.status_code == 201
        data = response.json()
        assert data["statut"] == "en_attente"
        assert "id" in data

    def test_retourne_les_valeurs_envoyees(self, client: TestClient) -> None:
        """Les données de la réponse doivent correspondre à la requête."""
        reservation_id = str(uuid4())
        payload = {
            "reservation_id": reservation_id,
            "montant": "150.00",
            "devise": "USD",
            "methode": "paypal",
        }
        response = client.post("/paiements/", json=payload)
        data = response.json()
        assert data["reservation_id"] == reservation_id
        assert data["montant"] == "150.00"
        assert data["devise"] == "USD"
        assert data["methode"] == "paypal"

    def test_devise_normalisee_en_majuscules(self, client: TestClient) -> None:
        """La devise doit être normalisée en majuscules dans la réponse."""
        response = client.post("/paiements/", json=_payload_base(devise="eur"))
        assert response.json()["devise"] == "EUR"

    def test_montant_invalide_retourne_422(self, client: TestClient) -> None:
        """Un montant nul doit retourner 422 Unprocessable Entity."""
        response = client.post("/paiements/", json=_payload_base(montant="0"))
        assert response.status_code == 422

    def test_devise_invalide_retourne_422(self, client: TestClient) -> None:
        """Une devise inconnue doit retourner 422."""
        response = client.post("/paiements/", json=_payload_base(devise="XYZ"))
        assert response.status_code == 422

    def test_corps_manquant_retourne_422(self, client: TestClient) -> None:
        """Une requête sans corps doit retourner 422."""
        response = client.post("/paiements/", json={})
        assert response.status_code == 422


# ─── POST /paiements/{id}/valider ────────────────────────────────────────────


class TestValiderPaiement:
    def _creer_paiement(self, client: TestClient) -> str:
        """Crée un paiement et retourne son UUID."""
        response = client.post("/paiements/", json=_payload_base())
        return response.json()["id"]

    def test_validation_reussie_retourne_statut_valide(
        self, client: TestClient
    ) -> None:
        """Valider avec un PSP OK doit retourner le statut valide."""
        paiement_id = self._creer_paiement(client)
        response = client.post(f"/paiements/{paiement_id}/valider")
        assert response.status_code == 200
        assert response.json()["statut"] == "valide"

    def test_validation_echouee_retourne_statut_refuse(
        self, client_psp_ko: TestClient
    ) -> None:
        """Valider avec un PSP KO doit retourner le statut refuse."""
        paiement_id = self._creer_paiement(client_psp_ko)
        response = client_psp_ko.post(f"/paiements/{paiement_id}/valider")
        assert response.status_code == 200
        assert response.json()["statut"] == "refuse"

    def test_paiement_inexistant_retourne_404(self, client: TestClient) -> None:
        """Valider un UUID inconnu doit retourner 404."""
        response = client.post(f"/paiements/{uuid4()}/valider")
        assert response.status_code == 404


# ─── POST /paiements/{id}/rembourser ─────────────────────────────────────────


class TestRembourserPaiement:
    def _creer_et_valider(self, client: TestClient) -> str:
        """Crée et valide un paiement, retourne son UUID."""
        resp = client.post("/paiements/", json=_payload_base())
        paiement_id = resp.json()["id"]
        client.post(f"/paiements/{paiement_id}/valider")
        return paiement_id

    def test_remboursement_reussi_retourne_statut_rembourse(
        self, client: TestClient
    ) -> None:
        """Un remboursement réussi doit retourner le statut rembourse."""
        paiement_id = self._creer_et_valider(client)
        response = client.post(f"/paiements/{paiement_id}/rembourser")
        assert response.status_code == 200
        assert response.json()["statut"] == "rembourse"

    def test_paiement_inexistant_retourne_422(self, client: TestClient) -> None:
        """Rembourser un UUID inconnu doit retourner 422."""
        response = client.post(f"/paiements/{uuid4()}/rembourser")
        assert response.status_code == 422

    def test_paiement_en_attente_retourne_422(self, client: TestClient) -> None:
        """Rembourser un paiement EN_ATTENTE doit retourner 422."""
        resp = client.post("/paiements/", json=_payload_base())
        paiement_id = resp.json()["id"]
        response = client.post(f"/paiements/{paiement_id}/rembourser")
        assert response.status_code == 422

    def test_psp_refuse_remboursement_retourne_422(
        self, client_remboursement_ko: TestClient
    ) -> None:
        """Si le PSP refuse le remboursement, l'API doit retourner 422."""
        paiement_id = self._creer_et_valider(client_remboursement_ko)
        response = client_remboursement_ko.post(
            f"/paiements/{paiement_id}/rembourser"
        )
        assert response.status_code == 422


# ─── GET /paiements/{id} ─────────────────────────────────────────────────────


class TestObtenirPaiement:
    def test_retourne_le_paiement_existant(self, client: TestClient) -> None:
        """GET sur un UUID existant doit retourner 200 avec les données."""
        resp = client.post("/paiements/", json=_payload_base())
        paiement_id = resp.json()["id"]
        response = client.get(f"/paiements/{paiement_id}")
        assert response.status_code == 200
        assert response.json()["id"] == paiement_id

    def test_paiement_inexistant_retourne_404(self, client: TestClient) -> None:
        """GET sur un UUID inexistant doit retourner 404."""
        response = client.get(f"/paiements/{uuid4()}")
        assert response.status_code == 404
