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
   - OpenAPI schema: `http://127.0.0.1:8000/api/schema/` (if drf-spectacular is configured).

6. **Tests**
   ```bash
   pytest
   # or
   python manage.py test
   ```

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
