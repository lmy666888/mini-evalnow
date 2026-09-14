from sqlalchemy import CheckConstraint, DateTime, Identity, Integer, Text
from sqlalchemy import UniqueConstraint

from app.models.base import Base
from app.models.submission import Submission


def test_submission_table_columns():
    table = Submission.__table__

    assert table.name == "submissions"
    assert table.metadata is Base.metadata
    assert set(table.columns.keys()) == {
        "id",
        "session_id",
        "author_id",
        "content",
        "submitted_at",
    }
    assert all(not column.nullable for column in table.columns)
    assert isinstance(table.c.id.type, Integer)
    assert list(table.primary_key.columns) == [table.c.id]
    assert isinstance(table.c.id.identity, Identity)
    assert isinstance(table.c.content.type, Text)


def test_submission_foreign_keys_and_relationships():
    table = Submission.__table__

    assert {key.target_fullname for key in table.c.session_id.foreign_keys} == {
        "feedback_sessions.id"
    }
    assert {key.target_fullname for key in table.c.author_id.foreign_keys} == {
        "users.id"
    }
    assert Submission.session.property.local_columns == {table.c.session_id}
    assert Submission.author.property.local_columns == {table.c.author_id}


def test_submission_has_one_submission_per_session_author():
    constraints = {
        constraint.name: constraint
        for constraint in Submission.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    constraint = constraints["uq_submissions_session_author"]
    assert list(constraint.columns.keys()) == ["session_id", "author_id"]


def test_submission_content_cannot_be_blank():
    constraints = {
        constraint.name: constraint
        for constraint in Submission.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    constraint = constraints["ck_submissions_content_not_blank"]
    assert str(constraint.sqltext) == "length(trim(content)) > 0"


def test_submission_submitted_at():
    column = Submission.__table__.c.submitted_at

    assert isinstance(column.type, DateTime)
    assert column.type.timezone is True
    assert column.server_default is not None
    assert str(column.server_default.arg) == "now()"
