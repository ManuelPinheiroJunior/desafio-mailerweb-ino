from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: UUID
    email: str
    is_admin: bool


def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    try:
        payload = decode_access_token(token)
        user_id = UUID(payload["sub"])
        email = str(payload["email"])
        is_admin = bool(payload.get("is_admin", False))
        return AuthenticatedUser(user_id=user_id, email=email, is_admin=is_admin)
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )


def get_current_admin(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this operation.",
        )
    return user


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db
