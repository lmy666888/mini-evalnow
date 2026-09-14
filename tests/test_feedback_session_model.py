from sqlalchemy import CheckConstraint, DateTime, Enum, Identity, Integer

from app.models.base import Base
from app.models.feedback_session import FeedbackSession, FeedbackSessionStatus


def test_feedback_session_table_columns():
    table = FeedbackSession.__table__

    assert table.name == "feedback_sessions"
    assert table.metadata is Base.metadata
    assert set(table.columns.keys()) == {
        "id",
        "student_id",
        "faculty_id",
        "status",
        "created_at",
        "updated_at",
    }
    assert all(not column.nullable for column in table.columns)
    assert isinstance(table.c.id.type, Integer)
    assert list(table.primary_key.columns) == [table.c.id]
    assert isinstance(table.c.id.identity, Identity)


def test_feedback_session_participant_foreign_keys_and_relationships():
    table = FeedbackSession.__table__

    assert {key.target_fullname for key in table.c.student_id.foreign_keys} == {
        "users.id"
    }
    assert {key.target_fullname for key in table.c.faculty_id.foreign_keys} == {
        "users.id"
    }
    assert FeedbackSession.student.property.local_columns == {table.c.student_id}
    assert FeedbackSession.faculty.property.local_columns == {table.c.faculty_id}


def test_feedback_session_status_enum_and_defaults():
    column = FeedbackSession.__table__.c.status

    assert isinstance(column.type, Enum)
    assert column.type.enum_class is FeedbackSessionStatus
    assert column.type.enums == [
        "AWAITING_BOTH",
        "AWAITING_STUDENT",
        "AWAITING_FACULTY",
        "UNLOCKED",
    ]
    assert column.type.name == "feedback_session_status"
    assert column.type.native_enum is True
    assert column.type.validate_strings is True
    assert column.default.arg is FeedbackSessionStatus.AWAITING_BOTH
    assert str(column.server_default.arg) == "AWAITING_BOTH"


def test_feedback_session_timestamps():
    table = FeedbackSession.__table__

    assert isinstance(table.c.created_at.type, DateTime)
    assert table.c.created_at.type.timezone is True
    assert str(table.c.created_at.server_default.arg) == "now()"
    assert isinstance(table.c.updated_at.type, DateTime)
    assert table.c.updated_at.type.timezone is True
    assert str(table.c.updated_at.server_default.arg) == "now()"
    assert str(table.c.updated_at.onupdate.arg) == "now()"


def test_feedback_session_requires_distinct_participants():
    constraints = {
        constraint.name: constraint
        for constraint in FeedbackSession.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    constraint = constraints["ck_feedback_sessions_distinct_participants"]
    assert str(constraint.sqltext) == "student_id <> faculty_id"
