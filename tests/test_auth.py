from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import register_user as register_user_endpoint
from app.models.user import User, UserRole
from app.schemas import UserRegistration
from app.security import decode_access_token, verify_password


REGISTER_DATA = {
    "email": "student@example.com",
    "password": "test-password-123",
}


def register_user(client):
    return client.post("/auth/register", json=REGISTER_DATA)


def login_user(client, password=REGISTER_DATA["password"]):
    return client.post(
        "/auth/login",
        json={"email": REGISTER_DATA["email"], "password": password},
    )


def test_register_creates_user_with_hashed_password(auth_client):
    client, testing_session_local = auth_client

    response = register_user(client)

    assert response.status_code == 201
    assert set(response.json()) == {"id", "email", "role", "created_at"}
    assert response.json()["email"] == REGISTER_DATA["email"]
    assert response.json()["role"] == "STUDENT"
    assert "password_hash" not in response.json()

    with testing_session_local() as db:
        user = db.scalar(select(User).where(User.email == REGISTER_DATA["email"]))
        assert user is not None
        assert user.role is UserRole.STUDENT
        assert user.password_hash != REGISTER_DATA["password"]
        assert verify_password(REGISTER_DATA["password"], user.password_hash)


def test_register_rejects_client_controlled_role(auth_client):
    client, testing_session_local = auth_client

    response = client.post(
        "/auth/register",
        json={**REGISTER_DATA, "role": "ADMIN"},
    )

    assert response.status_code == 422
    with testing_session_local() as db:
        assert db.scalar(select(User)) is None


def test_register_rejects_duplicate_email(auth_client):
    client, _ = auth_client
    assert register_user(client).status_code == 201

    response = client.post(
        "/auth/register",
        json={**REGISTER_DATA, "email": "STUDENT@example.com"},
    )

    assert response.status_code == 409


def test_register_rolls_back_uniqueness_race(monkeypatch):
    monkeypatch.setattr("app.auth.hash_password", lambda password: "password-hash")
    db = Mock(spec=Session)
    db.scalar.return_value = None
    db.commit.side_effect = IntegrityError(
        "INSERT INTO users",
        {},
        Exception("unique constraint violation"),
    )
    registration = UserRegistration(**REGISTER_DATA)

    with pytest.raises(HTTPException) as error:
        register_user_endpoint(registration, db=db)

    assert error.value.status_code == 409
    assert error.value.detail == "Email is already registered"
    db.rollback.assert_called_once_with()


def test_login_returns_bearer_access_token(auth_client):
    client, _ = auth_client
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    payload = decode_access_token(response.json()["access_token"])
    assert payload["sub"]


def test_invalid_logins_return_same_response(auth_client):
    client, _ = auth_client
    register_user(client)

    incorrect_password = login_user(client, password="incorrect-password")
    nonexistent_email = client.post(
        "/auth/login",
        json={"email": "missing@example.com", "password": "incorrect-password"},
    )

    assert incorrect_password.status_code == 401
    assert nonexistent_email.status_code == 401
    assert incorrect_password.json() == nonexistent_email.json()


def test_me_returns_current_user(auth_client):
    client, _ = auth_client
    registered_user = register_user(client).json()
    access_token = login_user(client).json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == registered_user
    assert "password_hash" not in response.json()


def test_me_requires_bearer_token(auth_client):
    client, _ = auth_client

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_rejects_invalid_token(auth_client):
    client, _ = auth_client

    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )

    assert response.status_code == 401
