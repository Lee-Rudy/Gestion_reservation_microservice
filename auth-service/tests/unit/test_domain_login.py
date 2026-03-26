import pytest

from auth_service.domain.login import Login


def test_login_normalizes_email_and_password():
    login = Login("  USER@Example.COM ", "  Abcdef1@  ", id=7)
    assert login.get_id() == 7
    assert login.get_email() == "user@example.com"
    assert login.get_password() == "Abcdef1@"


@pytest.mark.parametrize(
    "email",
    ["", "invalid-email", "invalid@", "invalid.com"],
)
def test_login_rejects_invalid_email(email):
    with pytest.raises(ValueError):
        Login(email, "Abcdef1@")


@pytest.mark.parametrize(
    "password",
    ["", "abcdef", "ABCDEF", "Abcdef", "Abcdef1", "abcdef1@"],
)
def test_login_rejects_invalid_password(password):
    with pytest.raises(ValueError):
        Login("user@example.com", password)


def test_login_rejects_non_string_values():
    with pytest.raises(ValueError):
        Login(123, "Abcdef1@")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        Login("user@example.com", 123)  # type: ignore[arg-type]
