from typing import Optional

from sqlalchemy.orm import Session

from auth_service.domain.entities import User, UserRole
from auth_service.domain.ports import UserRepositoryPort
from auth_service.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def find_by_email(self, email: str) -> Optional[User]:
        user_model = (
            self.session.query(UserModel).filter(UserModel.email == email).first()
        )
        if not user_model:
            return None

        return User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            password_hash=user_model.password_hash,
            role=UserRole(user_model.role),
            created_at=user_model.created_at,
        )

    def save(self, user: User) -> User:
        user_model = UserModel(
            name=user.name,
            email=user.email,
            password_hash=user.password_hash,
            role=user.role.value,
        )
        self.session.add(user_model)
        self.session.commit()
        self.session.refresh(user_model)

        user.id = user_model.id
        user.created_at = user_model.created_at
        return user
