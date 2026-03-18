from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums import OutboxEventType, OutboxStatus


@dataclass
class OutboxEvent:
    id: UUID
    aggregate_type: str
    aggregate_id: UUID
    event_type: OutboxEventType
    payload_json: dict
    idempotency_key: str
    status: OutboxStatus = OutboxStatus.PENDING
    attempt_count: int = 0
    max_attempts: int = 5
    next_retry_at: datetime | None = None
    processed_at: datetime | None = None
