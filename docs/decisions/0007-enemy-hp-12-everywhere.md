# 0007: Enemies get 12 HP on every level; old saves keep their enemy HP (R9)

- Status: accepted. The user chose 12 HP on every level when asked in round 4.
  How round 3 saves are upgraded (keeping their saved enemy HP) is my choice.
- Date: 2026-11-21
- Requirements: R9 (more enemy HP), which changes R2 (enemy stats) and R7.5
  (same stats on every level); R4.5 (old saves keep loading)

## Background

Until round 3 every enemy had 8 HP. With the sword (Atk 8) or the axe (Atk 10)
from level 1, every enemy on all three levels died in one hit and never hit
back. The round 3 handoff listed this as the main open balance problem. R9 asks
for harder enemies through more HP but does not say how much, or whether it
should rise per level.

## Decision (Y-statement)

In the context of **R9 making enemies harder with more HP, in a game of three
fixed levels whose round 3 saves must keep loading**,
facing **how much HP to add, whether it should grow per level, and what to do
with enemies already stored in a round 3 save**,
we decided for **12 HP for every enemy on every level (damage stays 3), and
upgrading round 3 saves by keeping each saved enemy's HP as it is, while the
levels still to come get 12 HP enemies because they are stored as text maps**
and neglected **HP rising per level (12/16/20), 16 HP everywhere, and raising
enemy HP in old saves (e.g. +4 each, or scaling by 12/8)**,
to achieve **a game where a single weapon no longer one-hits, while R7.5 ("same
stats on every level") and `Enemy` stay unchanged, so the save format needs no
enemy field and an old save loads exactly as it was saved**,
accepting **that the full weapon set (Atk 13+) still one-hits everything, that
on a round 3 save's current level the unhurt enemies still have 8 HP until the
player reaches the next level, and that R2, R6 and R7.5 tests had to be
rewritten for the new numbers**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| 12 / 16 / 20 HP by level | Changes R7.5 and needs per-level enemy stats. Level 3 has 11 enemies and 1 potion; together with poison (R10) it risked being unwinnable. |
| 16 HP everywhere | Even Atk 14 would need two hits, so every fight costs a hit-back and poison. Likely too hard for a short game. |
| Raise enemy HP in round 3 saves | Changes a game the player saved, mid-fight. A hurt enemy has no clear "new" HP (+4? x1.5?). |
| 12 HP everywhere, old saves kept as saved (chosen) | One constant changes. No save-format change for enemies. |

## Consequences

- `ENEMY_START_HP = 12`. `Enemy` and the enemy part of the save format are unchanged.
- `_upgrade_v3` only adds the player's poison (ADR 0008). It does not touch enemies.
- A search over every move in the default game (done outside the repo, not a
  test) found it still winnable: the best line collects all three level 1
  weapons and finishes level 3 at 20/20 HP. So the game is still easy for a
  player who finds every weapon. More tuning would need the user's say.
