-- Q3: Which vault items are the best value per gold, by slot and role?
-- The same item can be worth different amounts to different roles, so the
-- query scores every vault item once per role. ROW_NUMBER() then picks the
-- best value item in each role/slot pair.
--
-- power_per_100g = 100 * item_power / cost_gold. A higher number means more
-- role power for each 100 gold spent.

WITH roles(role) AS (
    VALUES ('Tank'), ('Healer'), ('Damage'), ('Support')
),
vault AS (
    SELECT
        name,
        slot,
        cost_gold,
        attack_bonus,
        defense_bonus,
        healing_bonus,
        speed_bonus
    FROM equipment
    WHERE character_id IS NULL
),
scored AS (
    SELECT
        r.role,
        v.slot,
        v.name AS item,
        v.cost_gold,
        CASE r.role
            WHEN 'Tank'    THEN v.defense_bonus * 3 + v.attack_bonus + v.speed_bonus
            WHEN 'Healer'  THEN v.healing_bonus * 3 + v.defense_bonus + v.speed_bonus
            WHEN 'Support' THEN v.healing_bonus * 2 + v.speed_bonus * 2 + v.defense_bonus
            WHEN 'Damage'  THEN v.attack_bonus * 3 + v.speed_bonus
        END AS item_power
    FROM roles r
    CROSS JOIN vault v
),
valued AS (
    SELECT
        *,
        ROUND(100.0 * item_power / cost_gold, 2) AS power_per_100g
    FROM scored
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY role, slot
            ORDER BY power_per_100g DESC, item_power DESC, cost_gold ASC
        ) AS value_rank
    FROM valued
)
SELECT
    role,
    slot,
    item,
    cost_gold,
    item_power,
    power_per_100g
FROM ranked
WHERE value_rank = 1
ORDER BY role, slot;
