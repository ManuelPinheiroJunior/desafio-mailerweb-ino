from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.domain.entities import Booking
from app.domain.enums import OutboxEventType, OutboxStatus
from app.domain.services import OutboxPayloadFactory
from app.infrastructure.orm.models.outbox_event_model import OutboxEventModel


class SqlAlchemyOutboxPublisher:
    def __init__(self, session: Session) -> None:
        self.session = session

    def publish_booking_event(
        self,
        event_type: OutboxEventType,
        booking: Booking,
        room_name: str,
    ) -> None:
        idempotency_key = f"booking:{booking.id}:{event_type.value}:{booking.version}"
        payload = OutboxPayloadFactory.build_booking_payload(
            event_type=event_type,
            booking=booking,
            room_name=room_name,
        )
        event = OutboxEventModel(
            id=uuid4(),
            aggregate_type="BOOKING",
            aggregate_id=booking.id,
            event_type=event_type,
            payload_json=payload,
            status=OutboxStatus.PENDING,
            attempt_count=0,
            max_attempts=5,
            next_retry_at=datetime.now(UTC),
            idempotency_key=idempotency_key,
        )
        self.session.add(event)
