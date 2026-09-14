import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type
from dotenv import load_dotenv


load_dotenv()

password_hasher = PasswordHasher(type=Type.ID)
JWT_ALGORITHM_KEY_LENGTHS = {"HS256": 32, "HS384": 48, "HS512": 64}


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def _get_jwt_config() -> tuple[str, str, int]:
    secret_key = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM")
    expire_minutes_value = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY is not set")
    if algorithm not in JWT_ALGORITHM_KEY_LENGTHS:
        raise RuntimeError("JWT_ALGORITHM must be HS256, HS384, or HS512")
    if not expire_minutes_value:
        raise RuntimeError("JWT_ACCESS_TOKEN_EXPIRE_MINUTES is not set")

    try:
        expire_minutes = int(expire_minutes_value)
    except ValueError as error:
        raise RuntimeError(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be an integer"
        ) from error

    if expire_minutes <= 0:
        raise RuntimeError("JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive")
    minimum_key_length = JWT_ALGORITHM_KEY_LENGTHS[algorithm]
    if len(secret_key.encode("utf-8")) < minimum_key_length:
        raise RuntimeError(
            f"JWT_SECRET_KEY must be at least {minimum_key_length} bytes for {algorithm}"
        )

    return secret_key, algorithm, expire_minutes


def create_access_token(
    user_id: int,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    secret_key, algorithm, expire_minutes = _get_jwt_config()
    if expires_delta is None:
        expires_delta = timedelta(minutes=expire_minutes)

    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": str(user_id), "role": role, "exp": expires_at}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    secret_key, algorithm, _ = _get_jwt_config()
    return jwt.decode(
        token,
        secret_key,
        algorithms=[algorithm],
        options={"require": ["sub", "exp"]},
    )
