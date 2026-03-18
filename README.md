# Meeting Room Booking System

Sistema Fullstack para gestão de reservas de salas de reunião com notificações assíncronas por e-mail usando **Transactional Outbox + Worker**.

## Stack

- Backend: Python 3.10+, FastAPI, SQLAlchemy 2.0, Alembic
- Banco: PostgreSQL (produção) / SQLite (desenvolvimento e testes locais)
- Auth: JWT Bearer
- Frontend: Next.js (App Router) + TypeScript
- Testes backend: Pytest
- Testes frontend: Vitest + Testing Library

## Arquitetura

Monorepo com separação clara entre backend e frontend:

```text
backend/
  app/
    api/              # controllers HTTP + schemas + dependências auth
    application/      # casos de uso, DTOs e portas (interfaces)
    domain/           # entidades, value objects e regras de negócio
    infrastructure/   # ORM, repositórios SQLAlchemy, adapters de e-mail
    workers/          # worker do outbox
  alembic/
  tests/

frontend/
  src/
    app/              # páginas Next.js
    components/       # componentes client-side
    lib/              # auth local + API client
    tests/            # testes unitários e integração
```

### Camadas backend

- **Domain**: invariantes de reserva (janela de tempo, status, permissões e normalização de participantes).
- **Application**: `BookingAppService` orquestra create/update/cancel e publica eventos no outbox.
- **Infrastructure**: implementação dos repositórios, UoW, ORM e envio de e-mail.
- **API**: endpoints FastAPI, autenticação JWT e mapeamento de erros para HTTP.

## Modelagem de dados

Tabelas principais:

- `users`
- `rooms` (nome único, capacidade > 0)
- `bookings` (ativa/cancelada, `start_at < end_at`)
- `booking_participants` (unique por `booking_id + email`)
- `outbox_events` (estado do evento, tentativas, retry, idempotency_key única)
- `email_deliveries` (idempotência por destinatário: unique `outbox_event_id + recipient_email`)

## Estratégia de concorrência

A proteção principal contra conflito de reservas simultâneas está no banco com:

- **PostgreSQL Exclusion Constraint** em `bookings`
- Regra de overlap: `new_start < existing_end AND new_end > existing_start`
- Range `[)` para permitir reuniões “encostadas” (sem overlap)
- Constraint parcial para considerar somente reservas `ACTIVE`

Constraint aplicada na migration inicial:

- `bookings_no_overlap_active` usando `EXCLUDE USING gist`
- extensão `btree_gist`

Isso garante consistência mesmo com múltiplas instâncias da API e requisições concorrentes.

## Outbox + Worker

### Transactional Outbox

Nos casos de uso de reserva (create/update/cancel), dentro da **mesma transação**:

1. Persiste mudança em `bookings`
2. Persiste evento em `outbox_events`
3. Commit único

Eventos suportados:

- `BOOKING_CREATED`
- `BOOKING_UPDATED`
- `BOOKING_CANCELED`

### Worker assíncrono

`app/workers/outbox_worker.py`:

- Busca eventos elegíveis em lote (`PENDING` e `PROCESSING` stale)
- Claim com `FOR UPDATE SKIP LOCKED`
- Envia e-mails (texto simples com título, sala, horário e tipo de evento)
- Marca evento como `PROCESSED`
- Em falha, aplica retry com backoff exponencial
- Ao atingir limite, marca `FAILED`
- Idempotência por destinatário via tabela `email_deliveries`

## Regras de domínio implementadas

- Datas com timezone obrigatório (ISO 8601)
- `start_at < end_at`
- Duração mínima de 15 minutos
- Duração máxima de 8 horas
- Sem overlap de reservas ativas na mesma sala
- Reservas canceladas não são removidas (soft-state por status)
- Apenas organizador (ou admin) pode alterar/cancelar reserva

## API (resumo)

Base: `/api/v1`

- `POST /auth/register`
- `POST /auth/login`
- `GET /rooms`
- `GET /rooms/{room_id}`
- `POST /rooms` (admin)
- `GET /bookings`
- `GET /bookings/{booking_id}`
- `POST /bookings`
- `PUT /bookings/{booking_id}`
- `POST /bookings/{booking_id}/cancel`

Erros relevantes:

- `409` para conflito de horário
- `403` para permissão
- `404` para recurso inexistente
- `422` para validação de domínio

## Como rodar

### Docker Compose (recomendado)

Da raiz do projeto:

```bash
docker compose up --build
```

Serviços:

- API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
copy .env.example .env
```

Rodar migrações:

```bash
alembic upgrade head
```

Subir API:

```bash
uvicorn app.main:app --reload
```

Subir worker:

```bash
python -m app.workers.outbox_worker
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

## Variáveis de ambiente

### Backend (`backend/.env`)

- `APP_NAME`
- `ENVIRONMENT`
- `DEBUG`
- `API_V1_PREFIX`
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `JWT_EXPIRE_MINUTES`
- `ADMIN_EMAIL`
- `WORKER_POLL_INTERVAL_SECONDS`
- `WORKER_BATCH_SIZE`
- `WORKER_MAX_BACKOFF_SECONDS`
- `WORKER_PROCESSING_TIMEOUT_SECONDS`
- `EMAIL_SENDER_ADDRESS`

### Frontend (`frontend/.env.local`)

- `NEXT_PUBLIC_API_BASE_URL`

## Testes

### Backend

```bash
cd backend
pytest -q
```

Cobertura atual inclui:

- validação de datas
- conflito de reserva
- permissões
- criação de evento no outbox
- processamento pelo worker
- idempotência de envio
- cenário concorrente (unitário com corrida simulada)
- cenário concorrente real em Postgres (`tests/integration/test_concurrency_postgres.py`)

### Frontend

```bash
cd frontend
npm test
```

Cobertura atual inclui:

- fluxo de login
- criação de reserva
- exibição de erro de conflito (`409`)
- integração do client com contrato HTTP (headers/body)
- integração real com backend (opcional via `FRONTEND_E2E_API_BASE_URL`)

### Testes opcionais de ambiente real

- Backend concorrência real:
  - defina `TEST_POSTGRES_URL`
  - rode `pytest -q`
- Frontend contra backend real:
  - defina `FRONTEND_E2E_API_BASE_URL` (ex: `http://localhost:8000/api/v1`)
  - rode `npm test`

## Próximas evoluções recomendadas

- E2E frontend/backend com Playwright
- Métricas e observabilidade no worker (latência, retries, DLQ)
- Provider SMTP/SES real no lugar do sender de console
- Refresh token e hardening adicional de autenticação
