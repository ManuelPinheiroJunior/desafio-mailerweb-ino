# Backend

Backend service for the meeting room booking system.

## Quick start

1. Create a virtual environment and install dependencies:
   - `pip install -e .[dev]`
2. Copy `.env.example` to `.env` and adjust values.
3. Run API:
   - `uvicorn app.main:app --reload`
4. Run worker:
   - `python -m app.workers.outbox_worker`
5. Run tests:
   - `pytest -q`

## Docker

From repository root:

- `docker compose up --build`

Backend container runs migrations on startup before launching the API.

## Current stage

Current implementation status:
- FastAPI API with JWT authentication
- Layered architecture (api/application/domain/infrastructure)
- SQLAlchemy + Alembic schema for rooms/bookings/outbox
- Transactional outbox publication on booking create/update/cancel
- Outbox repository primitives prepared for async worker polling
- Worker with polling, retry/backoff, and delivery idempotency

## API endpoints currently available

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/rooms`
- `POST /api/v1/rooms` (admin token required)
- `GET /api/v1/bookings`
- `GET /api/v1/bookings/{booking_id}`
- `POST /api/v1/bookings`
- `PUT /api/v1/bookings/{booking_id}`
- `POST /api/v1/bookings/{booking_id}/cancel`
