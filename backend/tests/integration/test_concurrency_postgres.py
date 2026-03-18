from datetime import UTC, datetime, timedelta
from threading import Barrier, Thread
from uuid import uuid4
import os

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.domain.enums import BookingStatus
from app.infrastructure.orm.models.booking_model import BookingModel
from app.infrastructure.orm.models.room_model import RoomModel
from app.infrastructure.orm.models.user_model import UserModel


TEST_POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    not TEST_POSTGRES_URL,
    reason="Set TEST_POSTGRES_URL to run real Postgres concurrency test.",
)


def test_exclusion_constraint_blocks_simultaneous_overlapping_bookings() -> None:
    engine = create_engine(TEST_POSTGRES_URL)
    SessionFactory = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)

    room_id = uuid4()
    user_id = uuid4()
    start_at = datetime(2026, 3, 19, 14, 0, tzinfo=UTC)
    end_at = start_at + timedelta(hours=1)

    with SessionFactory() as session:
        user = UserModel(id=user_id, email=f"concurrency_{uuid4()}@mail.com", password_hash="hash")
        room = RoomModel(id=room_id, name=f"Room-{uuid4()}", capacity=8)
        session.add_all([user, room])
        session.commit()

    barrier = Barrier(2)
    outcomes: list[str] = []

    def _try_insert_booking(suffix: str) -> None:
        with SessionFactory() as session:
            booking = BookingModel(
                id=uuid4(),
                title=f"Concurrent-{suffix}",
                room_id=room_id,
                organizer_user_id=user_id,
                start_at=start_at,
                end_at=end_at,
                status=BookingStatus.ACTIVE,
                version=1,
            )
            barrier.wait(timeout=3)
            session.add(booking)
            try:
                session.commit()
                outcomes.append("ok")
            except IntegrityError:
                session.rollback()
                outcomes.append("conflict")

    t1 = Thread(target=_try_insert_booking, args=("a",))
    t2 = Thread(target=_try_insert_booking, args=("b",))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert sorted(outcomes) == ["conflict", "ok"]

    with SessionFactory() as session:
        active_count = session.execute(
            select(BookingModel).where(
                BookingModel.room_id == room_id,
                BookingModel.start_at == start_at,
                BookingModel.end_at == end_at,
                BookingModel.status == BookingStatus.ACTIVE,
            )
        ).scalars().all()
        assert len(active_count) == 1
