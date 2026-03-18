from uuid import UUID

from sqlalchemy import ForeignKey, String, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.infrastructure.orm.models.base_mixins import UUIDPrimaryKeyMixin


class BookingParticipantModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "booking_participants"
    __table_args__ = (
        UniqueConstraint("booking_id", "email", name="uq_booking_participant_email"),
    )

    booking_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("bookings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(320), nullable=False)

    booking = relationship("BookingModel", back_populates="participants")
