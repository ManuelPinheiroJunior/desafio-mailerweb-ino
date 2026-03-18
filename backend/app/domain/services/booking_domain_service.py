from app.domain.value_objects import EmailAddress
from app.domain.exceptions import InvalidBookingTitleError


class BookingDomainService:
    @staticmethod
    def normalize_title(title: str) -> str:
        normalized = title.strip()
        if not normalized:
            raise InvalidBookingTitleError("Booking title cannot be empty.")
        return normalized

    @staticmethod
    def normalize_participants(emails: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for raw_email in emails:
            email = EmailAddress.create(raw_email).value
            if email in seen:
                continue
            seen.add(email)
            normalized.append(email)

        return normalized
