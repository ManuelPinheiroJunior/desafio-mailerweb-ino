from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.infrastructure.orm.models.base_mixins import UUIDPrimaryKeyMixin


class EmailDeliveryModel(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "email_deliveries"
    __table_args__ = (
        UniqueConstraint("outbox_event_id", "recipient_email", name="uq_email_delivery_recipient"),
    )

    outbox_event_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("outbox_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_email: Mapped[str] = mapped_column(String(320), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    outbox_event = relationship("OutboxEventModel", back_populates="email_deliveries")
