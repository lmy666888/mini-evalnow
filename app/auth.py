import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas import LoginInput, TokenResponse, UserRegistration, UserResponse
from app.security import create_access_token, decode_access_token, hash_password
from app.security import verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])
bearer_scheme = HTTPBearer(auto_error=False)
_DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-timing-protection")


def authentication_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    registration: UserRegistration,
    db: Session = Depends(get_db),
) -> User:
    email = str(registration.email).lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        email=email,
        password_hash=hash_password(registration.password),
        role=UserRole.STUDENT,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from None

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(login_input: LoginInput, db: Session = Depends(get_db)) -> TokenResponse:
    email = str(login_input.email).lower()
    user = db.scalar(select(User).where(User.email == email))
    password_hash = user.password_hash if user is not None else _DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(login_input.password, password_hash)

    if user is None or not password_is_valid:
        raise authentication_error()

    access_token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=access_token, token_type="bearer")


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise authentication_error()

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload["sub"]
        if not isinstance(subject, str) or not subject.isdigit():
            raise authentication_error()
        user_id = int(subject)
    except (jwt.PyJWTError, KeyError):
        raise authentication_error()

    user = db.get(User, user_id)
    if user is None:
        raise authentication_error()
    return user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
