DROP VIEW IF EXISTS v_character_loadout;

CREATE VIEW v_character_loadout AS
SELECT
    c.character_id,
    c.name,
    c.role,
    c.level,
    c.budget_gold,
    COUNT(e.equipment_id) AS items_equipped,
    COALESCE(SUM(e.cost_gold), 0) AS gear_cost,
    c.budget_gold - COALESCE(SUM(e.cost_gold), 0) AS budget_remaining,
    COUNT(DISTINCT e.slot) AS slots_filled,
    7 - COUNT(DISTINCT e.slot) AS empty_slots
FROM characters c
LEFT JOIN equipment e ON e.character_id = c.character_id
GROUP BY c.character_id;