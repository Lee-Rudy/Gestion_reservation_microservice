from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from user_service.application.use_cases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetAllUsersUseCase,
    GetUserUseCase,
    UpdateUserUseCase,
)
from user_service.domain.entities import UserRole
from user_service.infrastructure.database.database import SessionLocal
from user_service.infrastructure.database.repository import SQLAlchemyUserRepository
from user_service.infrastructure.security.password_hasher import BcryptPasswordHasher

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class UserWithPasswordResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    password_hash: str

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    hasher = BcryptPasswordHasher()
    use_case = CreateUserUseCase(repository, hasher)

    user = use_case.execute(
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà",
        )

    return UserResponse(
        id=user.id, name=user.name, email=user.email, role=user.role.value
    )


@router.get("/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    use_case = GetAllUsersUseCase(repository)
    users = use_case.execute()

    return [
        UserResponse(id=u.id, name=u.name, email=u.email, role=u.role.value)
        for u in users
    ]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    use_case = GetUserUseCase(repository)
    user = use_case.execute(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    return UserResponse(
        id=user.id, name=user.name, email=user.email, role=user.role.value
    )


@router.get("/by-email/{email}", response_model=UserWithPasswordResponse, include_in_schema=False)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    user = repository.find_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    return UserWithPasswordResponse(
        id=user.id, 
        name=user.name, 
        email=user.email, 
        role=user.role.value,
        password_hash=user.password_hash
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    hasher = BcryptPasswordHasher()
    use_case = UpdateUserUseCase(repository, hasher)

    user = use_case.execute(
        user_id=user_id,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    return UserResponse(
        id=user.id, name=user.name, email=user.email, role=user.role.value
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    repository = SQLAlchemyUserRepository(db)
    use_case = DeleteUserUseCase(repository)

    success = use_case.execute(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé"
        )

    return None
