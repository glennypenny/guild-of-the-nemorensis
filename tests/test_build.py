"""Tests for the build pipeline itself."""

import sqlite3

import pytest

from build_db import build


def test_build_creates_database_and_view(tmp_path):
    db_path = tmp_path / "guild.db"
    build(db_path)

    assert db_path.exists()
    with sqlite3.connect(db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0] == 12
        assert conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0] == 40
        assert conn.execute(
            """SELECT COUNT(*) FROM sqlite_master
               WHERE type = 'view' AND name = 'v_character_loadout'"""
        ).fetchone()[0] == 1


def test_build_leaves_no_temp_file(tmp_path):
    db_path = tmp_path / "guild.db"
    build(db_path)
    assert not db_path.with_name(db_path.name + ".tmp").exists()


def test_failed_build_keeps_previous_database(tmp_path):
    db_path = tmp_path / "guild.db"
    build(db_path)
    before = db_path.read_bytes()

    bad_characters = tmp_path / "bad_characters.csv"
    bad_characters.write_text(
        "name,role,level,budget_gold\n"
        "Jill,Healer,29,100\n"
        "Jill,Tank,20,100\n",
        encoding="utf-8",
    )

    with pytest.raises(sqlite3.IntegrityError):
        build(db_path, characters_csv=bad_characters)

    assert db_path.read_bytes() == before
    assert not db_path.with_name(db_path.name + ".tmp").exists()


def test_unknown_character_name_reports_line(tmp_path):
    db_path = tmp_path / "guild.db"
    bad_equipment = tmp_path / "bad_equipment.csv"
    bad_equipment.write_text(
        "name,slot,rarity,cost_gold,attack_bonus,defense_bonus,"
        "healing_bonus,speed_bonus,character_name\n"
        "Test blade,Weapon,Common,10,1,0,0,0,Nobody\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 2.*Nobody"):
        build(db_path, equipment_csv=bad_equipment)

    assert not db_path.exists()


def test_build_is_reproducible(tmp_path):
    first = tmp_path / "first.db"
    second = tmp_path / "second.db"
    build(first)
    build(second)

    def snapshot(path):
        with sqlite3.connect(path) as conn:
            counts = (
                conn.execute("SELECT COUNT(*) FROM characters").fetchone()[0],
                conn.execute("SELECT COUNT(*) FROM equipment").fetchone()[0],
            )
            powers = conn.execute(
                "SELECT name, role_power FROM v_character_loadout ORDER BY name"
            ).fetchall()
        return counts, powers

    assert snapshot(first) == snapshot(second)
