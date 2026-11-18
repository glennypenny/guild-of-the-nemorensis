# Guild of the Nemorensis — Gear Audit

A small, reproducible SQLite database for auditing an adventuring guild's equipment: who is under-equipped, who is over budget, and which vault item is the best affordable upgrade.

> **Project status:** Session 1 of 6 — domain model and data dictionary complete. Schema, seed data, queries, and tests are next.

## Why this project exists

This is a portfolio project for QA and data-analyst roles. It is deliberately small: two tables, 12 characters, 40 equipment items, eight analysis queries, and a pytest suite. The point is not volume; it is evidence of clear requirements, a defensible schema, enforced data quality, and tests that try to break the data.

The domain is an original dark-fantasy setting, the Guild of the Nemorensis. All data is synthetic and hand-authored. No copyrighted game data is used.

## What it will demonstrate

- Relational modelling: conceptual model → logical model → SQLite schema
- Data integrity: primary and foreign keys, `NOT NULL`, `CHECK`, `UNIQUE`, `STRICT`, and a partial unique index
- SQL analysis: joins, aggregates, CTEs, views, and window functions
- Python: building a database from CSV, parameterised queries, and a small report runner
- QA: a four-layer pytest suite and a defect log with regression tests
- Communication: a README that explains decisions, limitations, and what I learned

## Documentation

- [Project brief](docs/00_project_brief.md)
- [Glossary](docs/01_glossary.md)
- [Conceptual model](docs/02_conceptual_model.md)
- [Data dictionary](docs/03_data_dictionary.md)
- [Interview notes](docs/07_interview_notes.md) — living document

## Planned structure

```text
guild-of-the-nemorensis/
├── data/                  # characters.csv, equipment.csv
├── docs/                  # brief, models, dictionary, test plan, defect log
├── sql/                   # schema, views, queries, quality checks
├── src/                   # build_db.py, run_queries.py, quality_check.py
├── tests/                 # pytest suite
├── README.md
└── requirements.txt
```

## Roadmap

| Session | Deliverable | Status |
|---|---|---|
| 1 | Brief, glossary, conceptual model, data dictionary | Complete |
| 2 | Logical model, schema, ERD | Next |
| 3 | Seed CSVs, build script, integrity checks | Planned |
| 4 | Views and eight analysis queries | Planned |
| 5 | pytest suite and defect log | Planned |
| 6 | README polish, LinkedIn post, CV bullets | Planned |

## Domain in one paragraph

The Guild of the Nemorensis has 12 members. Each has a name, a role (Tank, Healer, Damage, or Support), a level, and a gear budget in gold. The guild owns 40 unique equipment items. Each item has a name, a slot, a rarity, a cost, and bonuses to attack, defense, healing, and speed. An item is either assigned to one character or sits in the vault unassigned. A character can have at most one item per slot. The quartermaster wants a repeatable audit, not a one-off spreadsheet.

## License

TBD. The code will use MIT; the synthetic data will use CC BY 4.0 or CC0. This will be finalised before publication.
