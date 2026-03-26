import time

import jwt
import pytest

from auth_service.infrastructure.security.token_service import (
    ALGORITHM,
    SECRET_KEY,
    JWTTokenService,
)


def test_create_access_token_returns_valid_jwt():
    service = JWTTokenService()
    data = {"sub": "test@example.com", "role": "USER"}

    token = service.create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0


def test_decode_token_returns_correct_data():
    service = JWTTokenService()
    data = {"sub": "test@example.com", "role": "ADMIN"}

    token = service.create_access_token(data)
    decoded = service.decode_token(token)

    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "ADMIN"
    assert "exp" in decoded


def test_decode_invalid_token_raises_exception():
    service = JWTTokenService()
    invalid_token = "invalid.token.here"

    with pytest.raises(jwt.InvalidTokenError):
        service.decode_token(invalid_token)


def test_decode_expired_token_raises_exception():
    service = JWTTokenService()
    data = {"sub": "test@example.com", "exp": int(time.time()) - 100}

    expired_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(jwt.ExpiredSignatureError):
        service.decode_token(expired_token)
