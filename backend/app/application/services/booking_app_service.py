from uuid import uuid4

from app.application.commands import CancelBookingCommand, CreateBookingCommand, UpdateBookingCommand
from app.application.dto import BookingDTO
from app.application.ports import UoWFactory
from app.domain.entities import Booking
from app.domain.enums import OutboxEventType
from app.domain.exceptions import BookingConflictError, BookingNotFoundError
from app.domain.services import BookingDomainService
from app.domain.value_objects import BookingTimeWindow


class BookingAppService:
    def __init__(self, uow_factory: UoWFactory) -> None:
        self._uow_factory = uow_factory

    def create_booking(self, command: CreateBookingCommand) -> BookingDTO:
        time_window = BookingTimeWindow.create(command.start_at, command.end_at)
        title = BookingDomainService.normalize_title(command.title)
        participants = BookingDomainService.normalize_participants(command.participants)

        with self._uow_factory() as uow:
            room = uow.rooms.get_by_id(command.room_id)
            if room is None:
                raise BookingNotFoundError("Room does not exist.")

            has_conflict = uow.bookings.exists_active_conflict(
                room_id=command.room_id,
                start_at=time_window.start_at,
                end_at=time_window.end_at,
            )
            if has_conflict:
                raise BookingConflictError("There is an active booking conflict in this room.")

            booking = Booking(
                id=uuid4(),
                title=title,
                room_id=command.room_id,
                organizer_user_id=command.organizer_user_id,
                start_at=time_window.start_at,
                end_at=time_window.end_at,
                participants=participants,
            )
            uow.bookings.add(booking)
            uow.outbox.publish_booking_event(
                OutboxEventType.BOOKING_CREATED,
                booking,
                room_name=room.name,
            )
            uow.commit()
            return self._to_dto(booking)

    def update_booking(self, command: UpdateBookingCommand) -> BookingDTO:
        time_window = BookingTimeWindow.create(command.start_at, command.end_at)
        title = BookingDomainService.normalize_title(command.title)
        participants = BookingDomainService.normalize_participants(command.participants)

        with self._uow_factory() as uow:
            booking = uow.bookings.get_by_id(command.booking_id)
            if booking is None:
                raise BookingNotFoundError("Booking does not exist.")

            booking.assert_can_be_modified_by(
                actor_user_id=command.actor_user_id,
                actor_is_admin=command.actor_is_admin,
            )

            room = uow.rooms.get_by_id(command.room_id)
            if room is None:
                raise BookingNotFoundError("Room does not exist.")

            has_conflict = uow.bookings.exists_active_conflict(
                room_id=command.room_id,
                start_at=time_window.start_at,
                end_at=time_window.end_at,
                exclude_booking_id=booking.id,
            )
            if has_conflict:
                raise BookingConflictError("There is an active booking conflict in this room.")

            booking.apply_schedule_update(
                title=title,
                room_id=command.room_id,
                time_window=time_window,
                participants=participants,
            )
            uow.bookings.save(booking)
            uow.outbox.publish_booking_event(
                OutboxEventType.BOOKING_UPDATED,
                booking,
                room_name=room.name,
            )
            uow.commit()
            return self._to_dto(booking)

    def cancel_booking(self, command: CancelBookingCommand) -> BookingDTO:
        with self._uow_factory() as uow:
            booking = uow.bookings.get_by_id(command.booking_id)
            if booking is None:
                raise BookingNotFoundError("Booking does not exist.")
            room = uow.rooms.get_by_id(booking.room_id)
            if room is None:
                raise BookingNotFoundError("Room does not exist.")

            booking.assert_can_be_modified_by(
                actor_user_id=command.actor_user_id,
                actor_is_admin=command.actor_is_admin,
            )
            booking.cancel()
            uow.bookings.save(booking)
            uow.outbox.publish_booking_event(
                OutboxEventType.BOOKING_CANCELED,
                booking,
                room_name=room.name,
            )
            uow.commit()
            return self._to_dto(booking)

    @staticmethod
    def _to_dto(booking: Booking) -> BookingDTO:
        return BookingDTO(
            id=booking.id,
            title=booking.title,
            room_id=booking.room_id,
            organizer_user_id=booking.organizer_user_id,
            start_at=booking.start_at,
            end_at=booking.end_at,
            status=booking.status,
            participants=booking.participants,
            version=booking.version,
        )
