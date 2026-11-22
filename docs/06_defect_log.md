# Defect Log — Guild of the Nemorensis

| Field | Value |
|---|---|
| Status | Complete |
| Defects logged | 4 |
| Regression tests | 4, all passing |
| Last updated | 2026-11-22 |

This log records real defects found while building the project. Each entry has
a symptom, a root cause, a fix, and a regression test that would fail if the
defect returned.

## Summary

| ID | Defect | Severity | Regression test |
|---|---|---|---|
| D-01 | A character with no gear was counted as having one item | High | `test_character_with_no_items_appears_in_loadout` |
| D-02 | Rebuilding the database deleted the loadout view | High | `test_build_creates_database_and_view` |
| D-03 | A failed build destroyed the previous good database | High | `test_failed_build_keeps_previous_database` |
| D-04 | An unknown `character_name` raised a bare `KeyError` | Medium | `test_unknown_character_name_reports_line` |

---

## D-01 — `COUNT(*)` counted the blank row from a `LEFT JOIN`

**Symptom.** A character with no equipment showed `items_equipped = 1` in the
loadout view.

**Root cause.** The view uses `FROM characters LEFT JOIN equipment`. For a
character with no gear, the join produces one row with every equipment column
set to `NULL`. `COUNT(*)` counts that row, so it reports one item. `COUNT(*)`
counts rows, not real items.

**Fix.** Count the equipment key instead:

```sql
COUNT(e.equipment_id) AS items_equipped
```

`COUNT(column)` ignores `NULL`, so a gearless character correctly reports `0`.

**Regression test.** `tests/test_data_quality.py::test_character_with_no_items_appears_in_loadout`
asserts that Corin has `items_equipped = 0`, `gear_cost = 0`, `role_power = 0`,
and `empty_slots = 7`.

**Lesson.** With an outer join, `COUNT(*)` and `COUNT(column)` answer different
questions. Use `COUNT(column)` when the column can be `NULL` because of the
join.

---

## D-02 — Rebuilding the database deleted the view

**Symptom.** After running `python3 src/build_db.py`, `v_character_loadout`
was missing. The queries that used the view failed.

**Root cause.** The build script deleted `guild.db` and recreated the tables,
but it only ran `sql/schema.sql`. The view had been created by hand in the
SQLite shell, so it was not part of the build.

**Fix.** Run `sql/views.sql` during the build, immediately after the schema:

```python
conn.executescript(SCHEMA_PATH.read_text())
conn.executescript(VIEWS_PATH.read_text())
```

The order matters: tables must exist before a view can refer to them.

**Regression test.** `tests/test_build.py::test_build_creates_database_and_view`
builds a fresh database and asserts that the view exists.

**Lesson.** Anything created by hand must be moved into the build, or it is not
reproducible. A one-command build has to create tables, views, and data.

---

## D-03 — A failed build destroyed the previous good database

**Symptom.** A typo in a CSV caused the build to fail, but the old `guild.db`
was already gone. The project was left with no usable database.

**Root cause.** The build deleted the target file first:

```python
if DB_PATH.exists():
    DB_PATH.unlink()
```

If a later insert, constraint, or health check failed, the old database had
already been removed.

**Fix.** Build into a temporary file, run the health checks, and replace the
target only on success:

```python
temp_path = db_path.with_name(db_path.name + ".tmp")
conn = sqlite3.connect(temp_path)
try:
    ...
    conn.commit()
except Exception:
    conn.rollback()
    conn.close()
    temp_path.unlink(missing_ok=True)
    raise
else:
    conn.close()
    os.replace(temp_path, db_path)
```

`os.replace` is atomic on the same filesystem. A failed build leaves the
previous database untouched and removes the temporary file.

**Regression test.** `tests/test_build.py::test_failed_build_keeps_previous_database`
builds a good database, attempts a build with duplicate character names, and
asserts that the original file is byte-for-byte unchanged and no `.tmp` file
remains.

**Lesson.** Do not destroy the last known good artifact before the replacement
is proven. Build beside it, check it, then swap.

---

## D-04 — Unknown CSV name raised a bare `KeyError`

**Symptom.** A typo in `equipment.csv` produced:

```text
KeyError: 'Jilll'
```

The message did not say which file, which line, or what the valid names were.

**Root cause.** The loader used a direct dictionary lookup:

```python
character_id = ids[holder]
```

A missing key raises `KeyError` with no context.

**Fix.** Catch the missing name and raise a clear `ValueError`:

```python
try:
    character_id = ids[holder]
except KeyError:
    raise ValueError(
        f"{Path(csv_path).name} line {line_no}: "
        f"unknown character_name {holder!r}"
    ) from None
```

**Regression test.** `tests/test_build.py::test_unknown_character_name_reports_line`
uses a CSV containing `Nobody` on line 2 and asserts that the error names the
line and the bad value.

**Lesson.** Error messages are part of the user interface. A loader should say
where the bad data is, not just that a dictionary key was missing.

---

## What is not in this log

Syntax errors and failed experiments from learning SQL are not defects. A
defect here means the project produced a wrong result or lost data, and the fix
is covered by a test. Four defects met that bar; the target was 3–5.

## Regression check

Run the whole suite:

```bash
.venv/bin/python -m pytest -q
```

All four regression tests are part of the 50-test suite. If any defect returns,
the suite fails.
