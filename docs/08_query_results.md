# Query Results — Guild of the Nemorensis

| Field | Value |
|---|---|
| Status | Complete |
| Database | `guild.db`, built from 12 characters and 40 items |
| Queries | 8 |
| Last run | 2026-11-22 |

These are the actual outputs from the eight analysis queries. They are
generated from the seed data, not typed by hand.

Run any query with:

```bash
sqlite3 -header -column guild.db < sql/queries/01_loadout_audit.sql
```

The tables below are formatted as Markdown for readability. The CLI layout
depends on your SQLite version; `-column`, `-box`, or `-markdown` all work on
recent versions.

---

## Q1 — Which characters need attention?

A character needs attention if they have fewer than three items equipped or
if their gear costs more than their budget. Over-budget characters are listed
first.

File: `sql/queries/01_loadout_audit.sql`

|  name   |  role   | items_equipped | empty_slots | under_equipped | gear_cost | budget_gold | budget_remaining | budget_status | role_power |
|---------|---------|----------------|-------------|----------------|-----------|-------------|------------------|---------------|------------|
| Jill    | Healer  | 2              | 5           | Yes            | 110       | 100         | -10              | Over          | 50         |
| Tamsin  | Support | 2              | 5           | Yes            | 235       | 230         | -5               | Over          | 66         |
| Rook    | Damage  | 3              | 4           | No             | 250       | 180         | -70              | Over          | 78         |
| Orla    | Tank    | 4              | 3           | No             | 420       | 380         | -40              | Over          | 144        |
| Corin   | Support | 0              | 7           | Yes            | 0         | 190         | 190              | Under         | 0          |
| Halvard | Tank    | 2              | 5           | Yes            | 75        | 75          | 0                | At            | 32         |
| Maelin  | Healer  | 2              | 5           | Yes            | 110       | 220         | 110              | Under         | 49         |
| Nia     | Support | 2              | 5           | Yes            | 90        | 170         | 80               | Under         | 37         |
| Santos  | Damage  | 2              | 5           | Yes            | 130       | 290         | 160              | Under         | 50         |
| Vexa    | Damage  | 2              | 5           | Yes            | 235       | 235         | 0                | At            | 59         |
| Ysolde  | Healer  | 2              | 5           | Yes            | 115       | 260         | 145              | Under         | 43         |

**Reading it:** 11 of 12 characters need attention. Brabby is the only one who
is both adequately equipped (3 items) and under budget. Corin has no gear at
all, but is under budget, so the recommendation query can still help.

---

## Q2 — Who is strongest for their role?

`RANK()` numbers characters inside their own role. A rank of 1 is the best in
that role; `gap_to_best` shows how far behind the leader each character is.

File: `sql/queries/02_role_power_ranking.sql`

|  name   |  role   | role_power | role_rank | gap_to_best | power_per_100g |
|---------|---------|------------|-----------|-------------|----------------|
| Rook    | Damage  | 78         | 1         | 0           | 31.2           |
| Vexa    | Damage  | 59         | 2         | 19          | 25.11          |
| Santos  | Damage  | 50         | 3         | 28          | 38.46          |
| Jill    | Healer  | 50         | 1         | 0           | 45.45          |
| Maelin  | Healer  | 49         | 2         | 1           | 44.55          |
| Ysolde  | Healer  | 43         | 3         | 7           | 37.39          |
| Tamsin  | Support | 66         | 1         | 0           | 28.09          |
| Nia     | Support | 37         | 2         | 29          | 41.11          |
| Corin   | Support | 0          | 3         | 66          |                |
| Orla    | Tank    | 144        | 1         | 0           | 34.29          |
| Brabby  | Tank    | 80         | 2         | 64          | 50.0           |
| Halvard | Tank    | 32         | 3         | 112         | 42.67          |

**Reading it:** Orla is the strongest tank by a wide margin, but she is also
over budget. Brabby has lower power but the best efficiency in the role. Rook
leads Damage; Corin has no gear, so `role_power` is 0 and `power_per_100g` is
`NULL`.

---

## Q3 — Which vault items are the best value per gold, by slot and role?

Every vault item is scored once per role. `ROW_NUMBER()` picks the best value
item in each role/slot pair.

File: `sql/queries/03_vault_value_by_role.sql`

|  role   |   slot    |        item        | cost_gold | item_power | power_per_100g |
|---------|-----------|--------------------|-----------|------------|----------------|
| Damage  | Accessory | Owl's eye pendant  | 120       | 15         | 12.5           |
| Damage  | Chest     | Tank top           | 200       | 20         | 10.0           |
| Damage  | Feet      | Iron-toed boots    | 55        | 4          | 7.27           |
| Damage  | Head      | Traveler's hood    | 20        | 2          | 10.0           |
| Damage  | Legs      | Runner's leggings  | 85        | 15         | 17.65          |
| Damage  | Off-hand  | Sharp shiv         | 70        | 15         | 21.43          |
| Damage  | Weapon    | Oakfall club       | 25        | 12         | 48.0           |
| Healer  | Accessory | Owl's eye pendant  | 120       | 27         | 22.5           |
| Healer  | Chest     | Tank top           | 200       | 25         | 12.5           |
| Healer  | Feet      | Iron-toed boots    | 55        | 7          | 12.73          |
| Healer  | Head      | Traveler's hood    | 20        | 10         | 50.0           |
| Healer  | Legs      | Runner's leggings  | 85        | 10         | 11.76          |
| Healer  | Off-hand  | Kite shield        | 60        | 10         | 16.67          |
| Healer  | Weapon    | Pilgrim's staff    | 45        | 24         | 53.33          |
| Support | Accessory | Owl's eye pendant  | 120       | 26         | 21.67          |
| Support | Chest     | Moth-eaten cloak   | 35        | 5          | 14.29          |
| Support | Feet      | Iron-toed boots    | 55        | 8          | 14.55          |
| Support | Head      | Traveler's hood    | 20        | 10         | 50.0           |
| Support | Legs      | Runner's leggings  | 85        | 19         | 22.35          |
| Support | Off-hand  | Gloves of the wind | 70        | 15         | 21.43          |
| Support | Weapon    | Pilgrim's staff    | 45        | 18         | 40.0           |
| Tank    | Accessory | Owl's eye pendant  | 120       | 9          | 7.5            |
| Tank    | Chest     | Moth-eaten cloak   | 35        | 10         | 28.57          |
| Tank    | Feet      | Iron-toed boots    | 55        | 20         | 36.36          |
| Tank    | Head      | Traveler's hood    | 20        | 8          | 40.0           |
| Tank    | Legs      | Runner's leggings  | 85        | 14         | 16.47          |
| Tank    | Off-hand  | Kite shield        | 60        | 30         | 50.0           |
| Tank    | Weapon    | Oakfall club       | 25        | 7          | 28.0           |

**Reading it:** 28 role/slot pairs, one winner each. The same item can have a
different value to different roles: the Owl's eye pendant is worth 27 to a
Healer, 26 to Support, 15 to Damage, and 9 to a Tank.

---

## Q4 — What is the best affordable next upgrade for each empty slot?

Builds every empty slot, joins it to affordable vault items of the same slot,
scores them for the character's role, and keeps the highest-power item per
slot.

File: `sql/queries/04_best_affordable_upgrade.sql`

| character |  role   |   slot    |        item        | cost_gold | item_power | budget_remaining |
|-----------|---------|-----------|--------------------|-----------|------------|------------------|
| Brabby    | Tank    | Chest     | Moth-eaten cloak   | 35        | 10         | 40               |
| Brabby    | Tank    | Weapon    | Oakfall club       | 25        | 7          | 40               |
| Corin     | Support | Accessory | Owl's eye pendant  | 120       | 26         | 190              |
| Corin     | Support | Chest     | Moth-eaten cloak   | 35        | 5          | 190              |
| Corin     | Support | Feet      | Iron-toed boots    | 55        | 8          | 190              |
| Corin     | Support | Head      | Traveler's hood    | 20        | 10         | 190              |
| Corin     | Support | Legs      | Runner's leggings  | 85        | 19         | 190              |
| Corin     | Support | Off-hand  | Gloves of the wind | 70        | 15         | 190              |
| Corin     | Support | Weapon    | Pilgrim's staff    | 45        | 18         | 190              |
| Maelin    | Healer  | Accessory | Ring of the wind   | 80        | 5          | 110              |
| Maelin    | Healer  | Feet      | Iron-toed boots    | 55        | 7          | 110              |
| Maelin    | Healer  | Head      | Traveler's hood    | 20        | 10         | 110              |
| Maelin    | Healer  | Legs      | Runner's leggings  | 85        | 10         | 110              |
| Maelin    | Healer  | Off-hand  | Kite shield        | 60        | 10         | 110              |
| Nia       | Support | Accessory | Ring of the wind   | 80        | 10         | 80               |
| Nia       | Support | Chest     | Moth-eaten cloak   | 35        | 5          | 80               |
| Nia       | Support | Feet      | Iron-toed boots    | 55        | 8          | 80               |
| Nia       | Support | Weapon    | Pilgrim's staff    | 45        | 18         | 80               |
| Santos    | Damage  | Chest     | Moth-eaten cloak   | 35        | 1          | 160              |
| Santos    | Damage  | Feet      | Iron-toed boots    | 55        | 4          | 160              |
| Santos    | Damage  | Head      | Traveler's hood    | 20        | 2          | 160              |
| Santos    | Damage  | Legs      | Runner's leggings  | 85        | 15         | 160              |
| Santos    | Damage  | Off-hand  | Sharp shiv         | 70        | 15         | 160              |
| Ysolde    | Healer  | Chest     | Moth-eaten cloak   | 35        | 4          | 145              |
| Ysolde    | Healer  | Head      | Traveler's hood    | 20        | 10         | 145              |
| Ysolde    | Healer  | Legs      | Runner's leggings  | 85        | 10         | 145              |
| Ysolde    | Healer  | Off-hand  | Kite shield        | 60        | 10         | 145              |
| Ysolde    | Healer  | Weapon    | Pilgrim's staff    | 45        | 24         | 145              |

**Reading it:** 28 affordable recommendations across six characters. Over-budget
characters (Jill, Tamsin, Rook, Orla) have no affordable upgrade, so they do not
appear. Halvard and Vexa are exactly at budget, so they also have nothing left
to spend. Q1 flags all of them.

---

## Q5 — Does the data obey the guild's rules?

Each row is one check. A healthy database returns zero failures for all checks.

File: `sql/queries/05_data_quality_checks.sql`

|              check_name               | failures |
|---------------------------------------|----------|
| characters with more than seven items | 0        |
| double-booked slots                   | 0        |
| duplicate character names             | 0        |
| duplicate equipment names             | 0        |
| invalid character roles               | 0        |
| invalid equipment slots               | 0        |
| invalid rarities                      | 0        |
| items with no effect                  | 0        |
| negative stat bonuses                 | 0        |
| non-positive item costs               | 0        |
| orphan equipment                      | 0        |

**Reading it:** all 11 checks pass. The schema should make these impossible;
this query is a second line of defence and is also asserted in the test suite.

---

## Q6 — How many characters are over, at, or under budget?

File: `sql/queries/06_budget_summary.sql`

| budget_status | characters | avg_role_power | total_gear_cost | avg_budget_remaining |
|---------------|------------|----------------|-----------------|----------------------|
| Over          | 4          | 84.5           | 1015            | -31.3                |
| At            | 2          | 45.5           | 310             | 0.0                  |
| Under         | 6          | 43.2           | 605             | 120.8                |

**Reading it:** four characters are over budget, two are exactly at budget,
and six are under. The over-budget group has the highest average power, which
fits the story: strong gear is expensive.

---

## Q7 — How does each role compare?

File: `sql/queries/07_role_summary.sql`

|  role   | characters | avg_role_power | best_role_power | avg_items | total_empty_slots | over_budget |
|---------|------------|----------------|-----------------|-----------|-------------------|-------------|
| Tank    | 3          | 85.3           | 144             | 3.0       | 12                | 1           |
| Damage  | 3          | 62.3           | 78              | 2.3       | 14                | 1           |
| Healer  | 3          | 47.3           | 50              | 2.0       | 15                | 1           |
| Support | 3          | 34.3           | 66              | 1.3       | 17                | 1           |

**Reading it:** every role has three characters and one over-budget character.
Tank has the highest average power; Support has the most empty slots and the
lowest average gear count. That is the clearest place to spend the next gold.

---

## Q8 — What is sitting in the vault?

File: `sql/queries/08_vault_composition.sql`

|   slot    | items | total_value | avg_cost | pct_of_vault_value | value_rank |
|-----------|-------|-------------|----------|--------------------|------------|
| Chest     | 2     | 235         | 117.5    | 23.6               | 1          |
| Off-hand  | 4     | 230         | 57.5     | 23.1               | 2          |
| Accessory | 2     | 200         | 100.0    | 20.1               | 3          |
| Weapon    | 3     | 170         | 56.7     | 17.1               | 4          |
| Legs      | 1     | 85          | 85.0     | 8.5                | 5          |
| Feet      | 1     | 55          | 55.0     | 5.5                | 6          |
| Head      | 1     | 20          | 20.0     | 2.0                | 7          |

**Reading it:** the vault holds 14 items worth 995 gold. Chest and Off-hand
account for almost half of the vault's value. Head is the cheapest and least
stocked slot, which matches Q4: Traveler's hood is the only head upgrade.

---

## Summary

| Query | Technique | Rows |
|---|---|---:|
| Q1 Loadout audit | View, `CASE`, `WHERE`, `ORDER BY` | 11 |
| Q2 Role ranking | `RANK()`, `PARTITION BY` | 12 |
| Q3 Vault value | `CROSS JOIN`, CTE, `ROW_NUMBER()` | 28 |
| Q4 Affordable upgrade | CTE, `NOT EXISTS`, `ROW_NUMBER()` | 28 |
| Q5 Data quality | `UNION ALL`, aggregate checks | 11 |
| Q6 Budget summary | `GROUP BY`, aggregates | 3 |
| Q7 Role summary | `GROUP BY`, conditional aggregate | 4 |
| Q8 Vault composition | CTE, window `RANK()`, scalar subquery | 7 |

All eight queries run against the same 12-character, 40-item database. The
tests execute these files directly, so the outputs and the test expectations
cannot drift apart silently.
