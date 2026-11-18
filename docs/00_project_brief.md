# Project Brief — Guild of the Nemorensis: Gear Audit

| Field | Value |
|---|---|
| Project | Guild of the Nemorensis — Gear Audit |
| Repository | `guild-of-the-nemorensis` |
| Author | Glen Salmon |
| Status | Session 1 complete — domain model; schema and data next |
| Version | 0.1.0 |
| Target roles | QA / software testing; data analyst |
| Stack | Python 3.12, SQLite 3.45, pytest |
| Scope mode | A — audit current loadouts and recommend per-slot upgrades |

## 1. Purpose

Given a guild roster and a vault of equipment, identify which characters are under-equipped, over budget, or poorly matched to their role, and recommend the best affordable per-slot upgrade from the vault.

This is a portfolio project, not a production application. Its value is the evidence it provides: a clear domain, a deliberate schema, enforced data quality, tested queries, and honest limitations.

## 2. The scope decision

"Best loadout for a role or budget" can mean two different projects:

- **A. Audit (chosen):** compare the loadouts characters already have; flag empty slots, overspend, and role mismatch; recommend the best affordable single vault item for each empty slot.
- **B. Optimiser (v2):** search all combinations of items across all slots to maximise power under a budget, a knapsack problem.

The two-table model supports A. B would need a loadout-plan table or a Python solver, and is deliberately out of scope for the MVP. The README will explain this trade-off; it is a good interview talking point.

## 3. Domain of discourse

The Guild of the Nemorensis is a small adventuring guild. It has 12 members. Each member has:

- a unique name;
- one role: Tank, Healer, Damage, or Support;
- a level from 1 to 60;
- a gear budget in gold.

The guild owns 40 unique equipment items. Each item has:

- a unique name;
- one slot: Weapon, Off-hand, Head, Chest, Legs, Feet, or Accessory;
- one rarity: Common, Uncommon, Rare, Epic, or Legendary;
- a cost in gold;
- bonuses to attack, defense, healing, and speed.

An item is either assigned to one character or unassigned in the guild vault. A character can have at most one item per slot. The vault is not a separate table: it is the set of items whose `character_id` is `NULL`. A loadout is not a separate table either: it is the set of items currently assigned to a character.

## 4. Users and decisions

| User | Decision they need to make |
|---|---|
| Guild quartermaster | Which characters need gear? Which vault items are the best affordable upgrades? |
| Guild leader | Which roles are strong or lagging? Who is over budget? |
| QA analyst | Does the data obey the guild's rules? Can bad data enter? |
| Interviewer | Can the author explain and defend the schema, queries, and tests? |

## 5. Primary questions

1. Which characters are under-equipped (empty slots) or over budget?
2. Which characters have the strongest current loadout for their role, and which are lagging?
3. Which unassigned items are the best value per gold, by slot and role?
4. Which affordable vault item is the best next upgrade for each character's empty slot?
5. Does the data obey the guild's rules: unique names, valid roles/slots, no orphans, no double-booked slots, no negative values?

## 6. Metrics

| Metric | Definition | Interpretation |
|---|---|---|
| `items_equipped` | Count of equipment rows assigned to the character | 0–7 under the one-per-slot rule |
| `gear_cost` | Sum of `cost_gold` for assigned items | 0 if the character has no gear |
| `role_power` | Weighted stat total: Tank `defense*3 + attack + speed`; Healer `healing*3 + defense + speed`; Damage `attack*3 + speed`; Support `healing*2 + speed*2 + defense` | Higher is better for that role |
| `budget_remaining` | `budget_gold - gear_cost` | Negative means over budget |
| `budget_status` | Over / At / Under | Based on `gear_cost` vs `budget_gold` |
| `power_per_100g` | `100.0 * role_power / NULLIF(gear_cost, 0)` | Higher is more efficient; `NULL` if no gear |
| `empty_slots` | `7 - COUNT(DISTINCT slot)` for assigned items | 0–7 |

**What "best" means:** for a role, the highest `role_power`; for a budget, the highest `role_power` that fits within the remaining budget; for value, the highest `power_per_100g`. These are guild heuristics, not objective game truth. The weights are deliberately visible and changeable in one view.

## 7. In scope

- Two tables: `characters` and `equipment`.
- 12 characters and 40 equipment items, hand-authored in CSV.
- Seven slots, four roles, five rarities.
- Optional assignment: `equipment.character_id` may be `NULL`.
- Constraints: primary key, foreign key, `NOT NULL`, `UNIQUE`, `CHECK`, `STRICT`, partial unique index, `COLLATE NOCASE`.
- Eight analysis queries covering joins, aggregates, CTEs, views, and window functions.
- A pytest suite with 15+ tests across schema, constraints, data quality, and queries.
- A defect log with 3–5 real defects and regression tests.
- README, ERD, glossary, interview notes, LinkedIn post, and CV bullets.

## 8. Out of scope and limitations

- No combat simulation. `role_power` is a transparent heuristic.
- No item history or audit trail; only the current assignment is stored.
- No multiple copies of the same item; each item is unique.
- No item sharing; an item belongs to at most one character.
- No multiple loadout plans per character.
- No market prices, taxes, discounts, consumables, quests, or character abilities.
- No true combinatorial optimiser; recommendations are per slot.
- No level normalisation; a high-level character may outrank a low-level one because they have more gear. Rankings should be read with level in mind.
- No web app, authentication, API, or multi-user access.
- Synthetic data; this is not a live game or a real guild.

## 9. Data provenance

All data is original and hand-authored for this project. No copyrighted game data, scraped wiki content, or personal data is used. If names or lore are drawn from the author's own world-building, that is original work and will be noted in the README. The dataset will be small enough to inspect by hand.

## 10. Design approach

The documentation follows a conventional data-modelling sequence:

1. Domain of discourse and limitations.
2. Conceptual data model: entities, attributes, relationships, business rules.
3. Data dictionary: meaning, permitted values, required/optional, examples.
4. Logical data model: target DBMS, implications, ERD, keys, constraints.
5. Physical implementation: SQLite schema, seed data, queries, tests.

The domain, data, schema, and queries are original to this project.

## 11. Definition of done

A fresh clone can be built and tested with one command, and the README tells the whole story:

- [ ] 12 characters and 40 items load cleanly from CSV.
- [ ] `PRAGMA integrity_check` returns `ok`.
- [ ] `PRAGMA foreign_key_check` returns no rows.
- [ ] All eight queries run and their outputs are documented.
- [ ] 15+ pytest tests pass in under 60 seconds.
- [ ] The defect log contains 3–5 real defects with regression tests.
- [ ] The data dictionary covers every column.
- [ ] The README explains the schema, queries, limitations, and what was learned.
- [ ] No secrets, copyrighted data, or real personal data.
- [ ] LinkedIn post and two CV bullets are drafted.

## 12. Build plan

| Session | Work | Output | Status |
|---|---|---|---|
| 1 | Brief, glossary, conceptual model, data dictionary | `docs/00`–`03`, `docs/07` | Complete |
| 2 | Logical model, schema, ERD | `docs/04`, `sql/schema.sql` | Next |
| 3 | Seed CSVs, build script, integrity checks | `data/`, `src/build_db.py` | Planned |
| 4 | Views and eight queries | `sql/views.sql`, `sql/queries/`, outputs | Planned |
| 5 | pytest suite and defect log | `tests/`, `docs/05`–`06` | Planned |
| 6 | README polish, LinkedIn, CV bullets | public repo | Planned |

## 13. Confirmed decisions

- Scope A: audit + per-slot recommendations.
- Name: Guild of the Nemorensis.
- 12 characters / 40 items.
- Roles: Tank, Healer, Damage, Support.
- Slots: Weapon, Off-hand, Head, Chest, Legs, Feet, Accessory.
- Stats: attack, defense, healing, speed.
- Python 3.12 + SQLite 3.45 + pytest in a project venv.
- Repo is standalone and self-contained.
- Data hand-authored and original.
- License: TBD (MIT for code; CC BY 4.0 or CC0 for data).
