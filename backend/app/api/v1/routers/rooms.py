from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import AuthenticatedUser, get_current_admin, get_current_user, get_db_session
from app.api.v1.schemas import RoomCreateRequest, RoomResponse
from app.infrastructure.orm.models.room_model import RoomModel

router = APIRouter()


@router.get("")
def list_rooms(
    _: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> list[RoomResponse]:
    rooms = db.execute(select(RoomModel).order_by(RoomModel.name.asc())).scalars().all()
    return [RoomResponse(id=room.id, name=room.name, capacity=room.capacity) for room in rooms]


@router.get("/{room_id}")
def get_room(
    room_id: UUID,
    _: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> RoomResponse:
    room = db.execute(select(RoomModel).where(RoomModel.id == room_id)).scalar_one_or_none()
    if room is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room does not exist.")
    return RoomResponse(id=room.id, name=room.name, capacity=room.capacity)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreateRequest,
    _: AuthenticatedUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
) -> RoomResponse:
    room = RoomModel(name=payload.name.strip(), capacity=payload.capacity)
    db.add(room)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        message = str(error.orig).lower() if error.orig else str(error).lower()
        if "unique" in message and "rooms" in message and "name" in message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room name already exists.",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create room.")
    db.refresh(room)
    return RoomResponse(id=room.id, name=room.name, capacity=room.capacity)
