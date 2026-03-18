from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, exists, select
from sqlalchemy.orm import Session, joinedload

from app.domain.entities import Booking
from app.domain.enums import BookingStatus
from app.infrastructure.orm.models.booking_model import BookingModel
from app.infrastructure.orm.models.booking_participant_model import BookingParticipantModel


def _to_domain(model: BookingModel) -> Booking:
    return Booking(
        id=model.id,
        title=model.title,
        room_id=model.room_id,
        organizer_user_id=model.organizer_user_id,
        start_at=model.start_at,
        end_at=model.end_at,
        status=model.status,
        participants=[participant.email for participant in model.participants],
        version=model.version,
    )


class SqlAlchemyBookingRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, booking: Booking) -> None:
        model = BookingModel(
            id=booking.id,
            title=booking.title,
            room_id=booking.room_id,
            organizer_user_id=booking.organizer_user_id,
            start_at=booking.start_at,
            end_at=booking.end_at,
            status=booking.status,
            version=booking.version,
            participants=[
                BookingParticipantModel(email=email)
                for email in booking.participants
            ],
        )
        self.session.add(model)

    def save(self, booking: Booking) -> None:
        model = self.session.execute(
            select(BookingModel)
            .options(joinedload(BookingModel.participants))
            .where(BookingModel.id == booking.id)
        ).unique().scalar_one()

        model.title = booking.title
        model.room_id = booking.room_id
        model.start_at = booking.start_at
        model.end_at = booking.end_at
        model.status = booking.status
        model.version = booking.version

        model.participants.clear()
        model.participants.extend(
            BookingParticipantModel(booking_id=booking.id, email=email)
            for email in booking.participants
        )

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        model = self.session.execute(
            select(BookingModel)
            .options(joinedload(BookingModel.participants))
            .where(BookingModel.id == booking_id)
        ).unique().scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model)

    def exists_active_conflict(
        self,
        room_id: UUID,
        start_at: datetime,
        end_at: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> bool:
        conditions = [
            BookingModel.room_id == room_id,
            BookingModel.status == BookingStatus.ACTIVE,
            BookingModel.start_at < end_at,
            BookingModel.end_at > start_at,
        ]
        if exclude_booking_id is not None:
            conditions.append(BookingModel.id != exclude_booking_id)

        statement = select(exists().where(and_(*conditions)))
        return bool(self.session.execute(statement).scalar())
