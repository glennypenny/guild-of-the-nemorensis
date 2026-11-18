# Glossary

A living glossary for the project. If a term is missing, add it here rather than letting it become mysterious.

> **Don't read this cover to cover.** It is a reference, not a book. Start with the ten core terms below and come back when a term appears in the build.
>
> **Core ten:** database, table, row, column, primary key, foreign key, `NULL`, constraint, query, schema.

## 1. Data modelling

| Term | Plain English | In this project |
|---|---|---|
| Domain of discourse | The part of the real world the database is about, including what is out of scope. | A small adventuring guild, its 12 members, its 40 equipment items, and the vault. |
| Entity | A thing we store data about. | `Character`, `Equipment item`. |
| Attribute | A fact about an entity. | A character's name, role, level, budget. |
| Relationship | How two entities are connected. | A character can be assigned equipment. |
| Cardinality | How many of one entity can relate to another. | One character to zero-or-many items; one item to zero-or-one character. |
| Optional relationship | A relationship that does not have to exist. | An item may be unassigned in the vault. |
| One-to-many | One row in table A can match many rows in table B, but each B row matches at most one A row. | One character can have many items; each item belongs to at most one character. |
| Many-to-many | Many rows in A can match many rows in B. Needs a junction table. | Not used in the MVP; would be needed if items could be shared. |
| Junction table | A table with foreign keys to two other tables, used to represent many-to-many. | Not in the MVP. |
| Conceptual data model (CDM) | A business-level model: entities, attributes, relationships, rules. No SQLite types yet. | `docs/02_conceptual_model.md`. |
| Logical data model (LDM) | The CDM mapped to a specific database: tables, columns, types, keys, constraints. | `docs/04_logical_model.md` (Session 2). |
| Physical schema | The actual SQL that creates the database. | `sql/schema.sql` (Session 2). |
| Data dictionary | A table of every column: meaning, type, permitted values, required/optional, example. | `docs/03_data_dictionary.md`. |
| ERD | Entity-relationship diagram. A picture of entities and their relationships. | Mermaid diagram in the conceptual model and README. |
| Normalisation | Organising data so each fact is stored once, reducing duplication and update anomalies. | Character facts live in `characters`; item facts live in `equipment`; the link is a foreign key. |
| Surrogate key | An artificial identifier with no business meaning. | `character_id`, `equipment_id`. |
| Natural key | A real-world attribute that uniquely identifies a row. | `characters.name`, `equipment.name` (both unique). |
| Primary key | The column that uniquely identifies each row. | `character_id`, `equipment_id`. |
| Foreign key | A column that references the primary key of another table. | `equipment.character_id` references `characters.character_id`. |
| Nullable | The column may contain `NULL`. | `equipment.character_id` is nullable: `NULL` means vault. |
| Orphan | A child row that references a parent row that does not exist. | An equipment row with `character_id = 999` when no character 999 exists. |
| Business rule | A rule the domain must obey. | "A character can have at most one item per slot." |
| Seed data | The initial data loaded into the database. | `data/characters.csv`, `data/equipment.csv`. |
| Fixture | Reusable setup or data for a test. | A small in-memory database with two characters and four items. |
| Synthetic data | Invented data, not collected from real people or a live system. | All 12 characters and 40 items. |
| Provenance | Where the data came from and whether it may be reused. | Original, hand-authored; no copyrighted game data. |

## 2. Database and SQLite

| Term | Plain English | In this project |
|---|---|---|
| Database | An organised collection of tables and other objects, usually stored in one file. | `guild.db`. |
| Table | A named grid of rows and columns. | `characters`, `equipment`. |
| Row / record | One item in a table. | One character or one equipment item. |
| Column / field | One attribute of a table. | `name`, `role`, `cost_gold`. |
| Schema | The structure of the database: tables, columns, types, constraints. Also the SQL file that creates it. | `sql/schema.sql`. |
| DDL | Data Definition Language: `CREATE`, `ALTER`, `DROP`. | Creating tables and indexes. |
| DML | Data Manipulation Language: `INSERT`, `UPDATE`, `DELETE`. | Loading CSV rows and testing invalid inserts. |
| DQL | Data Query Language: `SELECT`. | The eight analysis queries. |
| Constraint | A rule enforced by the database. | `NOT NULL`, `UNIQUE`, `CHECK`, `FOREIGN KEY`. |
| `NOT NULL` | The column must have a value; `NULL` is rejected. | `characters.name` must be present. |
| `UNIQUE` | No two rows may share the same value. | Character and item names. |
| `CHECK` | The value must satisfy a condition. | `level BETWEEN 1 AND 60`. |
| `DEFAULT` | The value used when a column is omitted from an insert. | Stat bonuses default to `0`. |
| `STRICT` | A table option that enforces the declared column types. | Both tables use it. |
| `PRAGMA` | A SQLite-specific command to read or change an internal setting. | `PRAGMA foreign_keys = ON`. |
| `PRAGMA foreign_keys` | The per-connection switch that enforces foreign keys. Off by default. | Turned on in the build script and every test connection. |
| Type affinity | SQLite's attempt to convert a value to the column's preferred type. It does not guarantee the type. | Why `STRICT` matters. |
| Dynamic typing | Values carry their own type; columns do not strictly enforce a type by default. | SQLite stores text in an `INTEGER` column unless the table is `STRICT`. |
| `COLLATE NOCASE` | An ASCII case-insensitive comparison rule for text. | `'Aria'` and `'aria'` count as the same name. |
| `NULL` | "Unknown" or "missing". Not the same as `0` or `''`. | `character_id IS NULL` means the item is in the vault. |
| `NULLIF(a, b)` | Returns `NULL` if `a = b`; otherwise returns `a`. | Turns a zero gear cost into `NULL` so division is safe. |
| Integer division | Dividing two integers and discarding the remainder. | `5 / 2` is `2`; use `5.0 / 2` for `2.5`. |
| Index | A data structure that speeds up lookups and can enforce uniqueness. | `ux_equipment_one_per_slot`. |
| Partial index | An index that applies only to rows matching a `WHERE` clause. | Only equipped items are checked for one-per-slot. |
| View | A saved `SELECT` query that behaves like a virtual table. | `v_character_loadout`, `v_equipment_value` (Session 4). |
| Transaction | A group of statements that either all succeed or all roll back. | Loading the seed data atomically. |
| Parameterised query | SQL with placeholders (`?`) and values supplied separately. | Prevents SQL injection. |
| SQL injection | Malicious input that changes the SQL being executed. | Avoided by parameterised queries, never f-strings. |
| `sqlite3` module | Python's standard-library SQLite driver. | `import sqlite3`. |
| `:memory:` | A temporary database that exists only in memory. | Fast test fixtures. |
| Single writer | SQLite allows one write transaction at a time. | Fine for a local portfolio project; not a multi-user app. |
| `PRAGMA integrity_check` | Checks the database's internal consistency. | Must return `ok` after the build. |
| `PRAGMA foreign_key_check` | Reports rows that violate foreign keys. | Must return no rows after the build. |
| `EXPLAIN QUERY PLAN` | Shows how SQLite intends to execute a query. | Optional stretch: compare a query with and without an index. |
| `row_factory` | A Python `sqlite3` setting that changes how rows are returned. | `sqlite3.Row` lets us use `row["name"]`. |

## 3. SQL query terms

| Term | Plain English | In this project |
|---|---|---|
| `SELECT` | Choose columns to return. | Every query. |
| `FROM` | Name the table(s) to read. | `FROM characters`. |
| `WHERE` | Filter individual rows. | `WHERE character_id IS NULL`. |
| `ORDER BY` | Sort the result. | Sort by `role_power DESC`. |
| `GROUP BY` | Collapse rows into groups so aggregates can be calculated. | One row per character. |
| `HAVING` | Filter groups after aggregation. | Characters whose total gear cost exceeds budget. |
| `JOIN` / `INNER JOIN` | Return only rows that match in both tables. | Characters with their assigned equipment. |
| `LEFT JOIN` | Return all rows from the left table, with `NULL` where the right table has no match. | Characters with no items still appear in the roster. |
| `ON` | The join condition. | `equipment.character_id = characters.character_id`. |
| `CASE` | SQL's if/else expression. | Map role to its power weights; label budget status. |
| Aggregate function | `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`; collapses many rows into one value. | `SUM(cost_gold)`. |
| `COALESCE` | Return the first non-`NULL` argument. | `COALESCE(SUM(cost_gold), 0)` for characters with no gear. |
| Subquery | A query inside another query. | Used in the capstone recommendation query. |
| CTE (`WITH`) | A named temporary result set that makes a complex query readable. | `WITH slots(slot) AS (VALUES ...)`. |
| Window function | Computes a value across related rows without collapsing them. | `RANK() OVER (PARTITION BY role ORDER BY role_power DESC)`. |
| `RANK()` | Ranks rows, leaving gaps after ties. | Role power ranking. |
| `ROW_NUMBER()` | Numbers rows sequentially, with no gaps. | Top item per slot. |
| `PARTITION BY` | Splits rows into groups for a window function. | Partition by role or slot. |
| `DISTINCT` | Remove duplicate rows. | Count distinct slots covered. |
| `LIMIT` | Cap the number of rows returned. | Top three items per slot. |
| `IN` | Match any value in a list. | `role IN ('Tank', 'Healer', 'Damage', 'Support')`. |
| `BETWEEN` | Inclusive range check. | `level BETWEEN 1 AND 60`. |
| `IS NULL` | Test for `NULL`. Use `IS`, not `=`. | `WHERE character_id IS NULL`. |

## 4. QA and testing

| Term | Plain English | In this project |
|---|---|---|
| Test | A check that compares expected behaviour with actual behaviour. | `pytest` tests. |
| Unit test | Tests one small piece in isolation. | A constraint test that inserts one invalid row. |
| Integration test | Tests several components together. | Build the schema, load data, run a query. |
| Regression test | A test that stops a fixed bug from returning. | One per defect in the log. |
| Fixture | Reusable setup or data for tests. | A temporary database with known rows. |
| Arrange-Act-Assert | Test structure: set up, perform the action, check the result. | Used in every test. |
| Expected vs actual | The value you expect compared with what the code produced. | `assert actual == expected`. |
| Edge case | An unusual or extreme input. | A character with no items; a vault full of items. |
| Boundary value | A value at the edge of a valid range. | Level 1 and 60 are valid; 0 and 61 are not. |
| Positive test | Confirms that valid input succeeds. | Insert a valid character. |
| Negative test | Confirms that invalid input is rejected. | Insert a character with role `Wizard`. |
| Defect | A bug: behaviour that violates the requirements. | Recorded in the defect log. |
| Defect log | A record of symptom, root cause, fix, and regression test. | `docs/06_defect_log.md` (Session 5). |
| Test plan | What will be tested, how, and with what data. | `docs/05_test_plan.md` (Session 5). |
| Coverage | How much of the requirements and code are tested. | Qualitative here: every business rule has a test. |
| CI | Continuous integration: run tests automatically on push. | Optional stretch. |
| `pytest` | A Python test framework. | `pytest -q`. |
| `sqlite3.IntegrityError` | The Python exception raised when a constraint is violated. | Asserted in negative tests. |

## 5. Project metrics

| Metric | Meaning |
|---|---|
| `items_equipped` | How many items are currently assigned to a character. |
| `gear_cost` | Total gold value of those items. |
| `role_power` | Role-weighted stat total: Tank `defense*3 + attack + speed`; Healer `healing*3 + defense + speed`; Damage `attack*3 + speed`; Support `healing*2 + speed*2 + defense`. |
| `budget_remaining` | `budget_gold - gear_cost`. Negative means over budget. |
| `budget_status` | Over budget, at budget, or under budget. |
| `power_per_100g` | `100.0 * role_power / NULLIF(gear_cost, 0)`. Higher is more efficient; `NULL` if the character has no gear. |
| `empty_slots` | `7 - COUNT(DISTINCT slot)` for the character's assigned items. |
| `over_budget` | True when `gear_cost > budget_gold`. |

## 6. SQLite gotchas worth remembering

1. **Foreign keys are off by default.** Run `PRAGMA foreign_keys = ON` on every connection.
2. **SQLite is dynamically typed by default.** Use `STRICT` tables so `'abc'` cannot enter an `INTEGER` column.
3. **`NULL` is not `0` and not `''`.** It means unknown or missing.
4. **A `CHECK` passes when the condition is `NULL`.** Pair checks with `NOT NULL` where a value is required.
5. **Integer division truncates.** Write `100.0`, not `100`, when you want decimals.
6. **`UNIQUE` treats `NULL`s as distinct.** Multiple vault items may share a slot because their `character_id` is `NULL`. We use a partial index to make the equipped-item rule explicit.
7. **`COLLATE NOCASE` is ASCII-only.** It does not case-fold accents. Document the limitation.
8. **`ALTER TABLE` is limited.** Some changes require creating a new table and copying data.
9. **SQLite has one writer at a time.** Great for a local portfolio project; not a high-concurrency web backend.
10. **No native `BOOLEAN` or `DATE` types.** Use `INTEGER` or `TEXT` with `CHECK` constraints and a documented format.
11. **`PRAGMA foreign_keys` is not stored in the `.db` file.** Each new connection must enable it again.
12. **The `sqlite3` CLI is optional.** Python's `sqlite3` module can do everything this project needs.

## 7. Python snippets

```python
import sqlite3

conn = sqlite3.connect("guild.db")
conn.execute("PRAGMA foreign_keys = ON")
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT name, role FROM characters WHERE role = ? ORDER BY name",
    ("Tank",),
).fetchall()

for row in rows:
    print(row["name"], row["role"])
```

The `?` is a placeholder. The value is passed separately so it can never be treated as SQL. Never build a query with an f-string around user input.
