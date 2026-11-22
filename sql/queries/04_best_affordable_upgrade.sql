-- Q4: What is the best affordable next upgrade for each empty slot?
-- 1. Build the list of every empty slot for every character.
-- 2. Join it to vault items of the same slot that fit the remaining budget.
-- 3. Score each candidate for the character's role.
-- 4. Keep the highest-power item in each character/slot pair.
--
-- Only affordable candidates appear. An over-budget character has no
-- affordable upgrade, so their empty slots are absent from this result.

WITH slots(slot) AS (
    VALUES
        ('Weapon'),
        ('Off-hand'),
        ('Head'),
        ('Chest'),
        ('Legs'),
        ('Feet'),
        ('Accessory')
),
empty_slots AS (
    SELECT
        c.character_id,
        c.name AS character,
        c.role,
        c.budget_remaining,
        s.slot
    FROM v_character_loadout c
    CROSS JOIN slots s
    WHERE NOT EXISTS (
        SELECT 1
        FROM equipment e
        WHERE e.character_id = c.character_id
          AND e.slot = s.slot
    )
),
candidates AS (
    SELECT
        es.character_id,
        es.character,
        es.role,
        es.slot,
        es.budget_remaining,
        v.name AS item,
        v.cost_gold,
        CASE es.role
            WHEN 'Tank'    THEN v.defense_bonus * 3 + v.attack_bonus + v.speed_bonus
            WHEN 'Healer'  THEN v.healing_bonus * 3 + v.defense_bonus + v.speed_bonus
            WHEN 'Support' THEN v.healing_bonus * 2 + v.speed_bonus * 2 + v.defense_bonus
            WHEN 'Damage'  THEN v.attack_bonus * 3 + v.speed_bonus
        END AS item_power
    FROM empty_slots es
    JOIN equipment v
      ON v.character_id IS NULL
     AND v.slot = es.slot
     AND v.cost_gold <= es.budget_remaining
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY character_id, slot
            ORDER BY item_power DESC, cost_gold ASC, item
        ) AS item_rank
    FROM candidates
)
SELECT
    character,
    role,
    slot,
    item,
    cost_gold,
    item_power,
    budget_remaining
FROM ranked
WHERE item_rank = 1
ORDER BY character, slot;
