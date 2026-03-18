from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.orm.models.email_delivery_model import EmailDeliveryModel


class SqlAlchemyEmailDeliveryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def already_sent(self, outbox_event_id: UUID, recipient_email: str) -> bool:
        statement = select(EmailDeliveryModel.id).where(
            EmailDeliveryModel.outbox_event_id == outbox_event_id,
            EmailDeliveryModel.recipient_email == recipient_email.lower(),
        )
        return self.session.execute(statement).scalar_one_or_none() is not None

    def record_delivery(
        self,
        outbox_event_id: UUID,
        recipient_email: str,
        provider_message_id: str | None,
    ) -> bool:
        delivery = EmailDeliveryModel(
            outbox_event_id=outbox_event_id,
            recipient_email=recipient_email.lower(),
            provider_message_id=provider_message_id,
        )
        savepoint = self.session.begin_nested()
        self.session.add(delivery)
        try:
            self.session.flush()
            savepoint.commit()
            return True
        except IntegrityError:
            savepoint.rollback()
            return False
