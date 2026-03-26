from auth_service.domain.entities import User, UserRole
from auth_service.domain.ports import PasswordHasherPort, TokenServicePort, UserRepositoryPort


class DummyUserRepository(UserRepositoryPort):
    def find_by_email(self, email: str):
        return super().find_by_email(email)

    def save(self, user: User):
        return super().save(user)


class DummyPasswordHasher(PasswordHasherPort):
    def hash_password(self, password: str) -> str:
        return super().hash_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return super().verify_password(plain_password, hashed_password)


class DummyTokenService(TokenServicePort):
    def create_access_token(self, data: dict) -> str:
        return super().create_access_token(data)

    def decode_token(self, token: str) -> dict:
        return super().decode_token(token)


def test_ports_default_methods_are_noops():
    repo = DummyUserRepository()
    hasher = DummyPasswordHasher()
    token_service = DummyTokenService()

    user = User(name="A", email="a@a.com", password_hash="h", role=UserRole.USER)
    assert repo.find_by_email("a@a.com") is None
    assert repo.save(user) is None
    assert hasher.hash_password("x") is None
    assert hasher.verify_password("x", "y") is None
    assert token_service.create_access_token({"sub": "x"}) is None
    assert token_service.decode_token("token") is None
