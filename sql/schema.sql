-- Guild of the Nemorensis — Gear Audit
-- This schema creates the characters and equipment tables for the guild's
-- gear audit. The build script runs it on a fresh database.
--
-- SQLite note: foreign keys are enforced per connection, not stored in the file.
-- Run this on every connection before relying on the foreign keys:
--   PRAGMA foreign_keys = ON;

CREATE TABLE characters (
    character_id INTEGER PRIMARY KEY,
    -- Surrogate key. SQLite fills this in when the insert omits it.

    name TEXT NOT NULL COLLATE NOCASE UNIQUE
         CHECK (name = TRIM(name) AND length(name) > 0),
    -- COLLATE NOCASE makes 'Aria' and 'aria' the same name.
    -- The CHECK rejects '', '   ', and ' Aria '.

    role TEXT NOT NULL
         CHECK (role IN ('Tank', 'Healer', 'Damage', 'Support')),

    level INTEGER NOT NULL CHECK (level BETWEEN 1 AND 60),

    budget_gold INTEGER NOT NULL CHECK (budget_gold >= 0)
) STRICT;
-- STRICT makes SQLite enforce the declared types instead of storing anything.

CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY,

    name TEXT NOT NULL COLLATE NOCASE UNIQUE
         CHECK (name = TRIM(name) AND length(name) > 0),

    slot TEXT NOT NULL
         CHECK (slot IN ('Weapon', 'Off-hand', 'Head', 'Chest', 'Legs', 'Feet', 'Accessory')),

    rarity TEXT NOT NULL
         CHECK (rarity IN ('Common', 'Uncommon', 'Rare', 'Epic', 'Legendary')),

    cost_gold INTEGER NOT NULL CHECK (cost_gold > 0),

    attack_bonus  INTEGER NOT NULL DEFAULT 0 CHECK (attack_bonus  >= 0),
    defense_bonus INTEGER NOT NULL DEFAULT 0 CHECK (defense_bonus >= 0),
    healing_bonus INTEGER NOT NULL DEFAULT 0 CHECK (healing_bonus >= 0),
    speed_bonus   INTEGER NOT NULL DEFAULT 0 CHECK (speed_bonus   >= 0),

    character_id INTEGER
        REFERENCES characters(character_id)
        ON DELETE SET NULL,
    -- NULL means the item is in the vault.
    -- Deleting a character returns their gear to the vault.

    CHECK (attack_bonus + defense_bonus + healing_bonus + speed_bonus > 0)
    -- An item with no effect is not useful.
) STRICT;

-- One equipped item per character per slot.
-- The WHERE clause exempts vault items (character_id IS NULL), so the vault
-- may hold many items in the same slot.
CREATE UNIQUE INDEX ux_equipment_one_per_slot
ON equipment(character_id, slot)
WHERE character_id IS NOT NULL;
