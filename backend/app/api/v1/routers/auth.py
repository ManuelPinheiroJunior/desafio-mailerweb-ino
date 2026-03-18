from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.api.v1.schemas import LoginRequest, LoginResponse, RegisterRequest
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.infrastructure.orm.models.user_model import UserModel
from app.infrastructure.repositories import SqlAlchemyUserRepository

settings = get_settings()
router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)) -> dict[str, str]:
    user = UserModel(email=payload.email.lower().strip(), password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered.",
        )
    return {"message": "User created successfully."}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> LoginResponse:
    users = SqlAlchemyUserRepository(db)
    user = users.get_by_email(payload.email.lower())
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    is_admin = user.email.lower() == settings.admin_email.lower()
    token = create_access_token(user_id=user.id, email=user.email, is_admin=is_admin)
    return LoginResponse(access_token=token)
