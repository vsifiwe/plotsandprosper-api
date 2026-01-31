# Data Model: Plots & Prosper Core Platform

**Branch**: 001-plots-prosper-core  
**Date**: 2026-01-31  
**Source**: [spec.md](./spec.md) entities and FRs

## Principles

- All financial and position-affecting records are **immutable** (append-only). No updates or deletes; corrections via **reversal/adjustment** records that reference the original.
- Monetary and percentage values use **decimal** type (e.g. `DecimalField(max_digits=20, decimal_places=4)`); no float for money.
- **Database-level constraints** (unique, check, FKs) enforce invariants where possible; services validate before insert.

## Entities and Relationships

### Member

- **Purpose**: A participant in the group with identity and role.
- **Attributes**: id, identifier (e.g. email or external id), role (member | admin | auditor), display_name (optional), created_at, is_active.
- **Relations**: One-to-many to Contribution, Penalty, HoldingShare, AssetShare, ExitRequest, BuyOut (as seller or buyer). No direct “balance” column; balances are derived from ledger.

### ContributionWindow (Period)

- **Purpose**: A defined time interval and rules for contributions (one per month or policy cycle).
- **Attributes**: id, start_at, end_at (inclusive), min_amount, max_amount (nullable), name/label (e.g. "2026-01"), created_at.
- **Relations**: One-to-many to Contribution. Used to determine whether a contribution is in-window (savings) or late/out-of-bound (penalty).

### Contribution

- **Purpose**: Single immutable record of a member’s savings payment within a contribution window.
- **Attributes**: id, member_id, window_id, amount (decimal), recorded_at, created_at. Optional: reference (e.g. bank ref), created_by (admin).
- **Constraints**: amount > 0; unique (member, window) if policy is one contribution per member per window, or allow multiple per window per policy.
- **Immutability**: No update/delete. Corrections via Reversal pointing to this id.

### Penalty (Late fee)

- **Purpose**: Separate immutable record for late or out-of-bound participation; not combined with investment-eligible savings.
- **Attributes**: id, member_id, amount (decimal), reason (e.g. late, over_max), period/window_id (optional), recorded_at, created_at, created_by.
- **Immutability**: Same as Contribution; corrections via Reversal.

### Investment (Holding) and HoldingShare

- **Purpose**: Record that funds were invested at a specific date and value; each member’s portion is stored so growth and ownership are deterministic.
- **Investment**: id, recorded_at (date of investment), unit_value (decimal, value per unit at that moment), total_units (optional), created_at, created_by.
- **HoldingShare**: id, investment_id, member_id, units (decimal) or percentage (decimal), created_at. Represents “member X has Y units (or Z%) of this holding at recorded value.”
- **Constraints**: Sum of units or percentages per investment consistent with policy (e.g. 100%); unit_value > 0.
- **Immutability**: No update/delete; corrections via Reversal.

### Asset and AssetShare

- **Purpose**: Long-term asset (e.g. property) created from holdings; ownership fixed at conversion.
- **Asset**: id, name/description, recorded_purchase_value (decimal), conversion_at (date), source_investment_id (optional), created_at, created_by.
- **AssetShare**: id, asset_id, member_id, share_percentage (decimal), created_at. Fixed at conversion; no speculative revaluation in model.
- **Constraints**: Sum of share_percentage per asset = 100%; recorded_purchase_value >= 0.
- **Immutability**: No update/delete of Asset or AssetShare; corrections via Reversal.

### ExitRequest

- **Purpose**: Immutable record that a member has requested early exit; links to queue position and liquidity.
- **Attributes**: id, member_id, requested_at, queue_position (integer, assigned by policy e.g. FIFO), status (queued | fulfilled | cancelled), fulfilled_at (nullable), amount_entitled (decimal, e.g. contributions + agreed realized portion), created_at.
- **Immutability**: Status changes (e.g. fulfilled) can be a new row or a small status table that only appends state changes; no overwrite of original request.

### BuyOut

- **Purpose**: Immutable record of ownership transfer using nominal valuation.
- **Attributes**: id, seller_id, buyer_id (nullable if group buys), nominal_valuation (decimal), valuation_inputs (JSON or separate columns: contributions, realized_growth, asset_value), recorded_at, created_at, created_by.
- **Relations**: May reference AssetShare(s) or HoldingShare(s) being transferred; transfer effect recorded in new rows (e.g. new AssetShare for buyer, seller’s share zeroed or closed via a “closure” record).
- **Immutability**: No update/delete; corrections via Reversal.

### Reversal (Adjustment)

- **Purpose**: Explicit record that corrects or reverses a prior record; preserves audit trail.
- **Attributes**: id, original_record_type (e.g. contribution, penalty, holding_share), original_record_id, reason (optional), created_at, created_by. Optional: replacement_record_id if a correct new entry is created.
- **Semantics**: Original record remains stored and visible; reversal marks it as reversed. Aggregation logic excludes reversed records (or includes them with a “reversed” flag) per policy.

## State and aggregation

- **Member position**: Derived from Contributions (sum in-range) − Reversals, Penalties (sum) − Reversals, HoldingShares (sum units × unit_value per investment), AssetShares (share_percentage × asset.recorded_purchase_value), ExitRequest status, BuyOut as seller/buyer. All computed in services with deterministic, testable logic.
- **Exit queue order**: From ExitRequest.queue_position and status; liquidity and fulfillment are separate (e.g. LiquidityEvent or Fulfillment record) so that “when liquidity allows” is auditable.

## Optional policy tables

- **GroupPolicy** (or env/settings): contribution_window_duration, late_penalty_rule, exit_entitlement_rule, buy_out_valuation_formula_id. Kept minimal; detailed formula can live in code that reads policy id.
- **LiquidityEvent**: id, amount (decimal), event_at, type (e.g. contribution_pool, asset_sale), created_at. Used to determine when exit requests can be fulfilled.

## Migration strategy

- Forward-only migrations; no migrations that rewrite or delete historical financial rows. New tables or columns only; backfill via data migrations that insert only.
