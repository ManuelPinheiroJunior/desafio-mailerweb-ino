"""initial schema

Revision ID: 20260317_0001
Revises:
Create Date: 2026-03-17 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260317_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


booking_status = postgresql.ENUM("ACTIVE", "CANCELED", name="booking_status", create_type=False)
outbox_status = postgresql.ENUM(
    "PENDING",
    "PROCESSING",
    "PROCESSED",
    "FAILED",
    name="outbox_status",
    create_type=False,
)
outbox_event_type = postgresql.ENUM(
    "BOOKING_CREATED",
    "BOOKING_UPDATED",
    "BOOKING_CANCELED",
    name="outbox_event_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    booking_status.create(bind, checkfirst=True)
    outbox_status.create(bind, checkfirst=True)
    outbox_event_type.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "rooms",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("capacity > 0", name="ck_rooms_capacity_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rooms_name", "rooms", ["name"], unique=True)

    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("room_id", sa.Uuid(), nullable=False),
        sa.Column("organizer_user_id", sa.Uuid(), nullable=False),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("start_at < end_at", name="ck_bookings_start_before_end"),
        sa.ForeignKeyConstraint(["organizer_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["room_id"], ["rooms.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookings_room_id", "bookings", ["room_id"], unique=False)
    op.create_index("ix_bookings_organizer_user_id", "bookings", ["organizer_user_id"], unique=False)
    op.create_index(
        "ix_bookings_room_time_window",
        "bookings",
        ["room_id", "start_at", "end_at"],
        unique=False,
    )

    op.create_table(
        "booking_participants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("booking_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("booking_id", "email", name="uq_booking_participant_email"),
    )
    op.create_index(
        "ix_booking_participants_booking_id",
        "booking_participants",
        ["booking_id"],
        unique=False,
    )

    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("aggregate_type", sa.String(length=80), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", outbox_event_type, nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("status", outbox_status, nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("next_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(
        "ix_outbox_events_status_next_retry",
        "outbox_events",
        ["status", "next_retry_at"],
        unique=False,
    )
    op.create_index(
        "ix_outbox_events_aggregate",
        "outbox_events",
        ["aggregate_type", "aggregate_id"],
        unique=False,
    )

    op.create_table(
        "email_deliveries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("outbox_event_id", sa.Uuid(), nullable=False),
        sa.Column("recipient_email", sa.String(length=320), nullable=False),
        sa.Column("provider_message_id", sa.String(length=255), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["outbox_event_id"], ["outbox_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("outbox_event_id", "recipient_email", name="uq_email_delivery_recipient"),
    )
    op.create_index(
        "ix_email_deliveries_outbox_event_id",
        "email_deliveries",
        ["outbox_event_id"],
        unique=False,
    )

    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
        op.execute(
            """
            ALTER TABLE bookings
            ADD CONSTRAINT bookings_no_overlap_active
            EXCLUDE USING gist (
                room_id WITH =,
                tstzrange(start_at, end_at, '[)') WITH &&
            )
            WHERE (status = 'ACTIVE')
            """
        )
    else:
        op.create_index(
            "ix_bookings_overlap_guard_fallback",
            "bookings",
            ["room_id", "status", "start_at", "end_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    if is_postgres:
        op.execute("ALTER TABLE bookings DROP CONSTRAINT IF EXISTS bookings_no_overlap_active")

    op.drop_index("ix_email_deliveries_outbox_event_id", table_name="email_deliveries")
    op.drop_table("email_deliveries")

    op.drop_index("ix_outbox_events_aggregate", table_name="outbox_events")
    op.drop_index("ix_outbox_events_status_next_retry", table_name="outbox_events")
    op.drop_table("outbox_events")

    op.drop_index("ix_booking_participants_booking_id", table_name="booking_participants")
    op.drop_table("booking_participants")

    if not is_postgres:
        op.drop_index("ix_bookings_overlap_guard_fallback", table_name="bookings")
    op.drop_index("ix_bookings_room_time_window", table_name="bookings")
    op.drop_index("ix_bookings_organizer_user_id", table_name="bookings")
    op.drop_index("ix_bookings_room_id", table_name="bookings")
    op.drop_table("bookings")

    op.drop_index("ix_rooms_name", table_name="rooms")
    op.drop_table("rooms")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    outbox_event_type.drop(bind, checkfirst=True)
    outbox_status.drop(bind, checkfirst=True)
    booking_status.drop(bind, checkfirst=True)
