from sqlalchemy import DateTime, Enum, Identity, Integer, String

from app.models.base import Base
from app.models.user import User, UserRole


def test_user_table_columns():
    table = User.__table__

    assert table.name == "users"
    assert table.metadata is Base.metadata
    assert set(table.columns.keys()) == {
        "id", "email", "password_hash", "role", "created_at"
    }
    assert all(not column.nullable for column in table.columns)
    assert isinstance(table.c.id.type, Integer)
    assert list(table.primary_key.columns) == [table.c.id]
    assert isinstance(table.c.id.identity, Identity)
    assert isinstance(table.c.email.type, String)
    assert isinstance(table.c.password_hash.type, String)


def test_user_email_has_unique_index():
    email_indexes = [
        index for index in User.__table__.indexes
        if list(index.columns.keys()) == ["email"]
    ]

    assert len(email_indexes) == 1
    assert email_indexes[0].unique is True


def test_user_role_enum():
    role_type = User.__table__.c.role.type

    assert isinstance(role_type, Enum)
    assert role_type.enum_class is UserRole
    assert role_type.enums == ["STUDENT", "FACULTY", "ADMIN"]
    assert {role.value for role in UserRole} == {"STUDENT", "FACULTY", "ADMIN"}
    assert role_type.name == "user_role"
    assert role_type.native_enum is True
    assert role_type.validate_strings is True


def test_user_created_at_has_server_default():
    column = User.__table__.c.created_at

    assert isinstance(column.type, DateTime)
    assert column.type.timezone is True
    assert column.server_default is not None
    assert str(column.server_default.arg) == "now()"
    assert column.default is None
