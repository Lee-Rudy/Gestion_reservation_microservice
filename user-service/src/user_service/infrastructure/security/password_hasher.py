import bcrypt

from user_service.domain.ports import PasswordHasherPort


class BcryptPasswordHasher(PasswordHasherPort):
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
