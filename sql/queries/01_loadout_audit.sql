-- Q1: Which characters need attention?
-- A character needs attention if they have fewer than three items equipped
-- (more than four empty slots) or if their gear costs more than their budget.
-- Over-budget characters are listed first.

SELECT
    name,
    role,
    items_equipped,
    empty_slots,
    CASE WHEN items_equipped < 3 THEN 'Yes' ELSE 'No' END AS under_equipped,
    gear_cost,
    budget_gold,
    budget_remaining,
    budget_status,
    role_power
FROM v_character_loadout
WHERE items_equipped < 3 OR budget_status = 'Over'
ORDER BY
    CASE budget_status WHEN 'Over' THEN 0 ELSE 1 END,
    empty_slots DESC,
    name;
