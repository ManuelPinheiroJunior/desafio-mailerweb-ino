from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.enums import BookingStatus
from app.domain.exceptions import BookingAlreadyCanceledError, BookingPermissionDeniedError
from app.domain.value_objects import BookingTimeWindow


@dataclass
class Booking:
    id: UUID
    title: str
    room_id: UUID
    organizer_user_id: UUID
    start_at: datetime
    end_at: datetime
    status: BookingStatus = BookingStatus.ACTIVE
    participants: list[str] = field(default_factory=list)
    version: int = 1

    def assert_can_be_modified_by(self, actor_user_id: UUID, actor_is_admin: bool = False) -> None:
        if actor_is_admin:
            return
        if self.organizer_user_id != actor_user_id:
            raise BookingPermissionDeniedError("Only organizer or admin can modify the booking.")

    def apply_schedule_update(
        self,
        title: str,
        room_id: UUID,
        time_window: BookingTimeWindow,
        participants: list[str],
    ) -> None:
        if self.status == BookingStatus.CANCELED:
            raise BookingAlreadyCanceledError("Canceled bookings cannot be updated.")
        self.title = title
        self.room_id = room_id
        self.start_at = time_window.start_at
        self.end_at = time_window.end_at
        self.participants = participants
        self.version += 1

    def cancel(self) -> None:
        if self.status == BookingStatus.CANCELED:
            raise BookingAlreadyCanceledError("Booking is already canceled.")
        self.status = BookingStatus.CANCELED
        self.version += 1
