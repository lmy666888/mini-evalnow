import os
from datetime import datetime, timedelta, timezone

import jwt

from app.models.user import User, UserRole
from app.security import create_access_token, hash_password


def create_user(testing_session_local, role: UserRole) -> User:
    with testing_session_local() as db:
        user = User(
            email=f"{role.value.lower()}@example.com",
            password_hash=hash_password("rbac-test-password"),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)
        return user


def bearer_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_rbac_endpoint_requires_token(auth_client):
    client, _ = auth_client

    response = client.get("/rbac/student")

    assert response.status_code == 401


def test_rbac_endpoint_rejects_invalid_token(auth_client):
    client, _ = auth_client

    response = client.get(
        "/rbac/student",
        headers=bearer_header("not-a-jwt"),
    )

    assert response.status_code == 401


def test_rbac_endpoint_rejects_expired_token(auth_client):
    client, _ = auth_client
    token = create_access_token(
        user_id=1,
        role="STUDENT",
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get("/rbac/student", headers=bearer_header(token))

    assert response.status_code == 401


def test_rbac_endpoint_rejects_invalid_subject(auth_client):
    client, _ = auth_client
    token = jwt.encode(
        {
            "sub": "not-a-user-id",
            "role": "STUDENT",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        os.environ["JWT_SECRET_KEY"],
        algorithm=os.environ["JWT_ALGORITHM"],
    )

    response = client.get("/rbac/student", headers=bearer_header(token))

    assert response.status_code == 401


def test_rbac_endpoint_rejects_missing_user(auth_client):
    client, _ = auth_client
    token = create_access_token(user_id=999, role="STUDENT")

    response = client.get("/rbac/student", headers=bearer_header(token))

    assert response.status_code == 401


def test_student_can_only_access_student_endpoint(auth_client):
    client, testing_session_local = auth_client
    user = create_user(testing_session_local, UserRole.STUDENT)
    token = create_access_token(user.id, user.role.value)
    headers = bearer_header(token)

    student_response = client.get("/rbac/student", headers=headers)
    faculty_response = client.get("/rbac/faculty", headers=headers)
    admin_response = client.get("/rbac/admin", headers=headers)

    assert student_response.status_code == 200
    assert student_response.json()["role"] == "STUDENT"
    assert faculty_response.status_code == 403
    assert admin_response.status_code == 403


def test_faculty_can_access_faculty_endpoint(auth_client):
    client, testing_session_local = auth_client
    user = create_user(testing_session_local, UserRole.FACULTY)
    token = create_access_token(user.id, user.role.value)

    response = client.get("/rbac/faculty", headers=bearer_header(token))

    assert response.status_code == 200
    assert response.json()["role"] == "FACULTY"


def test_admin_can_access_admin_endpoint(auth_client):
    client, testing_session_local = auth_client
    user = create_user(testing_session_local, UserRole.ADMIN)
    token = create_access_token(user.id, user.role.value)

    response = client.get("/rbac/admin", headers=bearer_header(token))

    assert response.status_code == 200
    assert response.json()["role"] == "ADMIN"


def test_rbac_uses_database_role_instead_of_token_claim(auth_client):
    client, testing_session_local = auth_client
    user = create_user(testing_session_local, UserRole.STUDENT)
    token = create_access_token(user.id, role="ADMIN")

    response = client.get("/rbac/admin", headers=bearer_header(token))

    assert response.status_code == 403
