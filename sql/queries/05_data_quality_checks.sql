-- Q5: Does the data obey the guild's rules?
-- Each row is one check. A healthy database returns zero failures for every
-- check. The schema should prevent all of these, so this query is a second
-- line of defence: it proves the constraints are doing their job.
--
-- The tests assert that SUM(failures) = 0.

SELECT 'duplicate character names' AS check_name, COUNT(*) AS failures
FROM (
    SELECT name
    FROM characters
    GROUP BY name COLLATE NOCASE
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'duplicate equipment names', COUNT(*)
FROM (
    SELECT name
    FROM equipment
    GROUP BY name COLLATE NOCASE
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'invalid character roles', COUNT(*)
FROM characters
WHERE role NOT IN ('Tank', 'Healer', 'Damage', 'Support')
UNION ALL
SELECT 'invalid equipment slots', COUNT(*)
FROM equipment
WHERE slot NOT IN ('Weapon', 'Off-hand', 'Head', 'Chest', 'Legs', 'Feet', 'Accessory')
UNION ALL
SELECT 'invalid rarities', COUNT(*)
FROM equipment
WHERE rarity NOT IN ('Common', 'Uncommon', 'Rare', 'Epic', 'Legendary')
UNION ALL
SELECT 'orphan equipment', COUNT(*)
FROM equipment e
LEFT JOIN characters c ON c.character_id = e.character_id
WHERE e.character_id IS NOT NULL
  AND c.character_id IS NULL
UNION ALL
SELECT 'negative stat bonuses', COUNT(*)
FROM equipment
WHERE attack_bonus < 0
   OR defense_bonus < 0
   OR healing_bonus < 0
   OR speed_bonus < 0
UNION ALL
SELECT 'items with no effect', COUNT(*)
FROM equipment
WHERE attack_bonus + defense_bonus + healing_bonus + speed_bonus = 0
UNION ALL
SELECT 'double-booked slots', COUNT(*)
FROM (
    SELECT character_id, slot
    FROM equipment
    WHERE character_id IS NOT NULL
    GROUP BY character_id, slot
    HAVING COUNT(*) > 1
)
UNION ALL
SELECT 'characters with more than seven items', COUNT(*)
FROM (
    SELECT character_id
    FROM equipment
    WHERE character_id IS NOT NULL
    GROUP BY character_id
    HAVING COUNT(*) > 7
)
UNION ALL
SELECT 'non-positive item costs', COUNT(*)
FROM equipment
WHERE cost_gold <= 0
ORDER BY failures DESC, check_name;
