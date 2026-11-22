# Test Plan — Guild of the Nemorensis

| Field | Value |
|---|---|
| Status | Complete |
| Test framework | pytest 9.2 |
| Database | SQLite 3.50.4 |
| Test data | `data/characters.csv` (12 rows), `data/equipment.csv` (40 rows) |
| Result | **50 passed, under 1 second** (2026-11-22) |

## 1. Purpose

This plan explains what is tested, how, and with what data. The goal is not
100% code coverage. The goal is evidence that the guild's rules are enforced,
the seed data is healthy, and the analysis queries return the expected shape
and values.

## 2. Test layers

| Layer | File | Tests | Question it answers |
|---|---|---:|---|
| Schema | `tests/test_schema.py` | 5 | Do the tables, view, `STRICT` flag, and foreign key exist? |
| Constraints | `tests/test_constraints.py` | 20 | Does the database reject invalid data and handle deletion safely? |
| Data quality | `tests/test_data_quality.py` | 12 | Does the seed data obey the rules, and does the view calculate correctly? |
| Queries | `tests/test_queries.py` | 8 | Does each analysis query run and return the expected result? |
| Build pipeline | `tests/test_build.py` | 5 | Is the build reproducible, and does a failed build preserve the old database? |

## 3. Test data and fixtures

`tests/conftest.py` builds one real database in a pytest temporary directory
for the whole session. It uses the same `build()` function as the command-line
tool, so the tests exercise the real schema, views, CSV loader, and health
checks. Each test receives a connection with `PRAGMA foreign_keys = ON` and
rolls back its changes afterwards.

The seed data deliberately includes:

- 12 characters, 3 per role;
- 40 items, 26 equipped and 14 in the vault;
- a character with no gear (Corin), to test `LEFT JOIN`, `COUNT`, `COALESCE`,
  and the empty-slot calculation;
- characters who are over, at, and under budget;
- at least one vault item in every slot, so every slot has a possible upgrade;
- one character with a full-ish loadout (Orla, 4 items) and one with none.

## 4. How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
```

Expected final line:

```text
50 passed
```

The exact timing varies by machine; the count and the zero failures are what
matter.

## 5. What each layer covers

### Schema

- both tables exist;
- both tables are `STRICT`;
- `v_character_loadout` exists;
- the view exposes `budget_status`, `power_per_100g`, and the other derived
  columns;
- `equipment` has a foreign key to `characters`.

### Constraints

Positive tests prove valid rows still work. Negative tests prove invalid rows
are rejected:

- duplicate and blank character names;
- invalid roles, levels, and negative budgets;
- duplicate and blank equipment names;
- invalid slots and rarities;
- zero and negative costs;
- negative stats and items with no effect;
- wrong types in a `STRICT` table;
- a second equipped item in the same slot;
- orphan equipment;
- deleting a character returns gear to the vault;
- an item can be reassigned to another character;
- multiple vault items may share a slot.

### Data quality

- exact character and item counts;
- 26 equipped and 14 vault items;
- no character has more than seven items;
- no orphan equipment and no double-booked slots;
- every slot has at least one vault item;
- `PRAGMA integrity_check` returns `ok`;
- `PRAGMA foreign_key_check` returns no rows;
- known `role_power` values match hand calculations;
- `budget_status` matches `gear_cost` versus `budget_gold`;
- a character with no items appears with zero counts and seven empty slots.

### Queries

Each query is executed from its `.sql` file, not copied into the test. This
means a broken query file fails the suite.

- Q1 returns 11 characters who are under-equipped or over budget.
- Q2 returns 12 ranked rows, with ranks 1–3 in each role.
- Q3 returns 28 role/slot combinations, one best-value vault item each.
- Q4 returns 28 affordable recommendations, one per character/slot pair, and
  every recommended item is in the vault and within budget.
- Q5 returns 11 checks, all with zero failures.
- Q6 returns 3 budget statuses covering all 12 characters.
- Q7 returns 4 roles covering all 12 characters.
- Q8 returns 7 slots, 14 vault items, and percentages that add to 100%.

### Build pipeline

- a build creates the database and the view;
- a successful build leaves no `.tmp` file;
- a failed build keeps the previous good database byte-for-byte;
- an unknown `character_name` reports the CSV line and the bad name;
- two builds produce the same counts and `role_power` values.

## 6. Traceability: business rules to tests

| Rule | Test |
|---|---|
| BR-01 Character names unique, trimmed, non-empty, case-insensitive | `test_duplicate_character_name_is_rejected`, `test_blank_character_name_is_rejected` |
| BR-02 Role is one of four values | `test_invalid_role_is_rejected` |
| BR-03 Level is 1–60 | `test_level_outside_range_is_rejected`, `test_level_boundaries` |
| BR-04 Budget is ≥ 0 | `test_negative_budget_is_rejected` |
| BR-05 Item names unique, trimmed, non-empty, case-insensitive | `test_duplicate_equipment_name_is_rejected`, `test_blank_equipment_name_is_rejected` |
| BR-06 Slot is one of seven values | `test_invalid_slot_is_rejected` |
| BR-07 Rarity is one of five values | `test_invalid_rarity_is_rejected` |
| BR-08 Cost is > 0 | `test_zero_cost_is_rejected`, `test_negative_cost_is_rejected` |
| BR-09 Stats are ≥ 0 and at least one is > 0 | `test_negative_stat_is_rejected`, `test_item_with_no_effect_is_rejected` |
| BR-10 An item has at most one owner | `test_item_can_be_reassigned` |
| BR-11 One item per slot per character | `test_second_equipped_item_in_same_slot_is_rejected`, `test_multiple_vault_items_in_same_slot_are_allowed` |
| BR-12 Deleting a character returns gear to the vault | `test_delete_character_returns_gear_to_vault` |
| BR-13 No orphan equipment | `test_orphan_equipment_is_rejected` |
| BR-14 Characters may have zero items | `test_character_with_no_items_appears_in_loadout` |

## 7. Boundaries and negative cases

The suite deliberately tests the edges, not only the happy path:

| Boundary | Valid | Invalid |
|---|---|---|
| Level | 1, 60 | 0, 61 |
| Budget | 0 | -1 |
| Cost | 1 | 0, -1 |
| Slots filled | 7 | 8 |
| Items in a slot | 1 equipped; many in vault | 2 equipped |
| Name | `Jill` | `jill` duplicate, blank, whitespace |
| Foreign key | existing character | `9999` |
| Stats | one positive stat | all zero, any negative |

## 8. Known gaps

- No concurrency or multi-writer testing. SQLite allows one writer at a time;
  this project is a local audit tool, not a web service.
- No performance or load testing. The dataset is intentionally small.
- No property-based or fuzz testing. The negative tests are hand-picked.
- No code-coverage measurement. Coverage is described qualitatively: every
  business rule has at least one test.
- SQLite only. PostgreSQL would need different type and `PRAGMA` handling.

These are scope boundaries, not hidden failures. They are listed in the README
and in the interview notes.

## 9. Exit criteria

The suite is considered complete when:

- `python3 src/build_db.py` succeeds;
- `pytest -q` reports 50 passed;
- `PRAGMA integrity_check` returns `ok`;
- `PRAGMA foreign_key_check` returns no rows;
- all eight query files run;
- every defect in `docs/06_defect_log.md` has a regression test;
- the working tree contains no generated database or scratch files.
