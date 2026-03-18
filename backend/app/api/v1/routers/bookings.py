from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.deps import AuthenticatedUser, get_current_user, get_db_session
from app.api.v1.error_mapping import raise_http_from_domain_error, raise_http_from_integrity_error
from app.api.v1.schemas import BookingCreateRequest, BookingResponse, BookingUpdateRequest
from app.application.commands import CancelBookingCommand, CreateBookingCommand, UpdateBookingCommand
from app.application.services import BookingAppService
from app.domain.exceptions import DomainError
from app.infrastructure.orm.models.booking_model import BookingModel
from app.infrastructure.uow import SqlAlchemyUnitOfWork

router = APIRouter()


def _service_factory(db: Session) -> BookingAppService:
    uow_factory: Callable[[], SqlAlchemyUnitOfWork] = lambda: SqlAlchemyUnitOfWork(db)
    return BookingAppService(uow_factory=uow_factory)


def _to_response(model: BookingModel) -> BookingResponse:
    return BookingResponse(
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


@router.post("")
def create_booking(
    payload: BookingCreateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BookingResponse:
    service = _service_factory(db)
    command = CreateBookingCommand(
        title=payload.title,
        room_id=payload.room_id,
        organizer_user_id=user.user_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        participants=payload.participants,
    )
    try:
        dto = service.create_booking(command)
    except DomainError as error:
        raise_http_from_domain_error(error)
    except IntegrityError as error:
        db.rollback()
        raise_http_from_integrity_error(error)
    return BookingResponse(**dto.__dict__)


@router.put("/{booking_id}")
def update_booking(
    booking_id: UUID,
    payload: BookingUpdateRequest,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BookingResponse:
    service = _service_factory(db)
    command = UpdateBookingCommand(
        booking_id=booking_id,
        actor_user_id=user.user_id,
        title=payload.title,
        room_id=payload.room_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        participants=payload.participants,
        actor_is_admin=user.is_admin,
    )
    try:
        dto = service.update_booking(command)
    except DomainError as error:
        raise_http_from_domain_error(error)
    except IntegrityError as error:
        db.rollback()
        raise_http_from_integrity_error(error)
    return BookingResponse(**dto.__dict__)


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BookingResponse:
    service = _service_factory(db)
    command = CancelBookingCommand(
        booking_id=booking_id,
        actor_user_id=user.user_id,
        actor_is_admin=user.is_admin,
    )
    try:
        dto = service.cancel_booking(command)
    except DomainError as error:
        raise_http_from_domain_error(error)
    except IntegrityError as error:
        db.rollback()
        raise_http_from_integrity_error(error)
    return BookingResponse(**dto.__dict__)


@router.get("")
def list_bookings(
    _: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[BookingResponse]:
    bookings = db.execute(
        select(BookingModel)
        .options(joinedload(BookingModel.participants))
        .order_by(BookingModel.start_at.asc())
    ).unique().scalars().all()
    return [_to_response(booking) for booking in bookings]


@router.get("/{booking_id}")
def get_booking(
    booking_id: UUID,
    _: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> BookingResponse:
    booking = db.execute(
        select(BookingModel)
        .options(joinedload(BookingModel.participants))
        .where(BookingModel.id == booking_id)
    ).unique().scalar_one_or_none()
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking does not exist.")
    return _to_response(booking)
