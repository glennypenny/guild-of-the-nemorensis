-- Q8: What is sitting in the vault, and where is the gold tied up?
-- Groups unassigned equipment by slot, totals the value, and uses a window
-- function to rank each slot by value. pct_of_vault_value shows how much of
-- the vault's total gold is in that slot.

WITH vault AS (
    SELECT slot, cost_gold
    FROM equipment
    WHERE character_id IS NULL
),
summary AS (
    SELECT
        slot,
        COUNT(*) AS items,
        SUM(cost_gold) AS total_value,
        ROUND(AVG(cost_gold), 1) AS avg_cost
    FROM vault
    GROUP BY slot
)
SELECT
    slot,
    items,
    total_value,
    avg_cost,
    ROUND(100.0 * total_value / (SELECT SUM(cost_gold) FROM vault), 1) AS pct_of_vault_value,
    RANK() OVER (ORDER BY total_value DESC) AS value_rank
FROM summary
ORDER BY total_value DESC, slot;
