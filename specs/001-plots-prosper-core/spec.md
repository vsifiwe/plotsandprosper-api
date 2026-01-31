# Feature Specification: Plots & Prosper Core Platform

**Feature Branch**: `001-plots-prosper-core`  
**Created**: 2026-01-31  
**Status**: Draft  
**Input**: Transparent digital mirror of the Plots & Prosper savings and investment group: member financial position, monthly contributions, penalties separate from investments, investment journey and asset conversion, exit and buy-out paths, shared reference with external records as source of truth.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Member Views Own Financial Position (Priority: P1)

A member can see a single, clear view of their financial position within the group: how much they have contributed over time, how those contributions were applied (savings vs. penalties), what share of group investment holdings they have, and where they stand in any exit or buy-out process. The member sees only their own data plus group-level aggregates; they never see other members’ private details.

**Why this priority**: Without visibility into their own position, members cannot trust or use the system. This is the foundation for all other flows.

**Independent Test**: A member can log in, open “My position,” and verify that contribution history, current holdings share, and any queue position match their expectations and external records.

**Acceptance Scenarios**:

1. **Given** a member is authenticated, **When** they open their financial position, **Then** they see their total contributions over time, split by savings and penalties.
2. **Given** a member has investment holdings, **When** they view their position, **Then** they see their share of group holdings and how it was determined (e.g., at time of investment).
3. **Given** a member is in an exit or buy-out queue, **When** they view their position, **Then** they see their status and what they are entitled to (e.g., return of contributions when liquid, or buy-out terms).
4. **Given** any member, **When** they view the group, **Then** they see only group-level aggregates (e.g., total pool, total members) and never other members’ individual balances or identity-linked details.

---

### User Story 2 - Monthly Contribution Process (Priority: P2)

The group runs a formal monthly contribution process. Members contribute within agreed boundaries (amounts and timing). Late or out-of-bound participation is recorded separately as penalties; penalties do not dilute or inflate anyone’s investment position. When funds are actually invested, the system records the moment and the value at that moment, so growth and ownership are based on objective conditions, not averages or assumptions.

**Why this priority**: The contribution process is the primary recurring event; getting it right (and keeping penalties separate) is essential for fairness and trust.

**Independent Test**: An administrator records a month’s contributions and penalties, then records an investment event with a given value; members’ positions update deterministically and can be reproduced from the recorded ledger.

**Acceptance Scenarios**:

1. **Given** a contribution window is open, **When** a member’s contribution is recorded within the agreed boundaries, **Then** it is recorded as savings and appears in their contribution history and in group totals.
2. **Given** a member contributes late or outside boundaries, **When** the administrator records it, **Then** it is recorded as a penalty (or late fee) and is kept separate from investment-eligible savings; it does not affect other members’ investment share.
3. **Given** funds are invested on a specific date, **When** the administrator records the investment with the value at that moment, **Then** each member’s share of the new holding is computed from their eligible savings at that time and the recorded value; the result is stored and never edited, only reversed by an explicit reversal record if needed.
4. **Given** any correction is required, **When** an authorized user requests it, **Then** the system creates only a reversal or adjustment record that references the original; the original record remains unchanged for audit.

---

### User Story 3 - Investment Journey and Asset Conversion (Priority: P3)

Members can see how the group’s collective savings become investment holdings and how those holdings are later converted into long-term assets through group decisions. Ownership percentages for assets are determined and fixed at the moment of purchase. The system does not revalue assets speculatively; value realization is through explicit group actions (e.g., sale, distribution), not through automatic mark-to-market.

**Why this priority**: Legibility of the investment journey reinforces trust and ensures everyone understands how holdings and assets were formed.

**Independent Test**: A member can trace a path from “my contributions” → “my share of holdings” → “my share of asset X” and see the dates and values at which each step was recorded.

**Acceptance Scenarios**:

1. **Given** a member has contributed and funds have been invested, **When** they view the investment journey, **Then** they see how their savings map to specific holdings and the value (and date) at which each allocation was made.
2. **Given** the group converts a holding into an asset (e.g., property purchase), **When** the conversion is recorded, **Then** each member’s ownership share of that asset is fixed at that moment based on the agreed rule (e.g., proportional to holdings at conversion); that share is not changed by later revaluations.
3. **Given** an asset exists, **When** a member views it, **Then** they see their ownership percentage and the recorded purchase value (or nominal value used for buy-outs), not a speculative current market value unless the group has explicitly recorded a new valuation event.

---

### User Story 4 - Exit and Buy-Out Paths (Priority: P4)

Members can leave or transfer ownership in a governed way. Early exit entitles the member only to the return of their own contributions (and any agreed realized portion), and only when liquidity allows. Buy-outs are supported as a fair alternative: ownership can be transferred using a nominal, non-speculative valuation (e.g., based on contributions, realized investment growth, and recorded asset value), so that new participants can assume obligations and benefits without negotiation asymmetry or opportunistic pricing.

**Why this priority**: Clear exit and buy-out rules protect both the individual and the group and reduce conflict.

**Independent Test**: A member requests exit or buy-out; the system applies the governed rules (liquidity, nominal valuation) and produces a deterministic outcome that can be audited.

**Acceptance Scenarios**:

1. **Given** a member requests early exit, **When** the group has liquidity to return contributions, **Then** the member receives only their contributed amount (and any agreed realized portion per policy); they do not receive a share of future upside.
2. **Given** a member requests early exit, **When** the group does not have liquidity, **Then** the member is placed in an exit queue and informed when funds become available; the system does not promise a date but records the request and queue position.
3. **Given** a buy-out is agreed, **When** the administrator records it, **Then** the valuation used is nominal and based on defined inputs (e.g., contributions, realized growth, recorded asset value); ownership is transferred to the buyer and the seller’s position is closed in an auditable way.
4. **Given** any exit or buy-out, **When** it is recorded, **Then** the system creates immutable records only; corrections are made via explicit reversal or adjustment records.

---

### User Story 5 - Shared Reference and Transparency (Priority: P5)

The system acts as a shared reference point, not an unquestionable authority. It gives members confidence that what they see reflects what has been recorded, while explicitly stating that external bank statements and investment records remain the ultimate source of truth in disputes. Members have access to their own records and group aggregates; the system supports transparency while respecting privacy and social boundaries.

**Why this priority**: This sets expectations and prevents the platform from replacing human judgment and external verification.

**Independent Test**: A member can confirm that their on-screen position is consistent with exportable or printable records and with the group’s stated policy that external records prevail in case of dispute.

**Acceptance Scenarios**:

1. **Given** a member views any financial summary, **When** they look for a disclaimer or help text, **Then** they see that external bank and investment records are the source of truth in case of dispute.
2. **Given** a member requests their own data, **When** they export or request a statement, **Then** they receive a consistent, historical record of their position and key events (contributions, penalties, investments, exits) that can be compared with external records.
3. **Given** an auditor or authorized role, **When** they access the system, **Then** they have read-only access (and optional issue-flagging) without the ability to change financial data; members retain access only to their own data and group aggregates.

---

### Edge Cases

- What happens when a member contributes exactly on the boundary of the contribution window (e.g., last minute of the last day)? The system MUST treat boundary rules as defined in group policy (e.g., inclusive end date, timezone).
- How does the system handle a request to correct a contribution that was recorded in error? Only by creating a reversal record and, if needed, a correct new entry; the original record MUST remain stored and visible for audit.
- What happens when liquidity is insufficient for all queued exits? The system MUST apply a defined order (e.g., first-request-first-served or policy-based) and make the order visible to affected members.
- How is a buy-out valuation computed when there are multiple assets and mixed realized/unrealized growth? The system MUST use a defined, documented formula (e.g., contributions + realized growth + nominal asset value) so that the result is deterministic and auditable.
- What happens when two members dispute the same record? The system MUST not allow either to edit the record; resolution is through reversal/correction by authorized roles and, ultimately, by reference to external source of truth.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record all contributions, penalties, investment allocations, asset conversions, exits, and buy-outs as immutable entries; no such record MAY be edited or deleted after creation.
- **FR-002**: The system MUST support corrections only by creating explicit reversal or adjustment records that reference the original record and preserve full audit history.
- **FR-003**: The system MUST treat external bank statements and external investment records as the ultimate source of truth in disputes; the system MUST present itself as a reference, not a replacement for those sources.
- **FR-004**: The system MUST enforce role-based access: members see only their own financial data and group-level aggregates; administrators can perform governed data entry and reconciliation; auditors have read-only access with optional issue-flagging.
- **FR-005**: The system MUST record monetary and percentage values with sufficient precision for financial accuracy (no floating-point rounding for money); all such values MUST be stored and computed in a deterministic way.
- **FR-006**: The system MUST record the date and value at which each investment allocation and asset conversion occurs, and MUST use that value (not a later revaluation) to determine member shares unless a later, explicit revaluation event is recorded per policy.
- **FR-007**: The system MUST keep penalties and late fees separate from investment-eligible savings so that penalties do not dilute or inflate any member’s investment position.
- **FR-008**: The system MUST support a defined monthly (or periodic) contribution process with configurable boundaries and consequences for late or out-of-bound participation.
- **FR-009**: The system MUST support exit requests and an exit queue when liquidity is insufficient, with entitlement limited to return of contributions (and any agreed realized portion) when liquidity allows.
- **FR-010**: The system MUST support buy-outs using a nominal, non-speculative valuation based on defined inputs (e.g., contributions, realized growth, recorded asset value) and MUST record ownership transfer in an auditable, immutable way.
- **FR-011**: The system MUST expose member-facing and administrative operations through a versioned, documented API that serves as a stable contract for frontends and integrations.
- **FR-012**: The system MUST allow members to export or obtain a consistent, historical statement of their own position and key events for comparison with external records.

### Key Entities *(include if feature involves data)*

- **Member**: A participant in the group; has identity, role, and link to all their financial records (contributions, penalties, holdings, assets, exit/buy-out state).
- **Contribution**: A single immutable record of a member’s savings payment within a contribution window; has amount, date, member, and period.
- **Penalty / Late fee**: A separate immutable record for late or out-of-bound participation; not combined with investment-eligible savings; has amount, date, member, and reason.
- **Contribution window / Period**: A defined time interval and rules (min/max amounts, deadlines) for contributions; one per month or per policy cycle.
- **Investment / Holding**: A record that funds were invested at a specific date and value; links to member shares (each member’s portion of the holding based on eligible savings at that moment).
- **Asset**: A long-term asset (e.g., property) created from holdings via group decision; has a recorded purchase value and fixed ownership percentages per member at the time of conversion.
- **Exit request**: An immutable record that a member has requested early exit; links to queue position and liquidity; entitlement is return of contributions (and agreed realized portion) when available.
- **Buy-out**: An immutable record of ownership transfer from one member to another (or to the group) using a nominal valuation; links to seller, buyer, valuation inputs, and resulting position changes.
- **Reversal / Adjustment**: An explicit record that corrects or reverses a prior record; references the original; both original and reversal remain for audit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Members can view their full financial position (contributions, penalties, holdings share, asset share, exit/buy-out status) in one place and complete that review in under two minutes.
- **SC-002**: A month’s contribution run (record contributions and penalties, then record an investment at a given value) can be completed by an administrator in under ten minutes for a group of at least 50 members, with zero manual edits to past records.
- **SC-003**: Any member’s current position can be reproduced deterministically from the stored ledger (contributions, penalties, investments, assets, exits, buy-outs) so that disputes can be resolved by comparing system output to external records.
- **SC-004**: Exit and buy-out flows produce a clear, documented outcome (queue position or completed transfer) and a record that can be audited without ambiguity.
- **SC-005**: At least 95% of members who use the “My position” view report that the information is consistent with their own records or can be reconciled with external statements.
- **SC-006**: Zero financial records are ever edited or deleted; 100% of corrections are made via explicit reversal or adjustment records that preserve history.

## Assumptions

- The group has an agreed governance document or policy that defines contribution windows, boundaries, late consequences, exit entitlement, and buy-out valuation rules; the system will enforce or reflect those rules, not define them.
- “Liquidity” for exit is defined by the group (e.g., available cash, or sale of an asset); the system records when liquidity exists and when exit can be fulfilled.
- Nominal valuation for buy-outs is defined by the group (e.g., formula based on contributions + realized growth + recorded asset value); the system implements the chosen formula deterministically.
- Members and administrators are identified and authenticated; the exact mechanism (e.g., login, invite codes) is left to implementation in line with constitution (e.g., JWT, RBAC).
- One group is in scope for this specification; multi-group or multi-tenant behavior is out of scope unless later specified.
