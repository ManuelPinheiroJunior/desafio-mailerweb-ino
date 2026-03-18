from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import BookingStatus
from app.infrastructure.orm.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class BookingModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("start_at < end_at", name="ck_bookings_start_before_end"),
        Index("ix_bookings_room_time_window", "room_id", "start_at", "end_at"),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    room_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("rooms.id"), nullable=False, index=True)
    organizer_user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False, index=True
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status"),
        nullable=False,
        default=BookingStatus.ACTIVE,
    )
    version: Mapped[int] = mapped_column(nullable=False, default=1)

    room = relationship("RoomModel", back_populates="bookings")
    organizer = relationship("UserModel", back_populates="bookings")
    participants = relationship(
        "BookingParticipantModel",
        back_populates="booking",
        cascade="all, delete-orphan",
    )
