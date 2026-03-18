from datetime import UTC, datetime, timedelta

import pytest

from app.domain.exceptions import InvalidBookingTimeError
from app.domain.value_objects import BookingTimeWindow


def test_booking_time_window_requires_timezone() -> None:
    start_at = datetime(2026, 3, 17, 9, 0, 0)
    end_at = datetime(2026, 3, 17, 10, 0, 0, tzinfo=UTC)

    with pytest.raises(InvalidBookingTimeError):
        BookingTimeWindow.create(start_at=start_at, end_at=end_at)


def test_booking_time_window_rejects_duration_lower_than_15_minutes() -> None:
    start_at = datetime(2026, 3, 17, 9, 0, 0, tzinfo=UTC)
    end_at = start_at + timedelta(minutes=14)

    with pytest.raises(InvalidBookingTimeError):
        BookingTimeWindow.create(start_at=start_at, end_at=end_at)


def test_booking_time_window_rejects_duration_greater_than_8_hours() -> None:
    start_at = datetime(2026, 3, 17, 9, 0, 0, tzinfo=UTC)
    end_at = start_at + timedelta(hours=8, minutes=1)

    with pytest.raises(InvalidBookingTimeError):
        BookingTimeWindow.create(start_at=start_at, end_at=end_at)


def test_booking_time_window_accepts_boundaries_15_minutes_and_8_hours() -> None:
    start_at = datetime(2026, 3, 17, 9, 0, 0, tzinfo=UTC)
    BookingTimeWindow.create(start_at=start_at, end_at=start_at + timedelta(minutes=15))
    BookingTimeWindow.create(start_at=start_at, end_at=start_at + timedelta(hours=8))
