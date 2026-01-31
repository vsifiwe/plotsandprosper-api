# Tasks: Plots & Prosper Core Platform

**Input**: Design documents from `specs/001-plots-prosper-core/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: REQUIRED for constitution-defined critical paths (contribution windows, penalties, NAV application, asset acquisition, exit queue, buy-out). Tasks include contract and integration tests for those flows.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `api/`, `common/`, `manage.py`, `tests/` at repository root
- **Models**: `common/models/`
- **Services**: `common/services/`
- **Views**: `common/views/`
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify project structure per plan (api/, common/, manage.py, tests/unit, tests/integration, tests/contract) and add tests directories if missing
- [X] T002 Add Django 5.x, djangorestframework, psycopg[binary], djangorestframework-simplejwt, drf-spectacular to requirements.txt at repository root
- [X] T003 [P] Configure ruff (or black/isort) in pyproject.toml or setup.cfg at repository root
- [X] T004 [P] Add .env.example at repository root with DATABASE_URL, SECRET_KEY, DEBUG
- [X] T005 [P] Add Dockerfile and docker-compose.yml at repository root for app and PostgreSQL 16

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Configure PostgreSQL 16 in api/settings.py (DATABASES default, ENGINE django.db.backends.postgresql)
- [X] T007 Ensure common app has migrations package and run python manage.py makemigrations common (no new models yet if none added)
- [X] T008 [P] Add rest_framework and rest_framework_simplejwt to INSTALLED_APPS and configure JWT settings in api/settings.py
- [X] T009 [P] Add drf_spectacular to INSTALLED_APPS and set DEFAULT_SCHEMA_CLASS in api/settings.py; add schema URL in api/urls.py
- [X] T010 Mount /api/v1/ in api/urls.py and include common.urls for API routes
- [X] T011 Ensure Member model in common/models/member.py has role/roles and display_name (or firstName/lastName) for position; use DecimalField for any money fields if added
- [X] T012 Implement RBAC permission classes in common/permissions.py (IsMemberReadOwnAndAggregates, IsAdmin, IsAuditorReadOnly) using Member.roles
- [X] T013 Configure REST_FRAMEWORK authentication (JWT) and default permission classes in api/settings.py
- [X] T014 [P] Contract test for POST /api/v1/auth/token/ in tests/contract/test_auth.py (obtain JWT)
- [X] T015 Configure structured error handling and logging in api/settings.py (LOGGING)

**Checkpoint**: Foundation ready — auth, API versioning, OpenAPI, and RBAC in place; user story implementation can begin

---

## Phase 3: User Story 1 — Member Views Own Financial Position (Priority: P1) 🎯 MVP

**Goal**: Member sees single view of contributions (savings + penalties), holdings share, asset share, exit/buy-out status; only own data + group aggregates.

**Independent Test**: Member can GET /me/position/ and GET /group/aggregates/ and see correct totals and disclaimer; no other members’ data.

### Tests for User Story 1 (REQUIRED for critical path: position view)

- [X] T016 [P] [US1] Integration test for member position in tests/integration/test_member_position.py (authenticated member GET /me/position/, GET /group/aggregates/, RBAC)
- [X] T017 [P] [US1] Contract test for GET /api/v1/me/position/ in tests/contract/test_me_position.py (response schema, 403 when unauthenticated)

### Implementation for User Story 1

- [X] T018 [US1] Create ContributionWindow model in common/models/contribution_window.py (start_at, end_at, min_amount, max_amount, name; decimal for amounts)
- [X] T019 [US1] Create Contribution model in common/models/contribution.py (member FK, window FK, amount DecimalField(max_digits=20, decimal_places=4), recorded_at, created_at; immutable)
- [X] T020 [US1] Create Penalty model in common/models/penalty.py (member FK, amount DecimalField, reason, window_id nullable, recorded_at, created_at; immutable)
- [X] T021 [US1] Implement PositionService in common/services/position_service.py (get_member_position: aggregate contributions and penalties for member; get_group_aggregates: total members, total pool)
- [X] T022 [US1] Implement GET /me/position/ in common/views/position_views.py (thin: call PositionService, return JSON with source_of_truth_disclaimer)
- [X] T023 [US1] Implement GET /group/aggregates/ in common/views/group_views.py (thin: call PositionService.get_group_aggregates)
- [X] T024 [US1] Wire /me/position/ and /group/aggregates/ under /api/v1/ in common/urls.py with permission IsMemberReadOwnAndAggregates
- [X] T025 [US1] Register Contribution, Penalty, ContributionWindow in common/admin.py (read-only or minimal create for data entry)

**Checkpoint**: User Story 1 complete — member can view position (contributions, penalties) and group aggregates; independently testable

---

## Phase 4: User Story 2 — Monthly Contribution Process (Priority: P2)

**Goal**: Record contributions within windows, penalties separate, record investment at date/value, reversal-only corrections.

**Independent Test**: Admin records contribution and penalty, then investment; positions update deterministically; correction only via reversal.

### Tests for User Story 2 (REQUIRED for critical paths: contribution window, penalties, NAV application)

- [X] T026 [P] [US2] Integration test for contribution flow in tests/integration/test_contribution_flow.py (record contribution, penalty, investment; verify position and no edit/delete)
- [X] T027 [P] [US2] Contract test for POST /api/v1/admin/contributions/ and POST /api/v1/admin/penalties/ in tests/contract/test_admin_contributions.py
- [X] T028 [P] [US2] Contract test for POST /api/v1/admin/investments/ in tests/contract/test_admin_investments.py

### Implementation for User Story 2

- [X] T029 [US2] Create Investment model in common/models/investment.py (recorded_at date, unit_value DecimalField, total_units nullable, created_at, created_by FK nullable)
- [X] T030 [US2] Create HoldingShare model in common/models/holding_share.py (investment FK, member FK, units DecimalField, created_at; immutable)
- [X] T031 [US2] Create Reversal model in common/models/reversal.py (original_record_type, original_record_id, reason nullable, created_at, created_by FK nullable)
- [X] T032 [US2] Implement ContributionRecordingService in common/services/contribution_service.py (record_contribution, record_penalty; validate window and boundaries)
- [X] T033 [US2] Implement InvestmentRecordingService in common/services/investment_service.py (record_investment: compute member shares from eligible savings at that date, create HoldingShare rows)
- [X] T034 [US2] Implement GET and POST /admin/contribution-windows/ in common/views/admin_views.py (admin only)
- [X] T035 [US2] Implement POST /admin/contributions/ and POST /admin/penalties/ in common/views/admin_views.py (admin only; thin, call services)
- [X] T036 [US2] Implement POST /admin/investments/ in common/views/admin_views.py (admin only; thin, call InvestmentRecordingService)
- [X] T037 [US2] Implement POST /admin/reversals/ in common/views/admin_views.py (admin only; create Reversal record only)
- [X] T038 [US2] Update PositionService in common/services/position_service.py to include holdings (HoldingShare × unit_value) in member position
- [X] T039 [US2] Exclude reversed records in PositionService and ContributionRecordingService (aggregate only non-reversed contributions/penalties/holdings)
- [X] T040 [US2] Wire admin endpoints under /api/v1/admin/ in common/urls.py with IsAdmin permission

**Checkpoint**: User Story 2 complete — contribution process, penalties separate, investment at value, reversal-only corrections; independently testable

---

## Phase 5: User Story 3 — Investment Journey and Asset Conversion (Priority: P3)

**Goal**: Members see savings → holdings → assets; ownership fixed at conversion; no speculative revaluation.

**Independent Test**: Member traces contributions → holdings → asset share; ownership percentage and recorded value visible.

### Tests for User Story 3 (REQUIRED for critical path: asset acquisition)

- [X] T041 [P] [US3] Integration test for asset conversion in tests/integration/test_asset_conversion.py (record asset with shares; position shows asset share and recorded value)

### Implementation for User Story 3

- [X] T042 [US3] Create Asset model in common/models/asset.py (name, recorded_purchase_value DecimalField, conversion_at date, source_investment_id FK nullable, created_at, created_by FK nullable)
- [X] T043 [US3] Create AssetShare model in common/models/asset_share.py (asset FK, member FK, share_percentage DecimalField, created_at; immutable)
- [X] T044 [US3] Implement AssetConversionService in common/services/asset_service.py (record_asset: create Asset and AssetShare rows from agreed rule e.g. proportional to holdings at conversion)
- [X] T045 [US3] Implement POST /admin/assets/ in common/views/admin_views.py (admin only; thin, call AssetConversionService)
- [X] T046 [US3] Update PositionService in common/services/position_service.py to include assets_breakdown (AssetShare with recorded_purchase_value) in member position
- [X] T047 [US3] Wire POST /admin/assets/ under /api/v1/admin/ in common/urls.py; add Asset, AssetShare to common/admin.py

**Checkpoint**: User Story 3 complete — investment journey and asset conversion with fixed ownership; independently testable

---

## Phase 6: User Story 4 — Exit and Buy-Out Paths (Priority: P4)

**Goal**: Exit request and queue; buy-out with nominal valuation; immutable records only.

**Independent Test**: Member requests exit (queue position); admin records buy-out; position shows exit status and entitlement.

### Tests for User Story 4 (REQUIRED for critical paths: exit queue, buy-out transfers)

- [ ] T048 [P] [US4] Integration test for exit queue and buy-out in tests/integration/test_exit_buyout.py (create exit request, fulfill or queue; record buy-out; verify position and audit trail)
- [ ] T049 [P] [US4] Contract test for POST /api/v1/admin/exit-requests/ and POST /api/v1/admin/buy-outs/ in tests/contract/test_admin_exit_buyout.py

### Implementation for User Story 4

- [ ] T050 [US4] Create ExitRequest model in common/models/exit_request.py (member FK, requested_at, queue_position int, status, fulfilled_at nullable, amount_entitled DecimalField, created_at)
- [ ] T051 [US4] Create BuyOut model in common/models/buy_out.py (seller FK, buyer FK nullable, nominal_valuation DecimalField, valuation_inputs JSONField or text, recorded_at, created_at, created_by FK nullable)
- [ ] T052 [US4] Implement ExitRequestService in common/services/exit_service.py (create exit request, assign queue_position e.g. FIFO; optional: fulfill when liquidity)
- [ ] T053 [US4] Implement BuyOutService in common/services/buyout_service.py (record buy-out, transfer ownership per policy; immutable)
- [ ] T054 [US4] Implement GET and POST /admin/exit-requests/ in common/views/admin_views.py (admin only)
- [ ] T055 [US4] Implement POST /admin/buy-outs/ in common/views/admin_views.py (admin only)
- [ ] T056 [US4] Update PositionService in common/services/position_service.py to include exit_request (status, queue_position, amount_entitled) in member position
- [ ] T057 [US4] Wire exit and buy-out endpoints under /api/v1/admin/ in common/urls.py; register ExitRequest, BuyOut in common/admin.py

**Checkpoint**: User Story 4 complete — exit and buy-out paths with deterministic, auditable records; independently testable

---

## Phase 7: User Story 5 — Shared Reference and Transparency (Priority: P5)

**Goal**: Statement export, source-of-truth disclaimer, auditor read-only.

**Independent Test**: Member exports statement; position response includes disclaimer; auditor cannot write financial data.

### Tests for User Story 5

- [ ] T058 [P] [US5] Integration test for statement export and disclaimer in tests/integration/test_statement_transparency.py (GET /me/statement/, disclaimer in /me/position/, auditor 403 on POST admin)

### Implementation for User Story 5

- [ ] T059 [US5] Implement StatementService in common/services/statement_service.py (get_member_statement: historical contributions, penalties, investments, exits for date range; deterministic)
- [ ] T060 [US5] Implement GET /me/statement/ in common/views/statement_views.py (query params from_date, to_date; return JSON; permission member own only)
- [ ] T061 [US5] Add source_of_truth_disclaimer field to /me/position/ response in common/views/position_views.py and document in contracts/openapi.yaml
- [ ] T062 [US5] Enforce auditor role read-only: ensure IsAuditorReadOnly denies POST/PUT/PATCH/DELETE on admin and write endpoints in common/permissions.py
- [ ] T063 [US5] Wire GET /me/statement/ under /api/v1/ in common/urls.py

**Checkpoint**: User Story 5 complete — transparency, statement export, and auditor read-only; independently testable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T064 [P] Update specs/001-plots-prosper-core/quickstart.md with final run/test steps and OpenAPI schema URL
- [ ] T065 Run full test suite (pytest or python manage.py test) and fix any failures
- [ ] T066 Security pass: ensure no PII in logs, JWT expiry and refresh configured, RBAC applied to all financial endpoints
- [ ] T067 Generate OpenAPI schema from drf-spectacular and compare to specs/001-plots-prosper-core/contracts/openapi.yaml; document any drift

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1)**: Depends on Phase 2 — MVP; no dependency on US2–US5
- **Phase 4 (US2)**: Depends on Phase 2; extends US1 position with holdings
- **Phase 5 (US3)**: Depends on Phase 2 and US2 (holdings); extends position with assets
- **Phase 6 (US4)**: Depends on Phase 2; extends position with exit/buy-out
- **Phase 7 (US5)**: Depends on Phase 2 and US1 (position/statement)
- **Phase 8 (Polish)**: Depends on completion of desired user stories

### User Story Dependencies

- **US1 (P1)**: After Foundational only — position with contributions/penalties (and later holdings/assets/exit as added in US2–US4)
- **US2 (P2)**: After Foundational — contribution process, investments, reversals; feeds US1 position (holdings)
- **US3 (P3)**: After US2 (holdings exist) — assets and asset shares; feeds US1 position (assets)
- **US4 (P4)**: After Foundational — exit and buy-out; feeds US1 position (exit_request)
- **US5 (P5)**: After US1 — statement and disclaimer; auditor enforcement

### Within Each User Story

- Tests (contract/integration) can be written in parallel where marked [P]; run and see fail before implementation
- Models before services; services before views; wire URLs last
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: T003, T004, T005 [P]
- Phase 2: T008, T009 [P]; T014 [P]
- Phase 3: T016, T017 [P]; T018–T020 (models) can be [P] if split across files
- Phase 4: T026, T027, T028 [P]; T029, T030, T031 (models) [P]
- Phase 5: T041 [P]; T042, T043 [P]
- Phase 6: T048, T049 [P]; T050, T051 [P]
- Phase 7: T058 [P]
- Phase 8: T064 [P]

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational  
3. Complete Phase 3: User Story 1  
4. **STOP and VALIDATE**: Test GET /me/position/ and GET /group/aggregates/ independently  
5. Deploy/demo if ready  

### Incremental Delivery

1. Setup + Foundational → foundation ready  
2. US1 → member position (contributions, penalties) → MVP  
3. US2 → contribution process, investments, reversals → full ledger  
4. US3 → assets → investment journey  
5. US4 → exit and buy-out → full lifecycle  
6. US5 → statement and transparency → compliance  
7. Polish → quickstart and security  

### Parallel Team Strategy

- Team completes Phase 1 and Phase 2 together  
- Then: Developer A — US1; Developer B — US2; Developer C — US3 (after US2 models); then US4, US5  
- Each story delivers an independently testable increment  

---

## Notes

- Every task includes a file path or explicit scope (e.g. api/settings.py, common/models/…).  
- [P] tasks are parallelizable (different files or no blocking dependency).  
- Constitution: immutable ledger, reversal-only corrections, JWT RBAC, DRF versioned API, decimal precision, mandatory tests for critical paths — all reflected in phases and task labels.  
- Commit after each task or logical group; run tests at each checkpoint.
