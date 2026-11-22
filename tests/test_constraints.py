"""Tests that the schema rejects invalid data and handles deletion safely."""

import sqlite3

import pytest


def character_id(conn, name):
    return conn.execute(
        "SELECT character_id FROM characters WHERE name = ?", (name,)
    ).fetchone()[0]


def test_duplicate_character_name_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('jill', 'Tank', 10, 100)"""
        )


def test_blank_character_name_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('   ', 'Tank', 10, 100)"""
        )


def test_invalid_role_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('Test wizard', 'Wizard', 10, 100)"""
        )


def test_level_outside_range_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('Test hero', 'Tank', 61, 100)"""
        )


def test_level_boundaries(conn):
    conn.execute(
        """INSERT INTO characters (name, role, level, budget_gold)
           VALUES ('Level one', 'Tank', 1, 100)"""
    )
    conn.execute(
        """INSERT INTO characters (name, role, level, budget_gold)
           VALUES ('Level sixty', 'Tank', 60, 100)"""
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('Level zero', 'Tank', 0, 100)"""
        )


def test_negative_budget_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('Test pauper', 'Tank', 10, -1)"""
        )


def test_duplicate_equipment_name_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('scorpion blade', 'Weapon', 'Rare', 10, 1)"""
        )


def test_blank_equipment_name_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('   ', 'Weapon', 'Rare', 10, 1)"""
        )


def test_invalid_slot_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('Test ring', 'Finger', 'Rare', 10, 1)"""
        )


def test_invalid_rarity_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('Test ring', 'Accessory', 'Mythic', 10, 1)"""
        )


def test_zero_cost_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('Test ring', 'Accessory', 'Common', 0, 1)"""
        )


def test_negative_cost_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('Test ring', 'Accessory', 'Common', -10, 1)"""
        )


def test_negative_stat_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus)
               VALUES ('Test ring', 'Accessory', 'Common', 10, -1)"""
        )


def test_item_with_no_effect_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold)
               VALUES ('Test ring', 'Accessory', 'Common', 10)"""
        )


def test_strict_table_rejects_wrong_type(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO characters (name, role, level, budget_gold)
               VALUES ('Test type', 'Tank', 'thirty', 100)"""
        )


def test_second_equipped_item_in_same_slot_is_rejected(conn):
    jill = character_id(conn, "Jill")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus, character_id)
               VALUES ('Second staff', 'Weapon', 'Common', 10, 1, ?)""",
            (jill,),
        )


def test_multiple_vault_items_in_same_slot_are_allowed(conn):
    conn.execute(
        """INSERT INTO equipment
           (name, slot, rarity, cost_gold, attack_bonus)
           VALUES ('Vault blade one', 'Weapon', 'Common', 10, 1)"""
    )
    conn.execute(
        """INSERT INTO equipment
           (name, slot, rarity, cost_gold, attack_bonus)
           VALUES ('Vault blade two', 'Weapon', 'Common', 12, 2)"""
    )
    count = conn.execute(
        """SELECT COUNT(*) FROM equipment
           WHERE slot = 'Weapon' AND character_id IS NULL"""
    ).fetchone()[0]
    assert count >= 4


def test_orphan_equipment_is_rejected(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO equipment
               (name, slot, rarity, cost_gold, attack_bonus, character_id)
               VALUES ('Orphan blade', 'Weapon', 'Common', 10, 1, 9999)"""
        )


def test_delete_character_returns_gear_to_vault(conn):
    jill = character_id(conn, "Jill")
    conn.execute("DELETE FROM characters WHERE character_id = ?", (jill,))
    rows = conn.execute(
        """SELECT character_id
           FROM equipment
           WHERE name IN ('Stave of Sunlight', 'Priest robes')"""
    ).fetchall()
    assert rows == [(None,), (None,)]


def test_item_can_be_reassigned(conn):
    santos = character_id(conn, "Santos")
    conn.execute(
        """UPDATE equipment
           SET character_id = ?
           WHERE name = 'Priest robes'""",
        (santos,),
    )
    owner = conn.execute(
        """SELECT c.name
           FROM equipment e
           JOIN characters c ON c.character_id = e.character_id
           WHERE e.name = 'Priest robes'"""
    ).fetchone()[0]
    assert owner == "Santos"
