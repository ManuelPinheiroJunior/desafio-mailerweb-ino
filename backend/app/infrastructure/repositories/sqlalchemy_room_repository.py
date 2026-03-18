from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities import Room
from app.infrastructure.orm.models.room_model import RoomModel


class SqlAlchemyRoomRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, room_id: UUID) -> Room | None:
        model = self.session.execute(
            select(RoomModel).where(RoomModel.id == room_id)
        ).scalar_one_or_none()
        if model is None:
            return None
        return Room(id=model.id, name=model.name, capacity=model.capacity)
