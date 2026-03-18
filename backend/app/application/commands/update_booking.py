from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UpdateBookingCommand:
    booking_id: UUID
    actor_user_id: UUID
    title: str
    room_id: UUID
    start_at: datetime
    end_at: datetime
    participants: list[str]
    actor_is_admin: bool = False
