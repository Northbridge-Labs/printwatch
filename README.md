# PrintWatch

Printer management & print job logging platform (similar to PaperCut).
Captures print/scan/copy jobs from CUPS (Linux/macOS) and Windows spoolers,
stores them in PostgreSQL, computes cost, enforces quotas, raises alerts,
and exposes a developer API for third-party printer apps to log jobs.

## Stack

- **Backend**: Python 3.12, Django 5, DRF, SimpleJWT, drf-spectacular
- **Architecture**: modular monolith — one Django app per bounded context
  (`accounts`, `printers`, `jobs`, `quotas`, `reporting`, `alerts`, `ingest`)
- **Layering** (per app): View → Service → Repository → Model, with
  framework-agnostic `domain/` records + interfaces (Protocols). SOLID,
  Strategy/Factory/Repository/Facade/Chain-of-Responsibility/Adapter/Command
  patterns, minimal custom DI container.
- **Cache / broker**: Valkey
- **DB**: PostgreSQL 16
- **Async**: Celery + beat
- **Ingest**: ZeroMQ PUSH/PULL — native agents PUSH frames to a
  `zmq-consumer` daemon that adapts them to the internal ingest API.
- **Frontend**: React 18 + TypeScript + Vite + Material UI

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service | Port | Purpose |
|---|---|---|
| `db` | 5432 | PostgreSQL |
| `cache` | 6379 | Valkey |
| `backend` | 8000 | DRF + Swagger |
| `zmq-consumer` | 5558 | ZeroMQ PULL → ingest API |
| `worker` | — | Celery worker |
| `beat` | — | Celery beat (periodic alerts/quota recompute) |
| `frontend` | 5173 | Vite dev server |

First run:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

Open:

- Frontend: http://localhost:5173
- API + Swagger: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

## API surface

### Internal (not in Swagger)

- `POST /api/ingest/jobs` — used by the zmq-consumer (header `X-Ingest-Token`).

### Admin / user (JWT)

- `POST /api/auth/login`, `/api/auth/refresh`, `GET /api/auth/me`
- `GET/POST /api/printers`, `/api/printers/<id>`
- `GET/POST /api/departments`, `/api/departments/<id>`
- `GET /api/jobs`, `/api/jobs/<id>`
- `GET/POST /api/quotas/rules`, `/api/quotas/rules/<id>`, `GET /api/quotas/usage`
- `GET/POST /api/alerts/rules`, `/api/alerts/rules/<id>`, `GET /api/alerts/events`
- `GET /api/reporting/{summary,pages-by-user,pages-by-printer,jobs-by-type,cost-trend}`
- `GET/POST /api/developer-tokens`, `POST /api/developer-tokens/<id>/revoke`

### Developer (versioned, in Swagger under "Developer API")

- `POST /api/v1/jobs/log` — log a print/scan/copy job. Auth: long-lived
  developer JWT (Bearer). Throttled 60/min. Synchronous 201 response.

Mint a developer token from the admin UI ("Developer Tokens" page) or
`POST /api/developer-tokens` — the JWT is returned once.

## Native agents

### CUPS filter (Linux/macOS)

```bash
sudo agents/cups_filter/install.sh
sudo lpadmin -p <queue> -o cupsFilter='application/vnd.cups-pdf:pwfilter'
```

See `agents/cups_filter/README.md`.

### Windows print processor

Build the C++ DLL with MSVC (see `agents/windows/print_processor/README.md`),
register the print processor, then install the Python service:

```powershell
pip install -r agents/windows/agent/requirements.txt
python agents/windows/agent/install_service.py install
python agents/windows/agent/install_service.py start
```

## Architecture notes

- **SOLID**: each layer has a single responsibility; services depend on
  Protocols, not ORM. New job types/sources are added by registering a new
  Strategy, without modifying existing code (OCP).
- **Patterns**:
  - *Strategy* — `CostStrategy` (per `job_type`), `IngestionProcessor` (per source)
  - *Factory* — `CostStrategyFactory`, `IngestionProcessorFactory`
  - *Repository* — `Django*Repository` per app
  - *Service Layer* — business logic in `services/`
  - *Facade* — `JobIngestionFacade` (single entry used by REST + zmq consumer)
  - *Adapter* — `zmq-consumer` adapts wire JSON → internal API
  - *Chain of Responsibility* — post-ingest pipeline (quota → alert)
  - *Command* — Celery tasks
- **DI**: tiny custom container in `apps/common/container.py`. Apps register
  their services in `containers.py`, wired in `AppConfig.ready()`.
- **Events**: direct calls in the facade (no signals, no event bus) —
  explicit and easy to trace.

## Testing

```bash
docker compose exec backend pytest
```

Unit tests for services run without a database (services depend on
injected interfaces, fakes are used in tests). Integration tests run
against a test PostgreSQL.

## Developer integration guide

1. Get an admin to mint a developer token (Dashboard → Developer Tokens).
2. Use the token as `Authorization: Bearer <token>`.
3. `POST /api/v1/jobs/log` with the JSON body documented in Swagger.
4. Inspect the full schema at `/api/schema/` for client codegen
   (`openapi-generator-cli generate -i http://localhost:8000/api/schema/ -g typescript-axios`).

## License

MIT.