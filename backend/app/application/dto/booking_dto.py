from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import BookingStatus


@dataclass(frozen=True)
class BookingDTO:
    id: UUID
    title: str
    room_id: UUID
    organizer_user_id: UUID
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    participants: list[str]
    version: int
