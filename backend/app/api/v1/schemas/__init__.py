from app.api.v1.schemas.auth_schema import LoginRequest, LoginResponse, RegisterRequest
from app.api.v1.schemas.booking_schema import BookingCreateRequest, BookingResponse, BookingUpdateRequest
from app.api.v1.schemas.room_schema import RoomCreateRequest, RoomResponse

__all__ = [
    "LoginRequest",
    "LoginResponse",
    "RegisterRequest",
    "RoomCreateRequest",
    "RoomResponse",
    "BookingCreateRequest",
    "BookingUpdateRequest",
    "BookingResponse",
]
