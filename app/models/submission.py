from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Identity, Text
from sqlalchemy import UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.feedback_session import FeedbackSession
from app.models.user import User


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "author_id",
            name="uq_submissions_session_author",
        ),
        CheckConstraint(
            "length(trim(content)) > 0",
            name="ck_submissions_content_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    session_id: Mapped[int] = mapped_column(
        ForeignKey("feedback_sessions.id"), nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    session: Mapped[FeedbackSession] = relationship()
    author: Mapped[User] = relationship()
