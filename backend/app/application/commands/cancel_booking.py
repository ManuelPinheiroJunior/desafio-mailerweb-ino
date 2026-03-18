from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelBookingCommand:
    booking_id: UUID
    actor_user_id: UUID
    actor_is_admin: bool = False
