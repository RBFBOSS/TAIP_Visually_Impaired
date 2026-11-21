from typing import TYPE_CHECKING
from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.enums import ApprovalStatus

if TYPE_CHECKING:
    from app.models.documents import Document, DocumentSection
    from app.models.reviews import ReviewLog, FsrsState


class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    document: Mapped["Document"] = relationship(back_populates="decks")
    flashcards: Mapped[list["Flashcard"]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Flashcard(Base):
    __tablename__ = "flashcards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("decks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status", create_type=False),
        default=ApprovalStatus.DRAFT,
        nullable=False,
        index=True,
    )
    validated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
    )
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    deck: Mapped["Deck"] = relationship(back_populates="flashcards")
    citations: Mapped[list["Citation"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    review_logs: Mapped[list["ReviewLog"]] = relationship(
        back_populates="flashcard",
        passive_deletes=True,
    )
    fsrs_states: Mapped[list["FsrsState"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Citation(Base):
    __tablename__ = "citations"
    __table_args__ = (
        CheckConstraint("page_number IS NULL OR page_number > 0", name="ck_citations_page_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flashcard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_sections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int | None] = mapped_column(Integer)
    source_excerpt: Mapped[str] = mapped_column(Text, nullable=False)

    flashcard: Mapped["Flashcard"] = relationship(back_populates="citations")
    section: Mapped["DocumentSection"] = relationship(back_populates="citations")