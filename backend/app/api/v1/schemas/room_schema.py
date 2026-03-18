from uuid import UUID

from pydantic import BaseModel, Field


class RoomCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    capacity: int = Field(gt=0)


class RoomResponse(BaseModel):
    id: UUID
    name: str
    capacity: int
