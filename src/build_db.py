"""Build guild.db from the seed CSVs."""

import csv
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "guild.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
VIEWS_PATH = ROOT / "sql" / "views.sql"
CHARACTERS_CSV = ROOT / "data" / "characters.csv"
EQUIPMENT_CSV = ROOT / "data" / "equipment.csv"


def load_characters(conn, csv_path=CHARACTERS_CSV):
    """Load character rows from CSV into an open connection."""
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for line_no, row in enumerate(reader, start=2):
            try:
                conn.execute(
                    """INSERT INTO characters (name, role, level, budget_gold)
                       VALUES (?, ?, ?, ?)""",
                    (
                        row["name"].strip(),
                        row["role"].strip(),
                        int(row["level"]),
                        int(row["budget_gold"]),
                    ),
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(
                    f"{Path(csv_path).name} line {line_no}: {exc}"
                ) from exc


def load_equipment(conn, csv_path=EQUIPMENT_CSV):
    """Load equipment rows, turning character names into foreign keys."""
    ids = {
        name: character_id
        for character_id, name in conn.execute(
            "SELECT character_id, name FROM characters"
        )
    }

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for line_no, row in enumerate(reader, start=2):
            holder = row["character_name"].strip()
            if holder:
                try:
                    character_id = ids[holder]
                except KeyError:
                    raise ValueError(
                        f"{Path(csv_path).name} line {line_no}: "
                        f"unknown character_name {holder!r}"
                    ) from None
            else:
                character_id = None

            try:
                conn.execute(
                    """INSERT INTO equipment
                       (name, slot, rarity, cost_gold,
                        attack_bonus, defense_bonus, healing_bonus, speed_bonus,
                        character_id)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        row["name"].strip(),
                        row["slot"].strip(),
                        row["rarity"].strip(),
                        int(row["cost_gold"]),
                        int(row["attack_bonus"]),
                        int(row["defense_bonus"]),
                        int(row["healing_bonus"]),
                        int(row["speed_bonus"]),
                        character_id,
                    ),
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(
                    f"{Path(csv_path).name} line {line_no}: {exc}"
                ) from exc


def build(db_path=DB_PATH, characters_csv=CHARACTERS_CSV, equipment_csv=EQUIPMENT_CSV):
    """Build a database at db_path and return the path.

    The database is built in a temporary file. It replaces the target only
    after the foreign-key and integrity checks pass, so a failed build leaves
    the previous good database untouched.
    """
    db_path = Path(db_path)
    temp_path = db_path.with_name(db_path.name + ".tmp")
    if temp_path.exists():
        temp_path.unlink()

    conn = sqlite3.connect(temp_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_PATH.read_text())
        conn.executescript(VIEWS_PATH.read_text())
        load_characters(conn, characters_csv)
        load_equipment(conn, equipment_csv)

        problems = conn.execute("PRAGMA foreign_key_check").fetchall()
        if problems:
            raise RuntimeError(f"Foreign key problems: {problems}")

        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise RuntimeError(f"Integrity check failed: {result}")

        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        temp_path.unlink(missing_ok=True)
        raise
    else:
        conn.close()
        os.replace(temp_path, db_path)

    print(f"Built {db_path}")
    return db_path


if __name__ == "__main__":
    build()
