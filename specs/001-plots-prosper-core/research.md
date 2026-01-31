# Research: Plots & Prosper Core Platform

**Branch**: 001-plots-prosper-core  
**Date**: 2026-01-31

## Technical Stack (from user input)

| Area | Decision | Rationale |
|------|----------|-----------|
| Framework | Django 5.x + Django REST Framework | Matches constitution (DRF, versioned API); mature ORM and admin; policy-driven config. |
| Language | Python 3.12 | LTS-style support; decimal and typing align with financial correctness. |
| Database | PostgreSQL 16 | ACID, decimal/numeric types, constraints, JSON if needed for policy. |
| Auth | JWT (e.g. djangorestframework-simplejwt) | Constitution requires JWT-backed RBAC; stateless, versioned API–friendly. |
| API contract | OpenAPI 3.x (e.g. drf-spectacular) | Frozen contract for frontend; versioned endpoints under `/api/v1/`. |
| Deployment | Docker | User-specified; reproducible; env-based config. |

## Append-only ledger

- **Decision**: All financial events (contributions, penalties, investment allocations, asset conversions, exits, buy-outs) are stored as immutable rows. Corrections are only reversal or adjustment records that reference the original; originals are never updated or deleted.
- **Rationale**: Constitution and spec require full audit trail and “external records as source of truth”; append-only guarantees reproducibility and dispute resolution.
- **Alternatives considered**: Soft deletes or status flags were rejected because they allow “editing” history; only explicit reversal records preserve intent.

## Decimal precision

- **Decision**: All monetary amounts and ownership percentages use `DecimalField` (Django) / `NUMERIC` (PostgreSQL) with explicit precision (e.g. 20 digits, 4 decimal places for currency). No `FloatField` or float math for money.
- **Rationale**: Constitution and FR-005 require financial accuracy and deterministic computation; floats introduce rounding errors.
- **Alternatives considered**: Float rejected; integer cents possible but decimals keep clarity for percentages and mixed units.

## RBAC roles

- **Decision**: Three roles—member, administrator, auditor. Members: read own data + group aggregates. Administrators: governed data entry and reconciliation (create contributions, penalties, investments, assets, exits, buy-outs, reversals). Auditors: read-only + optional issue-flagging (no write to financial data).
- **Rationale**: Matches constitution and spec FR-004; least privilege and audit support.

## Versioning and OpenAPI

- **Decision**: API under `/api/v1/`; OpenAPI spec generated (e.g. drf-spectacular) and treated as frozen contract for frontend; breaking changes require new version (e.g. v2).
- **Rationale**: Constitution requires versioned, documented API; frozen contract reduces drift.

## Policy-driven config

- **Decision**: Contribution windows (boundaries, deadlines), late consequences, exit entitlement, buy-out valuation formula are configurable via DB or env-backed config (e.g. settings or small policy tables), not hardcoded.
- **Rationale**: Constitution and spec assume group-defined policy; system enforces/reflects it.

## NEEDS CLARIFICATION resolved

- None; user provided full stack (Django 5.x, DRF, Python 3.12, PostgreSQL 16, append-only ledger, Docker).
