from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Barrier, Lock, Thread
from uuid import UUID, uuid4

import pytest

from app.application.commands import CreateBookingCommand, UpdateBookingCommand
from app.application.services import BookingAppService
from app.domain.entities import Booking, Room
from app.domain.enums import BookingStatus, OutboxEventType
from app.domain.exceptions import BookingConflictError, BookingPermissionDeniedError


def _overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and a_end > b_start


class InMemoryBookingRepository:
    def __init__(self, bookings: dict[UUID, Booking], sync_barrier: Barrier | None = None) -> None:
        self.bookings = bookings
        self.sync_barrier = sync_barrier
        self.lock = Lock()

    def add(self, booking: Booking) -> None:
        if self.sync_barrier is not None:
            self.sync_barrier.wait(timeout=2)
        with self.lock:
            for current in self.bookings.values():
                if current.status != BookingStatus.ACTIVE:
                    continue
                if current.room_id != booking.room_id:
                    continue
                if _overlaps(booking.start_at, booking.end_at, current.start_at, current.end_at):
                    raise BookingConflictError("There is an active booking conflict in this room.")
            self.bookings[booking.id] = booking

    def save(self, booking: Booking) -> None:
        self.bookings[booking.id] = booking

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        return self.bookings.get(booking_id)

    def exists_active_conflict(
        self,
        room_id: UUID,
        start_at: datetime,
        end_at: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> bool:
        for booking in self.bookings.values():
            if booking.status != BookingStatus.ACTIVE:
                continue
            if booking.room_id != room_id:
                continue
            if exclude_booking_id and booking.id == exclude_booking_id:
                continue
            if _overlaps(start_at, end_at, booking.start_at, booking.end_at):
                return True
        return False


class InMemoryRoomRepository:
    def __init__(self, rooms: dict[UUID, Room]) -> None:
        self.rooms = rooms

    def get_by_id(self, room_id: UUID) -> Room | None:
        return self.rooms.get(room_id)


class InMemoryOutboxPublisher:
    def __init__(self) -> None:
        self.events: list[tuple[OutboxEventType, UUID, str]] = []

    def publish_booking_event(self, event_type: OutboxEventType, booking: Booking, room_name: str) -> None:
        self.events.append((event_type, booking.id, room_name))


@dataclass
class InMemoryUoW:
    bookings: InMemoryBookingRepository
    rooms: InMemoryRoomRepository
    outbox: InMemoryOutboxPublisher
    committed: bool = False

    @property
    def outbox_events(self):  # pragma: no cover - not used in these tests
        return None

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type:
            self.rollback()


def _build_service(
    bookings: dict[UUID, Booking] | None = None,
    rooms: dict[UUID, Room] | None = None,
    sync_barrier: Barrier | None = None,
):
    bookings = bookings or {}
    room_id = uuid4()
    rooms = rooms or {room_id: Room(id=room_id, name="Room A", capacity=10)}
    outbox = InMemoryOutboxPublisher()

    uow = InMemoryUoW(
        bookings=InMemoryBookingRepository(bookings, sync_barrier=sync_barrier),
        rooms=InMemoryRoomRepository(rooms),
        outbox=outbox,
    )

    @contextmanager
    def factory():
        yield uow

    return BookingAppService(uow_factory=factory), uow, next(iter(rooms.values()))


def test_create_booking_publishes_outbox_event() -> None:
    service, uow, room = _build_service()
    command = CreateBookingCommand(
        title="Planning",
        room_id=room.id,
        organizer_user_id=uuid4(),
        start_at=datetime(2026, 3, 17, 10, 0, tzinfo=UTC),
        end_at=datetime(2026, 3, 17, 11, 0, tzinfo=UTC),
        participants=["A@MAIL.COM", "a@mail.com", "b@mail.com"],
    )

    dto = service.create_booking(command)

    assert dto.title == "Planning"
    assert dto.participants == ["a@mail.com", "b@mail.com"]
    assert uow.committed is True
    assert len(uow.outbox.events) == 1
    event_type, booking_id, room_name = uow.outbox.events[0]
    assert event_type == OutboxEventType.BOOKING_CREATED
    assert booking_id == dto.id
    assert room_name == "Room A"


def test_update_booking_requires_permission() -> None:
    room = Room(id=uuid4(), name="Room A", capacity=10)
    existing = Booking(
        id=uuid4(),
        title="Review",
        room_id=room.id,
        organizer_user_id=uuid4(),
        start_at=datetime(2026, 3, 17, 10, 0, tzinfo=UTC),
        end_at=datetime(2026, 3, 17, 11, 0, tzinfo=UTC),
    )
    service, _, _ = _build_service(bookings={existing.id: existing}, rooms={room.id: room})

    command = UpdateBookingCommand(
        booking_id=existing.id,
        actor_user_id=uuid4(),
        title="Review updated",
        room_id=room.id,
        start_at=existing.start_at + timedelta(hours=1),
        end_at=existing.end_at + timedelta(hours=1),
        participants=["x@mail.com"],
        actor_is_admin=False,
    )

    with pytest.raises(BookingPermissionDeniedError):
        service.update_booking(command)


def test_concurrent_create_only_one_booking_wins() -> None:
    barrier = Barrier(2)
    service, uow, room = _build_service(sync_barrier=barrier)
    organizer_a = uuid4()
    organizer_b = uuid4()
    start_at = datetime(2026, 3, 17, 14, 0, tzinfo=UTC)
    end_at = datetime(2026, 3, 17, 15, 0, tzinfo=UTC)

    results: list[str] = []

    def _create(organizer_id: UUID) -> None:
        command = CreateBookingCommand(
            title="Concurrent",
            room_id=room.id,
            organizer_user_id=organizer_id,
            start_at=start_at,
            end_at=end_at,
            participants=["p@mail.com"],
        )
        try:
            service.create_booking(command)
            results.append("ok")
        except BookingConflictError:
            results.append("conflict")

    t1 = Thread(target=_create, args=(organizer_a,))
    t2 = Thread(target=_create, args=(organizer_b,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(results) == ["conflict", "ok"]
    assert len(uow.bookings.bookings) == 1
