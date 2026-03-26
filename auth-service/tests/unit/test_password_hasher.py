import pytest

from auth_service.infrastructure.security.password_hasher import BcryptPasswordHasher


def test_hash_password_returns_different_from_plain():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"
    hashed = hasher.hash_password(password)

    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_with_correct_password():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"
    hashed = hasher.hash_password(password)

    assert hasher.verify_password(password, hashed) is True


def test_verify_password_with_incorrect_password():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"
    hashed = hasher.hash_password(password)

    assert hasher.verify_password("WrongPassword", hashed) is False


def test_hash_password_generates_unique_hashes():
    hasher = BcryptPasswordHasher()
    password = "MySecurePassword123!"

    hash1 = hasher.hash_password(password)
    hash2 = hasher.hash_password(password)

    assert hash1 != hash2
    assert hasher.verify_password(password, hash1) is True
    assert hasher.verify_password(password, hash2) is True
