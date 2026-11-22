-- Q7: How does each role compare?
-- One row per role: roster size, average power, best power, average gear,
-- total empty slots, and how many characters are over budget.

SELECT
    role,
    COUNT(*) AS characters,
    ROUND(AVG(role_power), 1) AS avg_role_power,
    MAX(role_power) AS best_role_power,
    ROUND(AVG(items_equipped), 1) AS avg_items,
    SUM(empty_slots) AS total_empty_slots,
    SUM(CASE WHEN budget_status = 'Over' THEN 1 ELSE 0 END) AS over_budget
FROM v_character_loadout
GROUP BY role
ORDER BY avg_role_power DESC, role;
