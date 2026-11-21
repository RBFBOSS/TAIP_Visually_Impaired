from datetime import datetime
import uuid

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base
from app.models.enums import AccountStatus, MentorshipStatus, UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", create_type=False),
        default=UserRole.STUDENT,
        nullable=False,
    )
    status: Mapped[AccountStatus] = mapped_column(
        Enum(AccountStatus, name="account_status", create_type=False),
        default=AccountStatus.ACTIVE,
        nullable=False,
    )
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    verifier: Mapped["User | None"] = relationship(
        remote_side=[id],
        foreign_keys=[verified_by],
    )
    student_links: Mapped[list["StudentValidator"]] = relationship(
        back_populates="student",
        foreign_keys="StudentValidator.student_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    validator_links: Mapped[list["StudentValidator"]] = relationship(
        back_populates="validator",
        foreign_keys="StudentValidator.validator_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class StudentValidator(Base):
    __tablename__ = "student_validators"
    __table_args__ = (
        UniqueConstraint("student_id", "validator_id", name="uq_student_validator_pair"),
        CheckConstraint("student_id <> validator_id", name="ck_sv_different_users"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    validator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[MentorshipStatus] = mapped_column(
        Enum(MentorshipStatus, name="mentorship_status", create_type=False),
        default=MentorshipStatus.PENDING,
        nullable=False,
    )
    initiated_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
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

    student: Mapped["User"] = relationship(
        back_populates="student_links",
        foreign_keys=[student_id],
    )
    validator: Mapped["User"] = relationship(
        back_populates="validator_links",
        foreign_keys=[validator_id],
    )
    initiator: Mapped["User"] = relationship(foreign_keys=[initiated_by])