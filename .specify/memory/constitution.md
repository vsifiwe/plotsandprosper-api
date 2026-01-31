<!--
Sync Impact Report
Version change: N/A (template) → 1.0.0
Modified principles: N/A (initial adoption)
Added sections: Core Principles, Operational & Performance Standards, Workflow & Quality Gates, Governance (initialized)
Removed sections: N/A
Templates requiring updates: ✅ .specify/templates/plan-template.md; ✅ .specify/templates/spec-template.md; ✅ .specify/templates/tasks-template.md
Follow-up TODOs: TODO(RATIFICATION_DATE): original adoption date unknown
-->
# Plots & Prosper Backend Constitution

## Core Principles

### Reality-Mirroring, Immutable Ledger
All financial records are immutable. Contributions, penalties, RNIT holdings, asset
allocations, exits, and buy-outs MUST never be edited or deleted once recorded.
Corrections occur only through explicit reversal records that preserve the
historical truth, and external bank statements and RNIT records are the ultimate
source of truth in disputes.
Rationale: Ensures auditability, traceability, and trust in every balance.

### Domain Boundaries & Precision Accounting
Django models MUST enforce strict domain boundaries with database-level
constraints and high-precision decimals. No floating-point math is permitted for
financial values, and invariants must be captured in model constraints or
validated in services before persistence.
Rationale: Financial correctness is non-negotiable and must be enforced by design.

### Deterministic Service-Layer Logic
Business rules belong in service layers or model managers, not in views. APIs
MUST remain thin, deterministic, and focused on orchestration and I/O, with
domain logic implemented in dedicated services that are independently testable.
Rationale: Keeps policy centralized and behavior predictable.

### Strict RBAC with JWT
Authentication and authorization MUST use JWT-backed role-based access control.
Members can only access their own financial standing and group aggregates;
administrators perform governed data entry and reconciliation; auditors are
read-only with issue-flagging capabilities.
Rationale: Least privilege protects member data and supports independent audits.

### Versioned, Documented, Tested Interfaces
All API endpoints MUST use Django REST Framework, follow REST conventions, be
versioned, and be documented in an OpenAPI specification that serves as a frozen
contract for frontend development. Critical paths MUST ship with automated tests
covering happy paths and defined edge cases.
Rationale: Contract clarity prevents drift and enforces correctness.

## Operational & Performance Standards

- Query efficiency must be actively managed using Django ORM best practices.
- Aggregation logic MUST be deterministic and testable.
- Reconciliation checks, alerts, and other background work MUST run asynchronously.
- The system must present itself as a transparent mirror of reality, not a
  replacement for external financial systems.

## Workflow & Quality Gates

- Testing is mandatory for all critical paths, including contribution windows,
  penalties, NAV application, asset acquisition snapshots, exit queues, and
  buy-out transfers.
- Configurations MUST be policy-driven rather than code-driven.
- Migrations must be clean, forward-only, and never rewrite historical records.
- Security defaults must be strict; access reviews are required for changes to
  authentication or authorization.
- Every design decision must favor clarity, auditability, and long-term
  maintainability.

## Governance

- This constitution supersedes all other development guidance.
- Amendments require a documented rationale, impact assessment, and a migration
  plan where behavior or data constraints change.
- Versioning follows semantic versioning: MAJOR for breaking policy changes,
  MINOR for new or expanded principles/sections, PATCH for clarifications.
- All specifications and plans MUST include a constitution compliance check.
- Compliance is reviewed during code review and at release readiness.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date unknown | **Last Amended**: 2026-01-31
