from datetime import UTC, datetime
from datetime import timedelta
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.domain.entities import OutboxEvent
from app.domain.enums import OutboxStatus
from app.infrastructure.orm.models.outbox_event_model import OutboxEventModel


class SqlAlchemyOutboxRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, model: OutboxEventModel) -> OutboxEvent:
        return OutboxEvent(
            id=model.id,
            aggregate_type=model.aggregate_type,
            aggregate_id=model.aggregate_id,
            event_type=model.event_type,
            payload_json=model.payload_json,
            idempotency_key=model.idempotency_key,
            status=model.status,
            attempt_count=model.attempt_count,
            max_attempts=model.max_attempts,
            next_retry_at=model.next_retry_at,
            processed_at=model.processed_at,
        )

    def fetch_pending_batch_for_processing(
        self,
        limit: int,
        processing_timeout_seconds: int = 300,
    ) -> list[OutboxEvent]:
        now = datetime.now(UTC)
        processing_timeout_cutoff = now - timedelta(seconds=processing_timeout_seconds)
        statement = (
            select(OutboxEventModel)
            .where(
                and_(
                    or_(
                        OutboxEventModel.status == OutboxStatus.PENDING,
                        and_(
                            OutboxEventModel.status == OutboxStatus.PROCESSING,
                            OutboxEventModel.updated_at <= processing_timeout_cutoff,
                        ),
                    ),
                    OutboxEventModel.attempt_count < OutboxEventModel.max_attempts,
                    or_(
                        OutboxEventModel.next_retry_at.is_(None),
                        OutboxEventModel.next_retry_at <= now,
                    ),
                )
            )
            .order_by(OutboxEventModel.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        models = list(self.session.execute(statement).scalars())
        return [self._to_domain(model) for model in models]

    def mark_processing(self, event_id: UUID) -> None:
        event = self.session.get(OutboxEventModel, event_id)
        if event is None:
            return
        event.status = OutboxStatus.PROCESSING

    def mark_processed(self, event_id: UUID) -> None:
        event = self.session.get(OutboxEventModel, event_id)
        if event is None:
            return
        event.status = OutboxStatus.PROCESSED
        event.processed_at = datetime.now(UTC)
        event.next_retry_at = None

    def schedule_retry(self, event_id: UUID, next_retry_at: datetime) -> None:
        event = self.session.get(OutboxEventModel, event_id)
        if event is None:
            return
        event.status = OutboxStatus.PENDING
        event.attempt_count += 1
        event.next_retry_at = next_retry_at

    def mark_failed(self, event_id: UUID) -> None:
        event = self.session.get(OutboxEventModel, event_id)
        if event is None:
            return
        event.status = OutboxStatus.FAILED
        event.attempt_count += 1
