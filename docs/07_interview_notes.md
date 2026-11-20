# Interview Notes — Guild of the Nemorensis

This is a living document. Do not memorise a script. Write each answer in your own words, point to the evidence, and rehearse it out loud.

## How to use this file

1. After each session, fill in the evidence and update the numbers.
2. Write a 30-second answer and a 2-minute answer for each question.
3. Rehearse out loud, ideally to someone who will interrupt and challenge you.
4. When the schema or data changes, update the answer.
5. At the end, add two CV bullets and a LinkedIn hook.

## The STAR spine

- **Situation:** the guild has a roster, a vault of gear, and no repeatable way to audit loadouts.
- **Task:** design a small database that answers the quartermaster's questions and prove the data can be trusted.
- **Action:** model the domain, build a two-table SQLite schema, enforce constraints, write eight queries, and test the rules with pytest.
- **Result:** a one-command build, a documented schema, tested queries, a defect log, and a public portfolio repo.

## 1. "Walk me through your schema."

**What they are testing:** Can you explain a design clearly, from the domain to the tables, without hiding behind jargon?

**Evidence:** `docs/02_conceptual_model.md`, `docs/03_data_dictionary.md`, `sql/schema.sql` (Session 2), ERD in the README.

**Prompts:**

- One sentence on what the database is for.
- Two entities: characters and equipment.
- The relationship: one character to zero-or-many items; one item to zero-or-one character.
- The vault is `character_id IS NULL`; the loadout is derived, not stored.
- The key constraints and why they exist.
- One query the schema makes easy.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 2 tables, 12 characters, 40 items, 7 slots, 4 roles.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 2. "Why only two tables?"

**What they are testing:** Do you understand cardinality and normalisation, or did you just stop early?

**Evidence:** `docs/02_conceptual_model.md` section 9; `sql/schema.sql`.

**Prompts:**

- Each item is a unique physical object, assigned to at most one character.
- A character can have many items. That is one-to-many.
- One-to-many uses a foreign key on the many side, not a junction table.
- The vault is an absence of assignment, not an entity.
- A loadout is derived by grouping, not stored.
- A junction table would be needed for shared items, multiple loadouts, or history.
- The trade-off is documented, not hidden.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 2 tables, 1 relationship, 0 junction tables.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 3. "Why is `character_id` nullable, and what happens when a character is deleted?"

**What they are testing:** Do you understand optional relationships and referential actions?

**Evidence:** `sql/schema.sql` (Session 2); `tests/test_constraints.py::test_delete_character_returns_gear_to_vault` (Session 5).

**Prompts:**

- `NULL` means the item is in the guild vault, unassigned.
- The relationship is optional on the equipment side: zero-or-one character.
- `ON DELETE SET NULL` returns the character's gear to the vault instead of deleting it.
- `PRAGMA foreign_keys = ON` is required for the action to run.
- The test proves it: delete a character, assert the items still exist with `character_id IS NULL`.
- Alternative: `RESTRICT` would block deletion; `CASCADE` would delete the gear. We chose `SET NULL` because gear is guild property.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 1 nullable FK; 1 test.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 4. "How do you prevent a character equipping two items in the same slot?"

**What they are testing:** Can you enforce a business rule at the database level rather than relying on the application?

**Evidence:** `sql/schema.sql` partial unique index (Session 2); `tests/test_constraints.py` (Session 5).

**Prompts:**

- The rule: one item per slot per character.
- The index: `CREATE UNIQUE INDEX ux_equipment_one_per_slot ON equipment(character_id, slot) WHERE character_id IS NOT NULL;`
- Why partial: vault items have `character_id = NULL` and may share a slot.
- What happens: the second equipped item in the same slot raises `UNIQUE constraint failed`.
- The tests cover both sides: duplicates fail; multiple vault items in one slot are allowed.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 1 partial unique index; 2 tests.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 5. "How do you stop bad data entering the database?"

**What they are testing:** Do you know the difference between database constraints, application validation, and testing?

**Evidence:** `sql/schema.sql`, `docs/03_data_dictionary.md`, `tests/` (Session 5).

**Prompts:**

- `NOT NULL` for required values.
- `CHECK` for ranges, allowed lists, and multi-column rules.
- `UNIQUE` for duplicate names, case-insensitively.
- `FOREIGN KEY` plus `PRAGMA foreign_keys = ON` for orphans.
- `STRICT` for types.
- `TRIM` checks for invisible whitespace.
- Parameterised queries in Python to avoid SQL injection.
- Negative tests prove invalid rows are rejected; positive tests prove valid rows still work.
- Constraints are the last line of defence; application validation improves the error message.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 5 constraint types; 15+ tests.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 6. "How do you test a database?"

**What they are testing:** Do you have a testing mindset, or do you only test the happy path?

**Evidence:** `docs/05_test_plan.md` and `docs/06_defect_log.md` (planned), `tests/` (planned).

**Prompts:**

- Four layers: schema, constraints, data quality, queries.
- Regression tests for every defect found.
- Fixtures create a fresh temporary database for each test.
- `PRAGMA integrity_check` and `PRAGMA foreign_key_check` for whole-database health.
- Positive and negative tests; boundary values; NULL cases.
- Known expected results for query tests.
- One command runs the suite; the README shows the result.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 4 test layers; 15+ tests; 3–5 defects.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 7. "What is a limitation of your project, and how would you extend it?"

**What they are testing:** Self-awareness and prioritisation. Strong candidates know what they did not build.

**Evidence:** README limitations; `docs/00_project_brief.md` section 8; `docs/02_conceptual_model.md` section 10.

**Prompts:**

- No item history, no multiple copies, no shared items, no multiple loadout plans.
- `role_power` is a heuristic, not a combat simulation.
- No level normalisation; rankings should be read with level in mind.
- No true optimiser; recommendations are per slot.
- Extension: add `loadout` and `loadout_item` for alternative plans.
- Extension: add `assignment_history` for audits.
- Extension: add a Python solver for the knapsack version.
- Extension: add a small dashboard or CSV report.
- Trade-off: every extension adds complexity; the MVP is deliberately finishable.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 1 documented scope boundary; 3 possible extensions.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## 8. "Why SQLite, and what are its trade-offs?"

**What they are testing:** Can you justify a tool choice and name its limits?

**Evidence:** README design decisions; `docs/01_glossary.md` section 6.

**Prompts:**

- SQLite is serverless, file-based, zero-setup, and in Python's standard library.
- Perfect for a portable portfolio demo: clone, run one command, inspect one file.
- Trade-offs: single writer, dynamic typing (mitigated with `STRICT`), foreign keys off by default (mitigated with `PRAGMA`), limited `ALTER TABLE`.
- When to use PostgreSQL instead: concurrent users, a web API, complex permissions, heavy write load.
- The project demonstrates awareness of the limits, not just the convenience.

**My 30-second answer:**

>

**My 2-minute answer:**

>

**Numbers to include:** 1 file, 0 servers, 2 SQLite gotchas mitigated.

**Confidence:** [ ] 1 [ ] 2 [ ] 3 [ ] 4 [ ] 5

## Numbers to remember

| Number | Value |
|---|---|
| Tables | 2 |
| Characters | 12 |
| Equipment items | 40 |
| Slots | 7 |
| Roles | 4 |
| Rarities | 5 |
| Analysis queries | 8 |
| Tests | 15+ |
| Defects in the log | 3–5 |
| Commands to build and test | 1 |
| External data sources | 0 |

## Career assets

To complete in Session 6.

### CV bullet 1

>

### CV bullet 2

>

### LinkedIn post hook

>

## Questions I still have

-
-
-

## Rehearsal checklist

- [ ] I can draw the schema from memory on a whiteboard.
- [ ] I can explain why `character_id` is nullable.
- [ ] I can explain the partial unique index without reading it.
- [ ] I can name the four test layers.
- [ ] I can describe one defect and its regression test.
- [ ] I can state one limitation and one extension.
- [ ] I can explain SQLite's trade-offs in plain English.
- [ ] My 30-second answers fit in 30 seconds.
