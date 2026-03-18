from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateBookingCommand:
    title: str
    room_id: UUID
    organizer_user_id: UUID
    start_at: datetime
    end_at: datetime
    participants: list[str]
