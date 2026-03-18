from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.domain.exceptions import (
    BookingAlreadyCanceledError,
    BookingConflictError,
    BookingNotFoundError,
    BookingPermissionDeniedError,
    InvalidBookingTimeError,
    InvalidBookingTitleError,
    InvalidEmailError,
)


def raise_http_from_domain_error(error: Exception) -> None:
    if isinstance(error, (InvalidBookingTimeError, InvalidEmailError, InvalidBookingTitleError)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error))
    if isinstance(error, BookingPermissionDeniedError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error))
    if isinstance(error, BookingConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(error, BookingNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    if isinstance(error, BookingAlreadyCanceledError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))

    raise error


def raise_http_from_integrity_error(error: IntegrityError) -> None:
    message = str(error.orig).lower() if error.orig else str(error).lower()
    if "bookings_no_overlap_active" in message:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is an active booking conflict in this room.",
        )
    if "unique" in message and "rooms" in message and "name" in message:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Room name already exists.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database integrity error.")
