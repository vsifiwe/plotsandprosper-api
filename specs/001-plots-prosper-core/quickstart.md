# Quickstart: Plots & Prosper Backend

**Branch**: 001-plots-prosper-core  
**Date**: 2026-01-31

## Prerequisites

- Python 3.12
- PostgreSQL 16 (local or Docker)
- Docker and Docker Compose (for containerized run)

## Local development (no Docker)

1. **Clone and branch**
   - Ensure you are on branch `001-plots-prosper-core` (or set `SPECIFY_FEATURE=001-plots-prosper-core` if not using git).

2. **Virtual environment**
   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment**
   - Copy `.env.example` to `.env`.
   - Set `DATABASE_URL` (e.g. `postgres://user:pass@localhost:5432/plots_prosper`), `SECRET_KEY`, and any JWT/DRF settings.

4. **Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser   # optional, for admin
   ```

5. **Run server**
   ```bash
   python manage.py runserver
   ```
   - API base: `http://127.0.0.1:8000/api/v1/`
   - OpenAPI schema (drf-spectacular): `http://127.0.0.1:8000/api/schema/` (YAML)
   - Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
   - ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`

6. **Tests and lint**
   ```bash
   pytest
   ruff check .
   ```
   Or: `python manage.py test` for Django test runner.

## Docker

1. **Build and run**
   ```bash
   docker-compose up -d
   ```
   - App and PostgreSQL run as defined in `docker-compose.yml`.
   - Run migrations inside the app container: `docker-compose exec web python manage.py migrate`.

2. **API**
   - Base URL as configured (e.g. `http://localhost:8000/api/v1/`).

## Constitution / spec alignment

- All financial writes are immutable; corrections only via reversal records.
- Use decimal precision for money; no float.
- JWT RBAC: member (own + aggregates), admin (governed data entry), auditor (read-only).
- API versioned under `/api/v1/`; OpenAPI contract in `specs/001-plots-prosper-core/contracts/openapi.yaml`.

## Validation

- After implementation, run tests for critical paths (contribution windows, penalties, NAV application, asset conversion, exit queue, buy-out).
- Confirm member position is reproducible from ledger (contributions, penalties, holdings, assets, exits, buy-outs).

## Final run/test steps

1. From repo root: `pip install -r requirements.txt` (if not already).
2. `python manage.py migrate`
3. `pytest` — run full test suite (unit, integration, contract).
4. `ruff check .` — lint (api, common, tests).
5. Optional: `python manage.py spectacular --file /tmp/schema.yaml` to export OpenAPI; compare with `specs/001-plots-prosper-core/contracts/openapi.yaml` for drift (see Schema drift below).

## Schema drift (T067)

To generate the live OpenAPI schema from drf-spectacular and compare to the contract:

```bash
python manage.py spectacular --file /tmp/generated-schema.yaml
diff specs/001-plots-prosper-core/contracts/openapi.yaml /tmp/generated-schema.yaml
```

Document any intentional drift (e.g. extra endpoints or schema extensions) in `specs/001-plots-prosper-core/contracts/` or in this quickstart. The contract `openapi.yaml` is the versioned API reference for frontend integration.

## Security (T066)

- **JWT**: Access token lifetime 60 minutes, refresh 7 days (configurable via `SIMPLE_JWT_*` in settings or env).
- **RBAC**: All financial endpoints use `IsAuthenticated` plus `IsAdmin` (admin/write) or `IsMemberReadOwnAndAggregates` (member read own + aggregates). Auditor has no write access.
- **Logging**: Default formatters do not include request bodies or PII; ensure custom loggers do not log passwords, tokens, or full request payloads.
