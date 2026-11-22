# 0006: Win only on the last level's exit (R3 changed)

- Status: accepted (the user chose this: it is the round 3 change to R3 in
  `problem.md`. The exact wording of the rule and the alternatives below are mine.)
- Date: 2026-11-21
- Requirements: R3 (winning and losing), R7 (multiple levels)

## Background

In rounds 1 and 2 the dungeon was one map, and R3.1 said: "When the player
moves onto the exit tile, the game ends with status `won`." Round 3 adds three
levels (R7). If the old rule had stayed, the first exit would end the game and
levels 2 and 3 could never be played. So R3 had to change too.

## Decision (Y-statement)

In the context of **R3 winning, once R7 turns the game into three levels in a
row**,
facing **the old rule that any exit wins, which would end the game on level 1
and make the other levels unreachable**,
we decided for **making the exit of the last level the only win: an earlier
level's exit loads the next level and the game keeps `playing`, and a game
built from a single map still wins on its one exit**
and neglected **keeping "any exit wins" and adding a separate "go down" tile,
winning by clearing every enemy or getting a score instead of reaching an exit,
and showing a "level won" status between levels**,
to achieve **one rule that works for any number of levels, with the
exit tile meaning the same thing on every map ("leave this level"), and a
win that needs the whole dungeon, which is the point of R7**,
accepting **that a full win now takes about three times as long, which pulls
against the "short break" goal in `problem.md`, that HP lost on level 1 counts
against the player on level 3, and that every R3 test and round 1/2 saves had
to be revisited (see ADR 0005)**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Keep "any `X` wins" and add a new stairs tile for level changes | Two tiles that both mean "leave", a new map symbol, and the exit on levels 1 and 2 would be a trap that ends the game early. |
| Win by defeating every enemy on the last level, or by score | Changes what the game is about. Enemies don't move, so the player could clear them in any order, and the exit would lose its purpose. |
| A `won` status per level plus a "continue?" prompt | Adds a status that is neither playing nor over, which the save format and the move/drink rules would all have to handle. |
| Only the last level's exit wins (chosen) | Smallest change: one `if` in `Game.move`, no new tile, no new status. |

## Consequences

- `Game.move` checks `next_levels` on reaching `X`: if levels are left it calls
  `_next_level()`, otherwise it sets `won`.
- `Game.from_map` (one level) still wins on its exit, so the R1, R2, R5 and R6
  tests that build small maps did not change.
- The R3 tests that checked "reaching the exit wins" were rewritten to play the
  default 3-level game, and their docstrings say R3 changed in round 3.
- Round 2 saves upgrade to level 1, so they also follow the new rule (ADR 0005).
