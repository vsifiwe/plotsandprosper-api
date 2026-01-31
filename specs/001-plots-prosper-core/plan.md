# Implementation Plan: Plots & Prosper Core Platform

**Branch**: `001-plots-prosper-core` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/001-plots-prosper-core/spec.md`

## Summary

Build a transparent, immutable digital mirror of the Plots & Prosper savings and investment group: member financial position, monthly contributions (with penalties kept separate), investment holdings and asset conversion with value-at-moment recording, exit queue and buy-out paths, and shared reference with external records as source of truth. The backend is a Django 5.x + DRF API on Python 3.12 with PostgreSQL 16, append-only ledger (immutable records + reversal-only corrections), and Docker deployment.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Django 5.x, Django REST Framework  
**Storage**: PostgreSQL 16  
**Testing**: pytest, Django test client, DRF APITestCase  
**Target Platform**: Linux server (Docker)  
**Project Type**: backend (API only; frontend out of scope)  
**Performance Goals**: Administrator can complete a month’s contribution run for 50+ members in under 10 minutes; member position view reproducible deterministically from ledger  
**Constraints**: All monetary and percentage values use decimal precision; no floating-point for money; forward-only migrations; no edits/deletes of financial records  
**Scale/Scope**: Single group; 50+ members; contribution windows, investments, assets, exit queue, buy-outs

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Immutable ledger with reversal-only corrections for financial records.
- Service-layer business logic; API views remain thin and deterministic.
- JWT RBAC with member/admin/auditor permissions and strict least privilege.
- DRF versioned endpoints with frozen OpenAPI contract for frontend.
- Mandatory tests for critical paths and deterministic aggregation logic.
- Precision decimals and DB constraints for all financial values.

## Project Structure

### Documentation (this feature)

```text
specs/001-plots-prosper-core/
├── plan.md              # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/            # Phase 1 output (OpenAPI)
└── tasks.md              # Phase 2 output (/speckit.tasks - not created by plan)
```

### Source Code (repository root)

```text
api/                      # Django project (settings, urls, wsgi/asgi)
├── settings.py
├── urls.py
└── ...

common/                   # Shared app: models, services, API
├── models/
├── services/
├── views/
├── urls.py
├── admin.py
└── migrations/

manage.py
requirements.txt
Dockerfile
docker-compose.yml
.env.example

tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Single Django project with one shared app (`common`) for core domain (members, contributions, penalties, windows, holdings, assets, exits, buy-outs, reversals). Additional apps (e.g. `ledger`, `members`) may be introduced in Phase 1 if boundaries warrant. API versioning under `/api/v1/`. Business logic in `common/services/` and model managers; views are thin.

## Complexity Tracking

> No constitution violations. All gates satisfied by design (immutable ledger, service layer, JWT RBAC, DRF + OpenAPI, decimal precision, mandatory tests).

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| *(none)* | — | — |
