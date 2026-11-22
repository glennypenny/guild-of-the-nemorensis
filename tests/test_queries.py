"""Run every analysis query and check its shape and known results."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
QUERY_DIR = ROOT / "sql" / "queries"


def run_query(conn, filename):
    sql = (QUERY_DIR / filename).read_text()
    return conn.execute(sql).fetchall()


def test_q1_loadout_audit(conn):
    rows = run_query(conn, "01_loadout_audit.sql")
    assert len(rows) == 11
    for row in rows:
        items_equipped = row[2]
        budget_status = row[8]
        assert items_equipped < 3 or budget_status == "Over"
    assert rows[0][8] == "Over"


def test_q2_role_power_ranking(conn):
    rows = run_query(conn, "02_role_power_ranking.sql")
    assert len(rows) == 12

    ranks_by_role = {}
    for name, role, role_power, role_rank, gap_to_best, power_per_100g in rows:
        ranks_by_role.setdefault(role, []).append(role_rank)
        assert gap_to_best >= 0
        assert role_power >= 0

    assert set(ranks_by_role) == {"Tank", "Healer", "Damage", "Support"}
    for ranks in ranks_by_role.values():
        assert sorted(ranks) == [1, 2, 3]


def test_q3_vault_value_by_role(conn):
    rows = run_query(conn, "03_vault_value_by_role.sql")
    assert len(rows) == 28
    pairs = {(role, slot) for role, slot, item, cost, power, value in rows}
    assert len(pairs) == 28
    assert all(cost > 0 for role, slot, item, cost, power, value in rows)
    assert all(value > 0 for role, slot, item, cost, power, value in rows)


def test_q4_best_affordable_upgrade(conn):
    rows = run_query(conn, "04_best_affordable_upgrade.sql")
    assert len(rows) == 28

    pairs = {(row[0], row[2]) for row in rows}
    assert len(pairs) == 28

    vault_items = {
        name
        for name, in conn.execute(
            "SELECT name FROM equipment WHERE character_id IS NULL"
        )
    }
    for character, role, slot, item, cost_gold, item_power, budget_remaining in rows:
        assert item in vault_items
        assert cost_gold <= budget_remaining
        assert item_power > 0


def test_q5_data_quality_checks(conn):
    rows = run_query(conn, "05_data_quality_checks.sql")
    assert len(rows) == 11
    assert all(failures == 0 for check_name, failures in rows)
    assert sum(failures for check_name, failures in rows) == 0


def test_q6_budget_summary(conn):
    rows = run_query(conn, "06_budget_summary.sql")
    assert len(rows) == 3
    summary = {row[0]: row[1] for row in rows}
    assert summary == {"Over": 4, "At": 2, "Under": 6}
    assert sum(summary.values()) == 12


def test_q7_role_summary(conn):
    rows = run_query(conn, "07_role_summary.sql")
    assert len(rows) == 4
    assert {row[0] for row in rows} == {"Tank", "Healer", "Damage", "Support"}
    assert sum(row[1] for row in rows) == 12
    assert sum(row[6] for row in rows) == 4


def test_q8_vault_composition(conn):
    rows = run_query(conn, "08_vault_composition.sql")
    assert len(rows) == 7
    assert sum(row[1] for row in rows) == 14
    assert sorted(row[5] for row in rows) == [1, 2, 3, 4, 5, 6, 7]
    assert sum(row[4] for row in rows) == pytest.approx(100.0, abs=0.5)

    vault_total = conn.execute(
        "SELECT SUM(cost_gold) FROM equipment WHERE character_id IS NULL"
    ).fetchone()[0]
    assert sum(row[2] for row in rows) == vault_total
