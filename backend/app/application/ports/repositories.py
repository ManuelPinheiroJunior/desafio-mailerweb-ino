from collections.abc import Callable
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities import Booking, OutboxEvent, Room
from app.domain.enums import OutboxEventType


class BookingRepository(Protocol):
    def add(self, booking: Booking) -> None: ...

    def save(self, booking: Booking) -> None: ...

    def get_by_id(self, booking_id: UUID) -> Booking | None: ...

    def exists_active_conflict(
        self,
        room_id: UUID,
        start_at: datetime,
        end_at: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> bool: ...


class RoomRepository(Protocol):
    def get_by_id(self, room_id: UUID) -> Room | None: ...


class OutboxEventPublisher(Protocol):
    def publish_booking_event(
        self,
        event_type: OutboxEventType,
        booking: Booking,
        room_name: str,
    ) -> None: ...


class OutboxEventRepository(Protocol):
    def fetch_pending_batch_for_processing(
        self,
        limit: int,
        processing_timeout_seconds: int = 300,
    ) -> list[OutboxEvent]: ...

    def mark_processing(self, event_id: UUID) -> None: ...

    def mark_processed(self, event_id: UUID) -> None: ...

    def schedule_retry(self, event_id: UUID, next_retry_at: datetime) -> None: ...

    def mark_failed(self, event_id: UUID) -> None: ...


class UnitOfWork(Protocol):
    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc, tb) -> None: ...

    @property
    def bookings(self) -> BookingRepository: ...

    @property
    def rooms(self) -> RoomRepository: ...

    @property
    def outbox(self) -> OutboxEventPublisher: ...

    @property
    def outbox_events(self) -> OutboxEventRepository: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


UoWFactory = Callable[[], AbstractContextManager[UnitOfWork]]
