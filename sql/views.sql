DROP VIEW IF EXISTS v_character_loadout;

CREATE VIEW v_character_loadout AS
WITH loadout AS (
    SELECT
        c.character_id,
        c.name,
        c.role,
        c.level,
        c.budget_gold,
        COUNT(e.equipment_id) AS items_equipped,
        COALESCE(SUM(e.cost_gold), 0) AS gear_cost,
        COALESCE(
            SUM(
                CASE c.role
                    WHEN 'Tank'    THEN e.defense_bonus * 3 + e.attack_bonus + e.speed_bonus
                    WHEN 'Healer'  THEN e.healing_bonus * 3 + e.defense_bonus + e.speed_bonus
                    WHEN 'Support' THEN e.healing_bonus * 2 + e.speed_bonus * 2 + e.defense_bonus
                    WHEN 'Damage'  THEN e.attack_bonus * 3 + e.speed_bonus
                END
            ),
            0
        ) AS role_power,
        COUNT(DISTINCT e.slot) AS slots_filled,
        7 - COUNT(DISTINCT e.slot) AS empty_slots
    FROM characters c
    LEFT JOIN equipment e ON e.character_id = c.character_id
    GROUP BY c.character_id
)
SELECT
    character_id,
    name,
    role,
    level,
    budget_gold,
    items_equipped,
    gear_cost,
    budget_gold - gear_cost AS budget_remaining,
    CASE
        WHEN gear_cost > budget_gold THEN 'Over'
        WHEN gear_cost = budget_gold THEN 'At'
        ELSE 'Under'
    END AS budget_status,
    role_power,
    CASE
        WHEN gear_cost = 0 THEN NULL
        ELSE ROUND(100.0 * role_power / gear_cost, 2)
    END AS power_per_100g,
    slots_filled,
    empty_slots
FROM loadout;
