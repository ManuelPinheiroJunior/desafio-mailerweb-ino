from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.exceptions import InvalidBookingTimeError

MIN_BOOKING_DURATION = timedelta(minutes=15)
MAX_BOOKING_DURATION = timedelta(hours=8)


@dataclass(frozen=True)
class BookingTimeWindow:
    start_at: datetime
    end_at: datetime

    @staticmethod
    def create(start_at: datetime, end_at: datetime) -> "BookingTimeWindow":
        if start_at.tzinfo is None or end_at.tzinfo is None:
            raise InvalidBookingTimeError("start_at and end_at must include timezone.")

        if start_at >= end_at:
            raise InvalidBookingTimeError("start_at must be lower than end_at.")

        duration = end_at - start_at
        if duration < MIN_BOOKING_DURATION:
            raise InvalidBookingTimeError("Booking duration must be at least 15 minutes.")
        if duration > MAX_BOOKING_DURATION:
            raise InvalidBookingTimeError("Booking duration must be at most 8 hours.")

        return BookingTimeWindow(start_at=start_at, end_at=end_at)
