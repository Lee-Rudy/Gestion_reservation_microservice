from typing import List, Optional

from sqlalchemy.orm import Session

from user_service.domain.entities import User, UserRole
from user_service.domain.ports import UserRepositoryPort
from user_service.infrastructure.database.models import UserModel


class SQLAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, user_id: int) -> Optional[User]:
        user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            return None
        return self._to_entity(user_model)

    def find_by_email(self, email: str) -> Optional[User]:
        user_model = (
            self.session.query(UserModel).filter(UserModel.email == email).first()
        )
        if not user_model:
            return None
        return self._to_entity(user_model)

    def find_all(self) -> List[User]:
        user_models = self.session.query(UserModel).all()
        return [self._to_entity(um) for um in user_models]

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

    def update(self, user: User) -> User:
        user_model = self.session.query(UserModel).filter(UserModel.id == user.id).first()
        if not user_model:
            raise ValueError("User not found")

        user_model.name = user.name
        user_model.email = user.email
        user_model.password_hash = user.password_hash
        user_model.role = user.role.value

        self.session.commit()
        self.session.refresh(user_model)
        return self._to_entity(user_model)

    def delete(self, user_id: int) -> bool:
        user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            return False

        self.session.delete(user_model)
        self.session.commit()
        return True

    def _to_entity(self, user_model: UserModel) -> User:
        return User(
            id=user_model.id,
            name=user_model.name,
            email=user_model.email,
            password_hash=user_model.password_hash,
            role=UserRole(user_model.role),
            created_at=user_model.created_at,
        )
