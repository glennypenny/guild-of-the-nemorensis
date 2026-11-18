# Data Dictionary — Guild of the Nemorensis

| Field | Value |
|---|---|
| Status | Session 1 draft; final DDL confirmed in Session 2 |
| Related documents | `02_conceptual_model.md`, `04_logical_model.md` (next), `sql/schema.sql` (next) |

This dictionary defines every column in the database. It follows a conventional data-dictionary pattern: meaning, type, permitted values, required or optional, and an example.

## 1. How to read this document

- **Required?** means the column cannot contain `NULL`.
- **Type** is the SQLite type planned for the logical model.
- **Permitted values** are the allowed values or range.
- **Example** is a plausible value, not necessarily a row in the seed data.
- **Notes** record the constraint or design decision attached to the column.

## 2. Table `characters`

| Column | Meaning | Type | Permitted values | Required? | Example | Notes |
|---|---|---|---|---|---|---|
| `character_id` | Stable identifier for a guild member. | INTEGER | Positive integer | Yes | `1` | `PRIMARY KEY`; auto-assigned by SQLite when omitted; surrogate key. |
| `name` | The member's display name. | TEXT | Trimmed, non-empty, unique, case-insensitive | Yes | `Aria Voss` | `COLLATE NOCASE`, `UNIQUE`, `CHECK (name = TRIM(name) AND length(name) > 0)`. ASCII case-insensitive only. |
| `role` | The member's combat role. | TEXT | `Tank`, `Healer`, `Damage`, `Support` | Yes | `Tank` | `CHECK (role IN (...))`; drives `role_power`. |
| `level` | Experience level. | INTEGER | 1–60 | Yes | `24` | `CHECK (level BETWEEN 1 AND 60)`; context only, not in the power formula. |
| `budget_gold` | Maximum gold value of gear the guild will assign to this character. | INTEGER | ≥ 0 | Yes | `1200` | `CHECK (budget_gold >= 0)`; a cap, not a cash balance. |

## 3. Table `equipment`

| Column | Meaning | Type | Permitted values | Required? | Example | Notes |
|---|---|---|---|---|---|---|
| `equipment_id` | Stable identifier for an item. | INTEGER | Positive integer | Yes | `1` | `PRIMARY KEY`; auto-assigned; surrogate key. |
| `name` | The item's display name. | TEXT | Trimmed, non-empty, unique, case-insensitive | Yes | `Ashen Bulwark` | `COLLATE NOCASE`, `UNIQUE`, `CHECK (name = TRIM(name) AND length(name) > 0)`. |
| `slot` | Where the item is equipped. | TEXT | `Weapon`, `Off-hand`, `Head`, `Chest`, `Legs`, `Feet`, `Accessory` | Yes | `Chest` | `CHECK (slot IN (...))`; one item per slot per character. |
| `rarity` | Item rarity. | TEXT | `Common`, `Uncommon`, `Rare`, `Epic`, `Legendary` | Yes | `Rare` | `CHECK (rarity IN (...))`; descriptive only, not in the power formula. |
| `cost_gold` | Item value in gold. | INTEGER | > 0 | Yes | `450` | `CHECK (cost_gold > 0)`; used for budget and efficiency. No free items in the MVP. |
| `attack_bonus` | Attack added when equipped. | INTEGER | ≥ 0 | Yes, default `0` | `12` | `CHECK (attack_bonus >= 0)`; additive. |
| `defense_bonus` | Defense added when equipped. | INTEGER | ≥ 0 | Yes, default `0` | `30` | `CHECK (defense_bonus >= 0)`; additive. |
| `healing_bonus` | Healing added when equipped. | INTEGER | ≥ 0 | Yes, default `0` | `0` | `CHECK (healing_bonus >= 0)`; additive. |
| `speed_bonus` | Speed added when equipped. | INTEGER | ≥ 0 | Yes, default `0` | `5` | `CHECK (speed_bonus >= 0)`; additive. |
| `character_id` | The character currently holding the item. | INTEGER | `NULL` or an existing `characters.character_id` | No | `3` | Foreign key to `characters`; `ON DELETE SET NULL`; `NULL` means the item is in the vault. |

### Table-level rules for `equipment`

- `CHECK (attack_bonus + defense_bonus + healing_bonus + speed_bonus > 0)` — an item must do something.
- `CREATE UNIQUE INDEX ux_equipment_one_per_slot ON equipment(character_id, slot) WHERE character_id IS NOT NULL;` — a character may have at most one equipped item per slot, while the vault may hold many items in the same slot.

## 4. Draft DDL

This is the planned schema for Session 2. It is included here so the data dictionary and the physical design can be reviewed together. It has not yet been committed as `sql/schema.sql`.

```sql
CREATE TABLE characters (
    character_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE
         CHECK (name = TRIM(name) AND length(name) > 0),
    role TEXT NOT NULL
         CHECK (role IN ('Tank', 'Healer', 'Damage', 'Support')),
    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 60),
    budget_gold INTEGER NOT NULL CHECK (budget_gold >= 0)
) STRICT;

CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE
         CHECK (name = TRIM(name) AND length(name) > 0),
    slot TEXT NOT NULL
         CHECK (slot IN ('Weapon', 'Off-hand', 'Head', 'Chest', 'Legs', 'Feet', 'Accessory')),
    rarity TEXT NOT NULL
         CHECK (rarity IN ('Common', 'Uncommon', 'Rare', 'Epic', 'Legendary')),
    cost_gold INTEGER NOT NULL CHECK (cost_gold > 0),
    attack_bonus INTEGER NOT NULL DEFAULT 0 CHECK (attack_bonus >= 0),
    defense_bonus INTEGER NOT NULL DEFAULT 0 CHECK (defense_bonus >= 0),
    healing_bonus INTEGER NOT NULL DEFAULT 0 CHECK (healing_bonus >= 0),
    speed_bonus INTEGER NOT NULL DEFAULT 0 CHECK (speed_bonus >= 0),
    character_id INTEGER REFERENCES characters(character_id) ON DELETE SET NULL,
    CHECK (attack_bonus + defense_bonus + healing_bonus + speed_bonus > 0)
) STRICT;

CREATE UNIQUE INDEX ux_equipment_one_per_slot
ON equipment(character_id, slot)
WHERE character_id IS NOT NULL;
```

`STRICT` requires SQLite 3.37 or later. This machine has 3.45.1.

Validated against SQLite 3.45.1 on 2026-11-18: valid rows insert; duplicate names (including case-only differences), invalid roles/levels/budgets, blank names, invalid slots, zero costs, all-zero stats, orphan foreign keys, and double-booked slots are rejected; multiple vault items in one slot are allowed; deleting a character sets the item's `character_id` to `NULL`.

## 5. Derived metrics

These are calculated in views and queries; they are not stored columns.

| Metric | Definition | Behaviour when the character has no gear |
|---|---|---|
| `items_equipped` | `COUNT(equipment_id)` for assigned items. | `0` |
| `gear_cost` | `COALESCE(SUM(cost_gold), 0)`. | `0` |
| `role_power` | `CASE role` with the weights from the brief. | `0` |
| `budget_remaining` | `budget_gold - gear_cost`. | Equal to `budget_gold` |
| `budget_status` | `Over`, `At`, or `Under`. | `Under` (unless the budget is 0, then `At`) |
| `power_per_100g` | `100.0 * role_power / NULLIF(gear_cost, 0)`. | `NULL` |
| `empty_slots` | `7 - COUNT(DISTINCT slot)`. | `7` |
| `over_budget` | `gear_cost > budget_gold`. | `FALSE` |

## 6. Business rules and where they are enforced

| ID | Rule | Enforced by | Planned test |
|---|---|---|---|
| BR-01 | Character names are unique, trimmed, non-empty, case-insensitive. | `UNIQUE COLLATE NOCASE`; `CHECK` | `test_duplicate_character_name_is_rejected`, `test_blank_character_name_is_rejected` |
| BR-02 | Role is one of four values. | `CHECK` | `test_invalid_role_is_rejected` |
| BR-03 | Level is 1–60. | `CHECK` | `test_level_boundaries` |
| BR-04 | Budget is ≥ 0. | `CHECK` | `test_negative_budget_is_rejected` |
| BR-05 | Item names are unique, trimmed, non-empty, case-insensitive. | `UNIQUE COLLATE NOCASE`; `CHECK` | `test_duplicate_item_name_is_rejected`, `test_blank_item_name_is_rejected` |
| BR-06 | Slot is one of seven values. | `CHECK` | `test_invalid_slot_is_rejected` |
| BR-07 | Rarity is one of five values. | `CHECK` | `test_invalid_rarity_is_rejected` |
| BR-08 | Cost is > 0. | `CHECK` | `test_zero_or_negative_cost_is_rejected` |
| BR-09 | Stats are ≥ 0 and at least one is > 0. | `CHECK` | `test_negative_stat_is_rejected`, `test_all_zero_stats_is_rejected` |
| BR-10 | An item is assigned to at most one character. | Single nullable `character_id` column | `test_item_can_be_reassigned` |
| BR-11 | A character has at most one item per slot. | Partial unique index | `test_character_cannot_equip_two_items_in_same_slot` |
| BR-12 | Deleting a character returns gear to the vault. | `ON DELETE SET NULL` plus `PRAGMA foreign_keys = ON` | `test_delete_character_returns_gear_to_vault` |
| BR-13 | No orphaned equipment. | Foreign key plus `PRAGMA foreign_keys = ON` | `test_orphan_equipment_is_rejected` |
| BR-14 | Characters may have zero items; items may be unassigned. | Nullable FK; `LEFT JOIN` in queries | `test_character_with_no_items_appears_in_roster` |

## 7. Seed data design targets

The exact values will be frozen in Session 3 and used in query tests.

| Target | Reason |
|---|---|
| 12 characters, 3 per role | Enough for a meaningful within-role ranking. |
| 40 items, 5–6 per slot | Enough competition per slot without manual data entry becoming the project. |
| Roughly 28 assigned, 12 in the vault | Both equipped and unassigned items appear in the analysis. |
| At least one character with zero items | Exercises `LEFT JOIN` and `COALESCE`. |
| At least one character with an empty slot | Exercises the empty-slots query. |
| At least one character over budget | Exercises the over-budget query and a negative remaining budget. |
| At least one character under budget with an affordable upgrade | Exercises the recommendation query. |
| At least one item of each rarity | Exercises rarity reporting. |
| At least one vault item in each slot | Ensures every slot has a potential upgrade. |
| Known expected query results | Makes query tests possible. |
| Names original and hand-authored | Avoids copyright and personal-data issues. |

## 8. Data provenance and license

- All data is synthetic and hand-authored for this project.
- No copyrighted game data, scraped wiki content, or personal data.
- If names or lore are drawn from the author's own world-building, that is original work and will be noted in the README.
- Code license: MIT (to be added before publication).
- Data license: CC BY 4.0 or CC0 (to be decided before publication).

## 9. Change log

| Date | Change |
|---|---|
| 2026-11-18 | Initial dictionary and draft DDL (Session 1). |
