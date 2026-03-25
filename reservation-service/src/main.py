# main.py
from fastapi import FastAPI
from adapters.category.category_controller import create_category_controller
from application.category.use_case import CategoryUseCase
from infrastructure.category.category_repository_impl import CategoryRepositoryImpl

app = FastAPI(title="Reservation API")

repository = CategoryRepositoryImpl()
use_case = CategoryUseCase(repository)

app.include_router(
    create_category_controller(use_case),
    prefix="/categories",
    tags=["Categories"] 
)