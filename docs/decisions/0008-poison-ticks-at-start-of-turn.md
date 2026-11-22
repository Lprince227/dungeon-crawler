# 0008: Poison ticks at the start of each move or attack, not on a drink (R10)

- Status: accepted. The user chose: every enemy poisons; 1 damage for 3 turns;
  a new hit resets the count (no stacking); a potion cures poison. When the
  damage happens within a turn, and what counts as a turn, are my choices.
- Date: 2026-11-21
- Requirements: R10 (poison), R5 (potions), R3.2 (losing), R4 (save)

## Background

Enemies in this game never act on their own: they only hit back when attacked
(R2.3, R5.5). "Damage over time" therefore needs a clock, and the only clock is
the player's own commands. A rule was needed for which commands count, and
where in a turn the 1 damage lands, because that decides whether a potion at
1 HP can still save a poisoned player, and whether the hit-back turn already
costs poison.

## Decision (Y-statement)

In the context of **R10 poison in a turn-based game where enemies only act when
attacked**,
facing **when the poison damage is dealt within a turn and which commands
count as turns**,
we decided for **dealing the damage at the start of each move or attack, before
the action (so poison that kills stops the action), counting only commands that
change the game as turns, and treating a drink as a turn on which the potion
cures the poison before it can hurt**
and neglected **dealing it at the end of every turn including the hit-back
turn, dealing it at the end of the turn while skipping the turn it was applied,
and counting every typed command (including wall bumps, refused drinks and
`help`) as a turn**,
to achieve **"3 turns" meaning the player's next 3 actions after the hit, a
hit-back that costs exactly 3 HP on its own turn, a potion that always saves a
poisoned player at 1 HP, and no damage for typing `help` or bumping a wall**,
accepting **that a drink is a special case in the rule, that poison can still
kill on the step onto an exit (the game is then lost, not won), and that saves
need a new field (version 4, `player.poison`)**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| End of every turn, including the hit-back turn | A hit-back would really cost 4 HP, and a potion drunk at 1 HP would be followed by a tick. |
| End of turn, but not the turn the poison was applied | Same damage as the chosen rule, but needs an extra "applied this turn" flag, and a re-hit while poisoned is awkward to order. |
| Every command is a turn | Typing `help` or `save` would hurt. It would also break R1.2 ("a wall bump does not change the game"). |
| Start of each move/attack, cured on a drink (chosen) | Simple order: tick, then act. The hit-back sets the count to 3 after the tick, so a re-hit resets cleanly. |

## Consequences

- `Game.poison` holds the turns left (0 to 3). `Game.move` calls `_poison_tick()`
  after the wall check and before the action; `drink` sets `poison = 0` and does
  not tick. R5.4 changed: drinking at full HP is allowed while poisoned.
- Poison carries over between levels like HP (R7.3).
- `SAVE_VERSION = 4` with `player.poison`, validated as an integer 0 to 3.
  `_upgrade_v3` loads round 3 saves with `poison` 0 (see ADR 0007 for enemy HP).
