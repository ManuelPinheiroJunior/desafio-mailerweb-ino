from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import BookingStatus


class BookingCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    room_id: UUID
    start_at: datetime
    end_at: datetime
    participants: list[str] = Field(default_factory=list)


class BookingUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    room_id: UUID
    start_at: datetime
    end_at: datetime
    participants: list[str] = Field(default_factory=list)


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    room_id: UUID
    organizer_user_id: UUID
    start_at: datetime
    end_at: datetime
    status: BookingStatus
    participants: list[str]
    version: int
