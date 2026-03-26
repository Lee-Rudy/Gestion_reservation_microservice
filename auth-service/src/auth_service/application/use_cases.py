from typing import Optional

from auth_service.domain.entities import AuthToken, User
from auth_service.domain.ports import (
    PasswordHasherPort,
    TokenServicePort,
    UserRepositoryPort,
)


class LoginUseCase:
    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ):
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_service = token_service

    def execute(self, email: str, password: str) -> Optional[AuthToken]:
        user = self.user_repository.find_by_email(email)
        if not user:
            return None

        if not self.password_hasher.verify_password(password, user.password_hash):
            return None

        token = self.token_service.create_access_token(
            {"sub": user.email, "role": user.role.value}
        )
        return AuthToken(access_token=token)


class VerifyTokenUseCase:
    def __init__(self, token_service: TokenServicePort):
        self.token_service = token_service

    def execute(self, token: str) -> Optional[dict]:
        try:
            return self.token_service.decode_token(token)
        except Exception:
            return None
