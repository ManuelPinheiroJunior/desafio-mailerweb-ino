from sqlalchemy.orm import Session

from app.infrastructure.repositories.sqlalchemy_booking_repository import SqlAlchemyBookingRepository
from app.infrastructure.repositories.sqlalchemy_outbox_publisher import SqlAlchemyOutboxPublisher
from app.infrastructure.repositories.sqlalchemy_outbox_repository import SqlAlchemyOutboxRepository
from app.infrastructure.repositories.sqlalchemy_room_repository import SqlAlchemyRoomRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.bookings = SqlAlchemyBookingRepository(session)
        self.rooms = SqlAlchemyRoomRepository(session)
        self.outbox = SqlAlchemyOutboxPublisher(session)
        self.outbox_events = SqlAlchemyOutboxRepository(session)

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
