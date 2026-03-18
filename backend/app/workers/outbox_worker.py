import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.core.config import get_settings
from app.core.db import SessionLocal
from app.domain.enums import OutboxStatus
from app.infrastructure.email import ConsoleEmailSender, EmailSender
from app.infrastructure.orm.models.outbox_event_model import OutboxEventModel
from app.infrastructure.repositories import SqlAlchemyEmailDeliveryRepository
from app.infrastructure.uow import SqlAlchemyUnitOfWork

logger = logging.getLogger(__name__)
settings = get_settings()


def _compute_backoff_seconds(next_attempt: int) -> int:
    base = 30
    raw = base * (2 ** (next_attempt - 1))
    return min(raw, settings.worker_max_backoff_seconds)


def _event_action_text(event_type: str) -> str:
    mapping = {
        "BOOKING_CREATED": "created",
        "BOOKING_UPDATED": "updated",
        "BOOKING_CANCELED": "canceled",
    }
    return mapping.get(event_type, event_type.lower())


def _build_email(event_payload: dict[str, Any]) -> tuple[str, str]:
    booking_payload = event_payload.get("booking", {})
    event_type = event_payload.get("event_type", "BOOKING_UPDATED")
    action_text = _event_action_text(event_type)

    title = booking_payload.get("title", "Meeting")
    room_name = booking_payload.get("room_name", "Unknown room")
    start_at = booking_payload.get("start_at", "")
    end_at = booking_payload.get("end_at", "")

    subject = f"[Meeting Rooms] Booking {action_text}: {title}"
    body = (
        f"Event: booking {action_text}\n"
        f"Title: {title}\n"
        f"Room: {room_name}\n"
        f"Start: {start_at}\n"
        f"End: {end_at}\n"
    )
    return subject, body


def _claim_pending_events() -> list[UUID]:
    with SessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        with uow:
            events = uow.outbox_events.fetch_pending_batch_for_processing(
                limit=settings.worker_batch_size,
                processing_timeout_seconds=settings.worker_processing_timeout_seconds,
            )
            for event in events:
                uow.outbox_events.mark_processing(event.id)
            uow.commit()
            return [event.id for event in events]


def _process_single_event(event_id: UUID, email_sender: EmailSender) -> None:
    with SessionLocal() as session:
        uow = SqlAlchemyUnitOfWork(session)
        deliveries = SqlAlchemyEmailDeliveryRepository(session)
        with uow:
            event = session.get(OutboxEventModel, event_id)
            if event is None:
                return

            if event.status not in (OutboxStatus.PROCESSING, OutboxStatus.PENDING):
                return

            event_payload = dict(event.payload_json or {})
            booking_payload = event_payload.get("booking", {})
            recipients = list(booking_payload.get("participants", []))
            subject, body = _build_email(event_payload)

            try:
                for recipient in recipients:
                    if deliveries.already_sent(event.id, recipient):
                        continue

                    message_id = email_sender.send_email(
                        recipient=recipient,
                        subject=subject,
                        body=body,
                        idempotency_key=f"{event.id}:{recipient}",
                    )
                    deliveries.record_delivery(event.id, recipient, message_id)

                uow.outbox_events.mark_processed(event.id)
                uow.commit()
            except Exception as exc:  # noqa: BLE001
                next_attempt = event.attempt_count + 1
                if next_attempt >= event.max_attempts:
                    uow.outbox_events.mark_failed(event.id)
                    logger.exception(
                        "Outbox event %s reached max attempts and was marked as FAILED.",
                        event.id,
                    )
                else:
                    retry_seconds = _compute_backoff_seconds(next_attempt)
                    retry_at = datetime.now(UTC) + timedelta(seconds=retry_seconds)
                    uow.outbox_events.schedule_retry(event.id, retry_at)
                    logger.exception(
                        "Outbox event %s failed. Retrying at %s.",
                        event.id,
                        retry_at.isoformat(),
                    )
                uow.commit()
                logger.debug("Worker error detail: %s", str(exc))


def run(email_sender: EmailSender | None = None) -> None:
    if email_sender is None:
        email_sender = ConsoleEmailSender()

    logger.info(
        "Outbox worker started (poll=%ss, batch=%s)",
        settings.worker_poll_interval_seconds,
        settings.worker_batch_size,
    )
    while True:
        claimed_event_ids = _claim_pending_events()
        if not claimed_event_ids:
            time.sleep(settings.worker_poll_interval_seconds)
            continue

        for event_id in claimed_event_ids:
            _process_single_event(event_id, email_sender)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
