-- Q6: How many characters are over, at, or under budget?
-- This is a small management summary: one row per budget status, with the
-- average loadout power and the total gold tied up in gear.

SELECT
    budget_status,
    COUNT(*) AS characters,
    ROUND(AVG(role_power), 1) AS avg_role_power,
    SUM(gear_cost) AS total_gear_cost,
    ROUND(AVG(budget_remaining), 1) AS avg_budget_remaining
FROM v_character_loadout
GROUP BY budget_status
ORDER BY
    CASE budget_status
        WHEN 'Over' THEN 1
        WHEN 'At' THEN 2
        ELSE 3
    END;
