from datetime import UTC, datetime

from app.domain.entities import Booking
from app.domain.enums import OutboxEventType


class OutboxPayloadFactory:
    @staticmethod
    def build_booking_payload(
        event_type: OutboxEventType,
        booking: Booking,
        room_name: str,
    ) -> dict:
        return {
            "event_type": event_type.value,
            "occurred_at": datetime.now(UTC).isoformat(),
            "aggregate_type": "BOOKING",
            "booking": {
                "id": str(booking.id),
                "title": booking.title,
                "status": booking.status.value,
                "room_id": str(booking.room_id),
                "room_name": room_name,
                "organizer_user_id": str(booking.organizer_user_id),
                "start_at": booking.start_at.isoformat(),
                "end_at": booking.end_at.isoformat(),
                "participants": booking.participants,
                "version": booking.version,
            },
        }
