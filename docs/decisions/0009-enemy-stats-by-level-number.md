# 0009: Enemy stats come from the level number and are stored on each enemy (R11)

- Status: accepted. The user chose the numbers (12 HP / 3 Atk on level 1,
  16 / 3 on level 2, 20 / 4 on level 3), the same poison on every level,
  and keeping the saved HP of enemies in round 4 saves. Where the stats come
  from (the level number), storing attack on each enemy, and save version 5
  are my choices.
- Date: 2026-11-22
- Requirements: R11 (difficulty rises by level), which changes R2 (enemy
  stats), R7.5 and R9.1 (same stats on every level); R4 (save and load)

## Background

Until round 5, every enemy had 12 HP and 3 attack (ADR 0007), so `Enemy` held
only a position and HP, and the hit-back used the constant `ENEMY_ATTACK`. R11
asks for stronger enemies on each level. The stats need a source (the level's
number, or something attached to each map). The saved game also needs a way to
know an enemy's attack. Round 4 saves have no enemy attack, and they have to
keep loading.

## Decision (Y-statement)

In the context of **R11 making enemies stronger on each level of a game built
from plain text maps, whose saves must keep loading**,
facing **where an enemy's HP and attack come from, and how a save knows an
enemy's attack**,
we decided for **a table of (HP, attack) by level number (`ENEMY_LEVEL_STATS`,
levels past 3 use the last row), applied when a level's map is loaded, with
each `Enemy` keeping its own `attack`, saved per enemy in save version 5; a
round 4 save is upgraded by giving its enemies the attack for the saved level
number and keeping their saved HP**
and neglected **deriving attack at hit time from `Game.level` (no save
change), writing stats into each map (a header line or a stats list next to
`LEVELS`), and different enemy symbols per strength**,
to achieve **one place to tune the curve, maps and the map legend unchanged,
an `Enemy` that says how hard it hits, and a save that records exactly what
the player faced**,
accepting **a save format bump with a new upgrade step and new validation,
that a custom game's second map is always level 2 strength (even if that map
is built in as "level 3"), and that unhurt enemies on a round 4 save's level 2
or 3 keep 12 HP until the player reaches the next level**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Derive attack from `Game.level` at hit time | No save change, but `Enemy` would no longer describe itself, and a later enemy type with its own attack would need the field anyway. |
| Stats written into each map | Changes the map format and legend (R8, R7.6 tests, `next_levels` in saves) for three numbers. |
| A different symbol per enemy strength | New map symbols across help, README and spec; R11 asks for stronger levels, not kinds of enemy. |
| Table by level number, attack stored per enemy, save v5 (chosen) | One table to tune; maps, `from_levels` and `next_levels` stay as they are. |

## Consequences

- `ENEMY_LEVEL_STATS = [(12, 3), (16, 3), (20, 4)]`, `enemy_stats(level)`.
  `ENEMY_START_HP` and `ENEMY_ATTACK` remain as the level 1 values.
- `Game.from_map(lines, level=1)` gives enemies that level's stats.
  `_next_level` builds the next map with the new level number and says how strong
  its enemies are.
- `SAVE_VERSION = 5`. Each enemy is saved as `{"row", "col", "hp", "attack"}`.
  `attack` must be an integer of 1 or more. `_upgrade_v4` (4 → 5) adds it.
- A search over every line of play (outside the repo, not a test) found the
  default game still winnable. The best line takes all weapons (Atk 15) and
  finishes level 3 at 20/20 HP with 2 potions, so the curve still leaves full
  weapon play comfortable.
