import pytest

from user_service.infrastructure.security.password_hasher import BcryptPasswordHasher


def test_hash_password_returns_different_from_plain():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"
    hashed = hasher.hash_password(password)

    assert hashed != password
    assert len(hashed) > 0


def test_hash_password_generates_unique_hashes():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"

    hash1 = hasher.hash_password(password)
    hash2 = hasher.hash_password(password)

    assert hash1 != hash2
