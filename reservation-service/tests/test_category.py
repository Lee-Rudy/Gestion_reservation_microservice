"""
Tests unitaires de la couche Category.

Couvre :
    - Entité Category (validations du domaine)
    - CategoryUseCase (orchestration via repo mock)
    - CategoryController (endpoints HTTP via TestClient)
"""

from typing import Optional
from unittest.mock import MagicMock

import importlib

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from reservation_service.application.category.use_case import CategoryUseCase
from reservation_service.domain.category.category import Category
from reservation_service.domain.category.category_repository import CategoryRepository


# ─── Repository in-memory ─────────────────────────────────────────────────────


class CategoryRepositoryInMemory(CategoryRepository):
    """Repository in-memory pour les tests — pas de connexion MySQL."""

    def __init__(self):
        self._store: dict[int, Category] = {}
        self._next_id = 1

    def save(self, category: Category) -> Category:
        category.id = self._next_id
        self._next_id += 1
        self._store[category.id] = category
        return category

    def find_by_id(self, id: int) -> Optional[Category]:
        return self._store.get(id)

    def find_all(self) -> list:
        return list(self._store.values())

    def update(self, id: int, category: Category) -> Optional[Category]:
        if id not in self._store:
            return None
        category.id = id
        self._store[id] = category
        return category

    def delete(self, id: int) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _build_client() -> TestClient:
    """Crée un TestClient FastAPI avec un repo in-memory.

    On recharge le module contrôleur pour obtenir un APIRouter vierge :
    le router est défini au niveau module chez Christina, donc partagé
    entre tous les appels. Sans reload, les routes MySQL enregistrées
    par main.py au démarrage prendraient la priorité.
    """
    import reservation_service.adapters.category.category_controller as mod

    importlib.reload(mod)
    app = FastAPI()
    repo = CategoryRepositoryInMemory()
    use_case = CategoryUseCase(repo)
    app.include_router(mod.create_category_controller(use_case))
    return TestClient(app)


# ─── Tests : entité Category ──────────────────────────────────────────────────


class TestCategoryEntity:
    def test_creation_valide(self):
        """Une catégorie avec un nom valide doit être créée correctement."""
        c = Category(name="hotel", description="Hôtels")
        assert c.name == "hotel"
        assert c.description == "Hôtels"

    def test_nom_vide_leve_erreur(self):
        with pytest.raises(ValueError, match="requis"):
            Category(name="", description="desc")

    def test_nom_trop_court_leve_erreur(self):
        with pytest.raises(ValueError, match="3 caractères"):
            Category(name="ab", description="desc")

    def test_nom_trop_long_leve_erreur(self):
        with pytest.raises(ValueError, match="100 caractères"):
            Category(name="a" * 101, description="desc")

    def test_description_longue_leve_erreur(self):
        with pytest.raises(ValueError, match="100 caractères"):
            Category(name="hotel", description="x" * 101)

    def test_description_none_acceptee(self):
        """Une description None doit être acceptée (champ optionnel)."""
        c = Category(name="hotel", description=None)
        assert c.description == ""


# ─── Tests : CategoryUseCase ──────────────────────────────────────────────────


class TestCategoryUseCase:
    def setup_method(self):
        self.repo = CategoryRepositoryInMemory()
        self.uc = CategoryUseCase(self.repo)

    def test_create_category(self):
        c = Category(name="hotel", description="desc")
        result = self.uc.create_category(c)
        assert result.id is not None

    def test_get_category_by_id(self):
        c = self.uc.create_category(Category(name="hotel", description="desc"))
        found = self.uc.get_category_by_id(c.id)
        assert found.name == "hotel"

    def test_get_category_by_id_inexistant(self):
        assert self.uc.get_category_by_id(999) is None

    def test_get_all_categories(self):
        self.uc.create_category(Category(name="hotel", description="d"))
        self.uc.create_category(Category(name="salle", description="d"))
        assert len(self.uc.get_all_categories()) == 2

    def test_update_category(self):
        c = self.uc.create_category(Category(name="hotel", description="desc"))
        updated = self.uc.update_category(c.id, Category(name="salle", description="d"))
        assert updated.name == "salle"

    def test_delete_category(self):
        c = self.uc.create_category(Category(name="hotel", description="desc"))
        result = self.uc.delete_category(c.id)
        assert result is True
        assert self.uc.get_category_by_id(c.id) is None


# ─── Tests : CategoryController (HTTP) ────────────────────────────────────────


class TestCategoryController:
    def setup_method(self):
        self.client = _build_client()

    def test_create_retourne_201(self):
        r = self.client.post("/categories", json={"name": "hotel", "description": "d"})
        assert r.status_code == 201
        assert r.json()["name"] == "hotel"

    def test_create_nom_invalide_retourne_400(self):
        r = self.client.post("/categories", json={"name": "ab", "description": "d"})
        assert r.status_code == 400

    def test_get_all_retourne_liste(self):
        self.client.post("/categories", json={"name": "hotel", "description": "d"})
        r = self.client.get("/categories")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_get_by_id_existant(self):
        created = self.client.post(
            "/categories", json={"name": "hotel", "description": "d"}
        ).json()
        r = self.client.get(f"/categories/{created['id']}")
        assert r.status_code == 200
        assert r.json()["name"] == "hotel"

    def test_get_by_id_inexistant_retourne_404(self):
        r = self.client.get("/categories/9999")
        assert r.status_code == 404

    def test_update_existant(self):
        created = self.client.post(
            "/categories", json={"name": "hotel", "description": "d"}
        ).json()
        r = self.client.put(
            f"/categories/{created['id']}",
            json={"name": "salle", "description": "d"},
        )
        assert r.status_code == 200
        assert r.json()["name"] == "salle"

    def test_update_inexistant_retourne_404(self):
        r = self.client.put(
            "/categories/9999", json={"name": "hotel", "description": "d"}
        )
        assert r.status_code == 404

    def test_delete_existant_retourne_204(self):
        created = self.client.post(
            "/categories", json={"name": "hotel", "description": "d"}
        ).json()
        r = self.client.delete(f"/categories/{created['id']}")
        assert r.status_code == 204

    def test_delete_inexistant_retourne_404(self):
        r = self.client.delete("/categories/9999")
        assert r.status_code == 404
