from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.infrastructure.orm.models.base_mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RoomModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "rooms"
    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_rooms_capacity_positive"),
    )

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    bookings = relationship("BookingModel", back_populates="room")
