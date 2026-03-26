from fastapi import FastAPI

from user_service.infrastructure.api.routes import router as user_router
from user_service.infrastructure.database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Service API",
    version="0.1.0",
    description="Service de gestion des utilisateurs (CRUD complet)",
)

app.include_router(user_router)


@app.get("/")
def root():
    return {"status": "user-service"}


@app.get("/health")
def health():
    return {"status": "healthy"}
