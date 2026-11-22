"""Tests for the seed data and the derived loadout view."""

EXPECTED_ROLE_POWER = {
    "Brabby": 80,
    "Jill": 50,
    "Orla": 144,
    "Rook": 78,
}


def test_character_count(conn):
    assert conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 12


def test_equipment_count(conn):
    assert conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0] == 40


def test_equipped_and_vault_counts(conn):
    equipped, vault = conn.execute(
        """SELECT
               SUM(CASE WHEN character_id IS NULL THEN 0 ELSE 1 END),
               SUM(CASE WHEN character_id IS NULL THEN 1 ELSE 0 END)
           FROM equipment"""
    ).fetchone()
    assert (equipped, vault) == (26, 14)


def test_every_character_has_at_most_seven_items(conn):
    worst = conn.execute(
        """SELECT MAX(items)
           FROM (
               SELECT COUNT(*) AS items
               FROM equipment
               WHERE character_id IS NOT NULL
               GROUP BY character_id
           )"""
    ).fetchone()[0]
    assert worst <= 7


def test_no_orphan_equipment(conn):
    orphans = conn.execute(
        """SELECT COUNT(*)
           FROM equipment e
           LEFT JOIN characters c ON c.character_id = e.character_id
           WHERE e.character_id IS NOT NULL
             AND c.character_id IS NULL"""
    ).fetchone()[0]
    assert orphans == 0


def test_no_double_booked_slots(conn):
    duplicates = conn.execute(
        """SELECT COUNT(*)
           FROM (
               SELECT character_id, slot
               FROM equipment
               WHERE character_id IS NOT NULL
               GROUP BY character_id, slot
               HAVING COUNT(*) > 1
           )"""
    ).fetchone()[0]
    assert duplicates == 0


def test_every_slot_has_a_vault_item(conn):
    slots = {
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT slot FROM equipment WHERE character_id IS NULL"
        )
    }
    assert slots == {
        "Weapon",
        "Off-hand",
        "Head",
        "Chest",
        "Legs",
        "Feet",
        "Accessory",
    }


def test_integrity_check_is_ok(conn):
    assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_foreign_key_check_is_empty(conn):
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_known_role_power_values(conn):
    actual = {
        name: power
        for name, power in conn.execute(
            "SELECT name, role_power FROM v_character_loadout"
        )
    }
    for name, expected in EXPECTED_ROLE_POWER.items():
        assert actual[name] == expected


def test_budget_status_matches_arithmetic(conn):
    rows = conn.execute(
        """SELECT gear_cost, budget_gold, budget_remaining, budget_status
           FROM v_character_loadout"""
    ).fetchall()
    for gear_cost, budget_gold, remaining, status in rows:
        assert remaining == budget_gold - gear_cost
        if gear_cost > budget_gold:
            assert status == "Over"
        elif gear_cost == budget_gold:
            assert status == "At"
        else:
            assert status == "Under"


def test_character_with_no_items_appears_in_loadout(conn):
    row = conn.execute(
        """SELECT items_equipped, gear_cost, role_power, empty_slots,
                  budget_remaining, budget_status, power_per_100g
           FROM v_character_loadout
           WHERE name = 'Corin'"""
    ).fetchone()
    assert row == (0, 0, 0, 7, 190, "Under", None)
