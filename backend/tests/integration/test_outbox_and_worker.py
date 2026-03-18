from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select

from app.application.commands import CreateBookingCommand
from app.application.services import BookingAppService
from app.domain.enums import BookingStatus, OutboxEventType, OutboxStatus
from app.domain.exceptions import BookingConflictError
from app.infrastructure.orm.models.booking_model import BookingModel
from app.infrastructure.orm.models.outbox_event_model import OutboxEventModel
from app.infrastructure.orm.models.room_model import RoomModel
from app.infrastructure.orm.models.user_model import UserModel
from app.infrastructure.uow import SqlAlchemyUnitOfWork
from app.workers import outbox_worker


class SpyEmailSender:
    def __init__(self, fail_times: int = 0) -> None:
        self.fail_times = fail_times
        self.calls: list[tuple[str, str, str, str]] = []

    def send_email(self, recipient: str, subject: str, body: str, idempotency_key: str) -> str:
        if self.fail_times > 0:
            self.fail_times -= 1
            raise RuntimeError("temporary email provider failure")
        self.calls.append((recipient, subject, body, idempotency_key))
        return f"msg-{len(self.calls)}"


def _uow_factory(session_factory):
    @contextmanager
    def factory():
        with session_factory() as session:
            yield SqlAlchemyUnitOfWork(session)

    return factory


def test_outbox_event_created_on_booking_creation(sqlite_session_factory) -> None:
    with sqlite_session_factory() as session:
        user = UserModel(email="owner@mail.com", password_hash="hash")
        room = RoomModel(name="Room One", capacity=8)
        session.add_all([user, room])
        session.commit()

        service = BookingAppService(uow_factory=_uow_factory(sqlite_session_factory))
        command = CreateBookingCommand(
            title="Sprint Planning",
            room_id=room.id,
            organizer_user_id=user.id,
            start_at=datetime(2026, 3, 17, 9, 0, tzinfo=UTC),
            end_at=datetime(2026, 3, 17, 10, 0, tzinfo=UTC),
            participants=["a@mail.com", "b@mail.com"],
        )
        service.create_booking(command)

    with sqlite_session_factory() as session:
        events = session.execute(select(OutboxEventModel)).scalars().all()
        assert len(events) == 1
        event = events[0]
        assert event.event_type == OutboxEventType.BOOKING_CREATED
        assert event.status == OutboxStatus.PENDING
        assert event.payload_json["booking"]["room_name"] == "Room One"


def test_outbox_event_not_created_when_booking_conflicts(sqlite_session_factory) -> None:
    with sqlite_session_factory() as session:
        user = UserModel(email="owner@mail.com", password_hash="hash")
        room = RoomModel(name="Room One", capacity=8)
        session.add_all([user, room])
        session.commit()

        existing = BookingModel(
            title="Existing",
            room_id=room.id,
            organizer_user_id=user.id,
            start_at=datetime(2026, 3, 17, 9, 0, tzinfo=UTC),
            end_at=datetime(2026, 3, 17, 10, 0, tzinfo=UTC),
            status=BookingStatus.ACTIVE,
            version=1,
        )
        session.add(existing)
        session.commit()

        service = BookingAppService(uow_factory=_uow_factory(sqlite_session_factory))
        command = CreateBookingCommand(
            title="Overlap",
            room_id=room.id,
            organizer_user_id=user.id,
            start_at=datetime(2026, 3, 17, 9, 30, tzinfo=UTC),
            end_at=datetime(2026, 3, 17, 10, 30, tzinfo=UTC),
            participants=["a@mail.com"],
        )

        raised = False
        try:
            service.create_booking(command)
        except BookingConflictError:
            raised = True
        assert raised is True

    with sqlite_session_factory() as session:
        events = session.execute(select(OutboxEventModel)).scalars().all()
        assert len(events) == 0


def test_worker_processes_outbox_event_and_is_idempotent(sqlite_session_factory, monkeypatch) -> None:
    with sqlite_session_factory() as session:
        event = OutboxEventModel(
            aggregate_type="BOOKING",
            aggregate_id=uuid4(),
            event_type=OutboxEventType.BOOKING_CREATED,
            payload_json={
                "event_type": "BOOKING_CREATED",
                "booking": {
                    "title": "Daily",
                    "room_name": "Room One",
                    "start_at": "2026-03-17T09:00:00+00:00",
                    "end_at": "2026-03-17T09:30:00+00:00",
                    "participants": ["a@mail.com", "b@mail.com"],
                },
            },
            status=OutboxStatus.PROCESSING,
            attempt_count=0,
            max_attempts=5,
            next_retry_at=datetime.now(UTC),
            idempotency_key=f"idem-{uuid4()}",
        )
        session.add(event)
        session.commit()
        event_id = event.id

    monkeypatch.setattr(outbox_worker, "SessionLocal", sqlite_session_factory)
    sender = SpyEmailSender()

    outbox_worker._process_single_event(event_id, sender)
    assert len(sender.calls) == 2

    with sqlite_session_factory() as session:
        event = session.get(OutboxEventModel, event_id)
        assert event is not None
        assert event.status == OutboxStatus.PROCESSED
        # Force re-processing attempt to assert recipient-level idempotency.
        event.status = OutboxStatus.PROCESSING
        event.next_retry_at = datetime.now(UTC)
        session.commit()

    outbox_worker._process_single_event(event_id, sender)
    assert len(sender.calls) == 2


def test_worker_retries_on_failure(sqlite_session_factory, monkeypatch) -> None:
    with sqlite_session_factory() as session:
        event = OutboxEventModel(
            aggregate_type="BOOKING",
            aggregate_id=uuid4(),
            event_type=OutboxEventType.BOOKING_UPDATED,
            payload_json={
                "event_type": "BOOKING_UPDATED",
                "booking": {
                    "title": "Retro",
                    "room_name": "Room Two",
                    "start_at": "2026-03-17T14:00:00+00:00",
                    "end_at": "2026-03-17T15:00:00+00:00",
                    "participants": ["a@mail.com"],
                },
            },
            status=OutboxStatus.PROCESSING,
            attempt_count=0,
            max_attempts=2,
            next_retry_at=datetime.now(UTC),
            idempotency_key=f"idem-{uuid4()}",
        )
        session.add(event)
        session.commit()
        event_id = event.id

    monkeypatch.setattr(outbox_worker, "SessionLocal", sqlite_session_factory)
    sender = SpyEmailSender(fail_times=1)

    outbox_worker._process_single_event(event_id, sender)

    with sqlite_session_factory() as session:
        event = session.get(OutboxEventModel, event_id)
        assert event is not None
        assert event.status == OutboxStatus.PENDING
        assert event.attempt_count == 1
        assert event.next_retry_at is not None

        # Make retry immediately eligible and process again.
        event.status = OutboxStatus.PROCESSING
        event.next_retry_at = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()

    outbox_worker._process_single_event(event_id, sender)

    with sqlite_session_factory() as session:
        event = session.get(OutboxEventModel, event_id)
        assert event is not None
        assert event.status == OutboxStatus.PROCESSED
