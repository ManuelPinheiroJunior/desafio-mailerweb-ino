from dataclasses import dataclass
from email.utils import parseaddr

from app.domain.exceptions import InvalidEmailError


@dataclass(frozen=True)
class EmailAddress:
    value: str

    @staticmethod
    def create(raw_email: str) -> "EmailAddress":
        normalized = raw_email.strip().lower()
        _, parsed = parseaddr(normalized)
        if not parsed or "@" not in parsed:
            raise InvalidEmailError("Participant email is invalid.")
        return EmailAddress(value=normalized)
