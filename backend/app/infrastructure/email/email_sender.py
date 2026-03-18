from typing import Protocol


class EmailSender(Protocol):
    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        idempotency_key: str,
    ) -> str: ...
