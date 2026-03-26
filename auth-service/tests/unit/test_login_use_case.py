from unittest.mock import Mock

import pytest

from auth_service.application.use_cases import LoginUseCase
from auth_service.domain.entities import User, UserRole


def test_login_success_with_valid_credentials():
    user_repo = Mock()
    password_hasher = Mock()
    token_service = Mock()

    user = User(
        id=1,
        name="Test",
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER,
    )

    user_repo.find_by_email.return_value = user
    password_hasher.verify_password.return_value = True
    token_service.create_access_token.return_value = "fake_jwt_token"

    use_case = LoginUseCase(user_repo, password_hasher, token_service)
    result = use_case.execute("test@example.com", "correct_password")

    assert result is not None
    assert result.access_token == "fake_jwt_token"
    user_repo.find_by_email.assert_called_once_with("test@example.com")
    password_hasher.verify_password.assert_called_once_with(
        "correct_password", "hashed_password"
    )


def test_login_fails_with_nonexistent_user():
    user_repo = Mock()
    password_hasher = Mock()
    token_service = Mock()

    user_repo.find_by_email.return_value = None

    use_case = LoginUseCase(user_repo, password_hasher, token_service)
    result = use_case.execute("nonexistent@example.com", "password")

    assert result is None
    password_hasher.verify_password.assert_not_called()


def test_login_fails_with_invalid_password():
    user_repo = Mock()
    password_hasher = Mock()
    token_service = Mock()

    user = User(
        id=1,
        name="Test",
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.USER,
    )

    user_repo.find_by_email.return_value = user
    password_hasher.verify_password.return_value = False

    use_case = LoginUseCase(user_repo, password_hasher, token_service)
    result = use_case.execute("test@example.com", "wrong_password")

    assert result is None
    token_service.create_access_token.assert_not_called()
