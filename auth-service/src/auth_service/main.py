from fastapi import FastAPI

from auth_service.infrastructure.api.routes import router as auth_router
from auth_service.infrastructure.database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service API",
    version="0.1.0",
    description="Service d'authentification avec JWT",
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "auth-service"}


@app.get("/health")
def health():
    return {"status": "healthy"}
