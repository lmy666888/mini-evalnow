from fastapi import APIRouter, Depends

from app.auth import require_roles
from app.models.user import User, UserRole
from app.schemas import UserResponse


router = APIRouter(prefix="/rbac", tags=["role-based authorization"])


@router.get("/student", response_model=UserResponse)
def read_student_resource(
    current_user: User = Depends(require_roles(UserRole.STUDENT)),
) -> User:
    return current_user


@router.get("/faculty", response_model=UserResponse)
def read_faculty_resource(
    current_user: User = Depends(require_roles(UserRole.FACULTY)),
) -> User:
    return current_user


@router.get("/admin", response_model=UserResponse)
def read_admin_resource(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> User:
    return current_user
