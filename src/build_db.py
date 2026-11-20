"""Build guild.db from the seed CSVs."""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "guild.db"
SCHEMA_PATH = ROOT / "sql" / "schema.sql"
CHARACTERS_CSV = ROOT / "data" / "characters.csv"
EQUIPMENT_CSV = ROOT / "data" / "equipment.csv"

def build():
    # 1. Delete an existing guild.db so every build starts fresh.
    if DB_PATH.exists():
        DB_PATH.unlink()
    # 2. Open a connection to DB_PATH.
    conn = sqlite3.connect(DB_PATH)
    # 3. Turn foreign keys on for this connection.
    conn.execute("PRAGMA foreign_keys = ON")
    # 4. Run the SQL in SCHEMA_PATH with conn.executescript(...).
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)
    # 5. Open a CSV reader for CHARACTERS_CSV.
    with open(CHARACTERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace = True)
        # 6. For each row in reader, execute an INSERT statement into the characters table.
        for row in reader:
            conn.execute(
                """INSERT INTO characters (name, role, level, budget_gold)
                    VALUES (?, ?, ?, ?)""",
                (row["name"].strip(), row["role"].strip(), int(row["level"]), int(row["budget_gold"])),
            )
    # 6. Build a lookup table for characters by name.
    ids = {}
    for character_ids, name in conn.execute("SELECT character_id, name FROM characters"):
        ids[name] = character_ids
    # 7. Open a CSV reader for EQUIPMENT_CSV.
    with open(EQUIPMENT_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace = True)
        for row in reader:
            holder = row["character_name"].strip()
            character_id = ids[holder] if holder else None

            conn.execute(
                """INSERT INTO equipment
                (name, slot, rarity, cost_gold,
                attack_bonus, defense_bonus, healing_bonus, speed_bonus,
                character_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["name"], row["slot"], row["rarity"],
                    int(row["cost_gold"]), int(row["attack_bonus"]),
                    int(row["defense_bonus"]), int(row["healing_bonus"]),
                    int(row["speed_bonus"]), character_id
                )
            )
    # 8. Make the database build fail if unhealthy.
    problems = conn.execute("PRAGMA foreign_key_check").fetchall()
    if problems:
        raise RuntimeError(f"Foreign key problems: {problems}")
    result = conn.execute("PRAGMA integrity_check").fetchone()[0]
    if result != "ok":
        raise RuntimeError(f"Integrity check failed: {result}")
    # Commit, close, and print a one-line confirmation.
    conn.commit()
    conn.close()
    print(f"Built {DB_PATH}")

if __name__ == "__main__":
    build()