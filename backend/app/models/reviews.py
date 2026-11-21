from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.enums import FsrsCardState, RecallRating, SessionStatus

if TYPE_CHECKING:
    from app.models.learning import Flashcard

class ReviewSession(Base):
    __tablename__ = "review_sessions"
    __table_args__ = (
        CheckConstraint("ended_at IS NULL OR ended_at >= started_at", name="ck_review_sessions_time_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status", create_type=False),
        default=SessionStatus.ACTIVE,
        nullable=False,
    )

    logs: Mapped[list["ReviewLog"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ReviewLog(Base):
    __tablename__ = "review_logs"
    __table_args__ = (
        CheckConstraint("response_latency_ms >= 0", name="ck_review_logs_response_latency"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("review_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flashcards.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    rating: Mapped[RecallRating] = mapped_column(
        Enum(RecallRating, name="recall_rating", create_type=False),
        nullable=False,
    )
    response_latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    session: Mapped["ReviewSession"] = relationship(back_populates="logs")
    flashcard: Mapped["Flashcard"] = relationship(back_populates="review_logs")


class FsrsState(Base):
    __tablename__ = "fsrs_states"
    __table_args__ = (
        UniqueConstraint("user_id", "flashcard_id", name="uq_fsrs_states_user_flashcard"),
        CheckConstraint("stability IS NULL OR stability >= 0", name="ck_fsrs_states_stability"),
        CheckConstraint(
            "difficulty IS NULL OR (difficulty >= 0 AND difficulty <= 10)",
            name="ck_fsrs_states_difficulty",
        ),
        CheckConstraint("repetitions >= 0", name="ck_fsrs_states_repetitions"),
        CheckConstraint("lapses >= 0", name="ck_fsrs_states_lapses"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    state: Mapped[FsrsCardState] = mapped_column(
        Enum(FsrsCardState, name="fsrs_card_state", create_type=False),
        default=FsrsCardState.NEW,
        nullable=False,
    )
    stability: Mapped[float | None] = mapped_column(Float)
    difficulty: Mapped[float | None] = mapped_column(Float)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    last_review: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="fsrs_states")