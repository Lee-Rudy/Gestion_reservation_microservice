from typing import List, Optional

from user_service.domain.entities import User, UserRole
from user_service.domain.ports import PasswordHasherPort, UserRepositoryPort


class CreateUserUseCase:
    def __init__(
        self, user_repository: UserRepositoryPort, password_hasher: PasswordHasherPort
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(
        self, name: str, email: str, password: str, role: UserRole = UserRole.USER
    ) -> Optional[User]:
        existing = self.user_repository.find_by_email(email)
        if existing:
            return None

        password_hash = self.password_hasher.hash_password(password)
        user = User(
            name=name, email=email, password_hash=password_hash, role=role
        )
        return self.user_repository.save(user)


class GetUserUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> Optional[User]:
        return self.user_repository.find_by_id(user_id)


class GetAllUsersUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self) -> List[User]:
        return self.user_repository.find_all()


class UpdateUserUseCase:
    def __init__(
        self, user_repository: UserRepositoryPort, password_hasher: PasswordHasherPort
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher

    def execute(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[UserRole] = None,
    ) -> Optional[User]:
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None

        if name:
            user.name = name
        if email:
            user.email = email
        if password:
            user.password_hash = self.password_hasher.hash_password(password)
        if role:
            user.role = role

        return self.user_repository.update(user)


class DeleteUserUseCase:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> bool:
        return self.user_repository.delete(user_id)
