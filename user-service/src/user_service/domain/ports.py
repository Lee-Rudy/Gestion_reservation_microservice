from abc import ABC, abstractmethod
from typing import List, Optional

from user_service.domain.entities import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass

    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass


class PasswordHasherPort(ABC):
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass
