"""Tests for the physical schema."""


def test_tables_exist(conn):
    names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    assert {"characters", "equipment"} <= names


def test_tables_are_strict(conn):
    for table in ("characters", "equipment"):
        strict = conn.execute(
            "SELECT strict FROM pragma_table_list WHERE name = ?", (table,)
        ).fetchone()[0]
        assert strict == 1, f"{table} should be STRICT"


def test_view_exists(conn):
    count = conn.execute(
        """SELECT COUNT(*)
           FROM sqlite_master
           WHERE type = 'view' AND name = 'v_character_loadout'"""
    ).fetchone()[0]
    assert count == 1


def test_view_has_derived_columns(conn):
    columns = {
        row[1] for row in conn.execute("PRAGMA table_info(v_character_loadout)")
    }
    expected = {
        "items_equipped",
        "gear_cost",
        "budget_remaining",
        "budget_status",
        "role_power",
        "power_per_100g",
        "slots_filled",
        "empty_slots",
    }
    assert expected <= columns


def test_equipment_has_foreign_key_to_characters(conn):
    foreign_keys = conn.execute("PRAGMA foreign_key_list(equipment)").fetchall()
    assert any(
        fk[2] == "characters" and fk[3] == "character_id" for fk in foreign_keys
    )
