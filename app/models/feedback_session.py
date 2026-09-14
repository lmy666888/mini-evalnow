from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, Identity, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.user import User


class FeedbackSessionStatus(str, Enum):
    AWAITING_BOTH = "AWAITING_BOTH"
    AWAITING_STUDENT = "AWAITING_STUDENT"
    AWAITING_FACULTY = "AWAITING_FACULTY"
    UNLOCKED = "UNLOCKED"


class FeedbackSession(Base):
    __tablename__ = "feedback_sessions"
    __table_args__ = (
        CheckConstraint(
            "student_id <> faculty_id",
            name="ck_feedback_sessions_distinct_participants",
        ),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    faculty_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    status: Mapped[FeedbackSessionStatus] = mapped_column(
        SQLAlchemyEnum(
            FeedbackSessionStatus,
            name="feedback_session_status",
            validate_strings=True,
        ),
        nullable=False,
        default=FeedbackSessionStatus.AWAITING_BOTH,
        server_default=FeedbackSessionStatus.AWAITING_BOTH.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    student: Mapped[User] = relationship(foreign_keys=[student_id])
    faculty: Mapped[User] = relationship(foreign_keys=[faculty_id])
