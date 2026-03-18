class DomainError(Exception):
    """Base error for domain-level business rule violations."""


class InvalidBookingTimeError(DomainError):
    """Raised when booking time window is invalid."""


class BookingConflictError(DomainError):
    """Raised when booking overlaps an active booking in the same room."""


class BookingNotFoundError(DomainError):
    """Raised when booking does not exist."""


class BookingPermissionDeniedError(DomainError):
    """Raised when user is not allowed to mutate a booking."""


class BookingAlreadyCanceledError(DomainError):
    """Raised when cancel operation targets an already canceled booking."""


class InvalidEmailError(DomainError):
    """Raised when a participant email is invalid."""


class InvalidBookingTitleError(DomainError):
    """Raised when booking title is invalid."""
