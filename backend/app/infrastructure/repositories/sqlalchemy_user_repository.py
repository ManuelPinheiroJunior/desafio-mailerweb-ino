from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.orm.models.user_model import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_email(self, email: str) -> UserModel | None:
        return self.session.execute(
            select(UserModel).where(UserModel.email == email.lower())
        ).scalar_one_or_none()
