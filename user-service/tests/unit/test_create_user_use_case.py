from unittest.mock import Mock

import pytest

from user_service.application.use_cases import CreateUserUseCase
from user_service.domain.entities import User, UserRole


def test_create_user_success():
    user_repo = Mock()
    password_hasher = Mock()

    user_repo.find_by_email.return_value = None
    password_hasher.hash_password.return_value = "hashed_password"

    saved_user = User(
        id=1,
        name="Test",
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER,
    )
    user_repo.save.return_value = saved_user

    use_case = CreateUserUseCase(user_repo, password_hasher)
    result = use_case.execute("Test", "test@example.com", "password", UserRole.USER)

    assert result is not None
    assert result.email == "test@example.com"
    user_repo.find_by_email.assert_called_once_with("test@example.com")
    password_hasher.hash_password.assert_called_once_with("password")
    user_repo.save.assert_called_once()


def test_create_user_fails_if_email_exists():
    user_repo = Mock()
    password_hasher = Mock()

    existing_user = User(
        id=1,
        name="Existing",
        email="test@example.com",
        password_hash="hashed",
        role=UserRole.USER,
    )
    user_repo.find_by_email.return_value = existing_user

    use_case = CreateUserUseCase(user_repo, password_hasher)
    result = use_case.execute("Test", "test@example.com", "password")

    assert result is None
    password_hasher.hash_password.assert_not_called()
    user_repo.save.assert_not_called()
