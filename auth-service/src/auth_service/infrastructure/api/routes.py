import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth_service.application.use_cases import LoginUseCase, VerifyTokenUseCase
from auth_service.domain.entities import User, UserRole
from auth_service.infrastructure.database.database import SessionLocal
from auth_service.infrastructure.database.repository import SQLAlchemyUserRepository
from auth_service.infrastructure.security.password_hasher import BcryptPasswordHasher
from auth_service.infrastructure.security.token_service import JWTTokenService

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

USER_SERVICE_URL = "http://user-service:8002"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenVerifyResponse(BaseModel):
    email: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_repository = SQLAlchemyUserRepository(db)
    password_hasher = BcryptPasswordHasher()
    token_service = JWTTokenService()

    user = user_repository.find_by_email(form_data.username)
    
    if not user:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{USER_SERVICE_URL}/users/by-email/{form_data.username}")
                if response.status_code == 200:
                    user_data = response.json()
                    
                    if password_hasher.verify_password(form_data.password, user_data["password_hash"]):
                        token = token_service.create_access_token(
                            {"sub": user_data["email"], "role": user_data["role"]}
                        )
                        return TokenResponse(access_token=token, token_type="bearer")
        except Exception:
            pass
    
    use_case = LoginUseCase(user_repository, password_hasher, token_service)
    result = use_case.execute(form_data.username, form_data.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=result.access_token, token_type="bearer")


@router.get("/verify", response_model=TokenVerifyResponse)
def verify_token(token: str = Depends(oauth2_scheme)):
    token_service = JWTTokenService()
    use_case = VerifyTokenUseCase(token_service)
    payload = use_case.execute(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenVerifyResponse(email=payload["sub"], role=payload["role"])
