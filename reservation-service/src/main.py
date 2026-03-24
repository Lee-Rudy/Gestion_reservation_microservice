# main.py
from fastapi import FastAPI
from adapters.category.category_controller import create_category_controller
from application.category.use_case import CategoryUseCase
from infrastructure.category.category_repository_impl import CategoryRepositoryImpl

app = FastAPI()

# wiring (hexagonal)
repository = CategoryRepositoryImpl()
use_case = CategoryUseCase(repository)

# register route
app.include_router(create_category_controller(use_case))