from abc import ABC, abstractmethod
from typing import Optional

from auth_service.domain.entities import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass


class PasswordHasherPort(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass


class TokenServicePort(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str:
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        pass
