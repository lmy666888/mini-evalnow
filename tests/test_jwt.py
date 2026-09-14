from datetime import timedelta

import jwt
import pytest

from app.security import create_access_token, decode_access_token


def test_access_token_contains_subject_and_expiration(jwt_environment):
    token = create_access_token(user_id=42, role="STUDENT")

    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "STUDENT"
    assert "exp" in payload
    assert "password" not in payload
    assert "password_hash" not in payload


def test_expired_access_token_is_rejected(jwt_environment):
    token = create_access_token(
        user_id=42,
        role="STUDENT",
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_malformed_access_token_is_rejected(jwt_environment):
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("not-a-jwt")


def test_tampered_access_token_is_rejected(jwt_environment):
    token = create_access_token(user_id=42, role="STUDENT")
    header, payload, signature = token.split(".")
    first_character = "A" if signature[0] != "A" else "B"
    tampered_token = f"{header}.{payload}.{first_character}{signature[1:]}"

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(tampered_token)
