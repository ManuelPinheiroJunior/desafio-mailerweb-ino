import logging
from uuid import uuid4

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ConsoleEmailSender:
    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        idempotency_key: str,
    ) -> str:
        message_id = str(uuid4())
        logger.info(
            "EMAIL_SENT from=%s to=%s subject=%s idempotency_key=%s message_id=%s body=%s",
            settings.email_sender_address,
            recipient,
            subject,
            idempotency_key,
            message_id,
            body.replace("\n", " | "),
        )
        return message_id
