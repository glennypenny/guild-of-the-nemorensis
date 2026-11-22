-- Q2: Who is strongest for their role, and who is lagging?
-- RANK() numbers characters within their own role, ordered by role_power.
-- A rank of 1 is the strongest in that role; gap_to_best shows how far behind
-- the leader each character is.

WITH ranked AS (
    SELECT
        name,
        role,
        role_power,
        power_per_100g,
        RANK() OVER (PARTITION BY role ORDER BY role_power DESC) AS role_rank,
        MAX(role_power) OVER (PARTITION BY role) AS role_best
    FROM v_character_loadout
)
SELECT
    name,
    role,
    role_power,
    role_rank,
    role_best - role_power AS gap_to_best,
    power_per_100g
FROM ranked
ORDER BY role, role_rank, name;
