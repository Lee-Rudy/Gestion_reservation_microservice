# adapters/category_controller.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from reservation_service.application.category.use_case import CategoryUseCase
from reservation_service.domain.category.category import Category

router = APIRouter()


class CategoryRequest(BaseModel):
    name: str
    description: str | None = None


def create_category_controller(use_case: CategoryUseCase):

    # CREATE
    @router.post("/categories", status_code=201)
    def create(category_request: CategoryRequest):
        try:
            category_obj = Category(
                name=category_request.name, description=category_request.description
            )
            category = use_case.create_category(category_obj)

            return {
                "id": category.id,
                "name": category.name,
                "description": category.description,
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # READ ALL
    @router.get("/categories")
    def get_all():
        from reservation_service.infrastructure.database.database import get_connection
        
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, description, price_per_day FROM categories")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        return categories

    # READ BY ID
    @router.get("/categories/{id}")
    def get_by_id(id: int):
        category = use_case.get_category_by_id(id)
        if not category:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
        }

    # UPDATE
    @router.put("/categories/{id}")
    def update(id: int, category_request: CategoryRequest):
        try:
            category_obj = Category(
                name=category_request.name, description=category_request.description
            )
            updated = use_case.update_category(id, category_obj)
            if not updated:
                raise HTTPException(status_code=404, detail="Catégorie non trouvée")

            return {
                "id": updated.id,
                "name": updated.name,
                "description": updated.description,
            }

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # DELETE
    @router.delete("/categories/{id}", status_code=204)
    def delete(id: int):
        deleted = use_case.delete_category(id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Catégorie non trouvée")
        return None

    return router
