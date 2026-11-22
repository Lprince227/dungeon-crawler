# Handoff: end of round 6

Written for a fresh session starting round 7. Standing rules for every session are in
`CLAUDE.md`. Read it first, then `problem.md`, `spec.md`, `docs/decisions/` (0001-0011)
and this file. The older handoffs (`handoff-round-1.md` to `handoff-round-5.md`) are
history. Where they differ from this file, this file wins.

## Current state

- R1-R12 from `problem.md` are implemented. R12 changed R2 (combat is no longer fully
  predictable), R5.4 (drinking at full HP) and R11.6 (level 3 hit counts).
  **270 tests pass** with `py -m pytest` (Python 3.12.10, pytest 9.2.0 in `.venv`). Tests
  per file: R1 18, R2 6, R3 9, R4 93, R5 14, R6 13, R7 16, R8 9, R9 11, R10 20, R11 29,
  R12 32. Each parametrized case counts as one test.
- Round 6 is 5 commits after the user's requirements commit `0bc8267`, from `b2d2b45`
  (spec) to `70f409b` (ADRs 0010 and 0011). See them with `git log --oneline 0bc8267..HEAD`.
- Round 6 order: user questions answered → spec → failing tests (R12, R4 v6, rewritten
  R5.4, R11.6 hits table) → implementation and save v6 → status line, help and README →
  ADRs 0010 and 0011.
- **Uncommitted on purpose:** this file and one new `CLAUDE.md` rule (see decision 13).
  The user reviews them first.
- A short session was piped into `py -m dungeon` (`d d s help quit`) and ran without
  error. The level 3 messages were printed from a script and read correctly. A full
  3-level game was **not** played by hand in a real terminal.

### What round 6 added

| Area | What changed |
|------|--------------|
| `dungeon/game.py` | New constants `PARALYSIS_LEVEL = 3`, `PARALYSIS_TURNS = 3`, `PARALYSIS_CHANCE = 0.75`, and `enemy_paralyses(level)` (true from level 3). `Enemy` gains `paralyses: bool = False`, set by `from_map(lines, level)`. `Game` gains `paralysis: int = 0` and `rng: random.Random` (`compare=False, repr=False`, not saved). `move` ticks poison, then `_paralysis_tick()`, then `_step(direction, target, paralysed)`. On a paralysed turn, an attack fails if `rng.random() < 0.75`: "You are paralysed and can't attack!", with no damage and no hit-back. `_attack` sets `paralysis = 3` on a hit-back by a paralysing enemy. `drink` cures both statuses and is allowed at full HP while paralysed. `_next_level` adds "Their hits also paralyse you." on levels ≥ 3. `SAVE_VERSION = 6`: `player.paralysis` (integer 0-3) and each enemy's `paralyses` (strict bool, new `_bool` helper). New `_upgrade_v5`. |
| `dungeon/cli.py` | The status line ends with `   Paralysed: n turn(s)` after the poison count. The help text explains paralysis and that a potion cures both. |
| `tests/` | New `test_r12_paralysis.py`, with `FixedRoll`/`NoRoll` stub generators and its own copy of `_default_game_on_level`. `test_r4_save_load.py`: exact v6 layout, 12 new invalid v6 cases, a valid v6 base save, v5 upgrade tests (levels 1-4), a v5 → level 3 test, a 4 → 5 → 6 chain test, paralysis in the level 3 round trip, and every "version 5" assertion is now 6. `test_r5_drink_at_full_hp_keeps_potion` was rewritten on the default game and now includes the paralysed case. `test_r11_hits_needed_by_attack` clears `paralysis` between hits. Docstrings say "changed in round 6". |
| `spec.md` | Round 6: R2 intro and R2.3, Turns, status line, R4.1/R4.3/R4.5, v6 layout, R5.2/R5.4, R11.4/R11.5/R11.6, new R12.1-R12.7, out-of-scope list. |
| `docs/decisions/` | 0010 (paralysis rules, mostly the user's), 0011 (random generator held by `Game`, not saved). |
| `README.md` | Paralysis, round 5 saves, R1-R12. |

## How to run

```
py -m dungeon            # new game, level 1 of 3
py -m dungeon --load     # continue from savegame.json in the current directory
```

In the game: `w a s d` move, `p` or `drink` drinks a potion (heals 10, cures poison and
paralysis), then `save`, `load`, `help`, `quit`.
Map: `@` you, `E` enemy, `X` exit, `#` wall, `.` floor, `!` potion, `-` dagger, `/` sword, `T` axe.
Enemies: level 1 12 HP / hit 3, level 2 16 / 3, level 3 20 / 4. All poison for 3 turns;
level 3 enemies also paralyse for 3 turns (each attack fails 75% of the time).

## How to run the tests

```
.\.venv\Scripts\Activate.ps1              # PowerShell (Git Bash: source .venv/Scripts/activate)
py -m pytest
```

If `.venv` is missing: `py -m venv .venv`, activate it, then `py -m pip install -r requirements-dev.txt`.
Without activating: `.venv/Scripts/python -m pytest`.

## Decisions made in round 6, and why

Decisions 1-4 are the user's answers to the round 6 questions (ADR 0010). The rest are
mine. The user saw the list of my decisions in chat at the end of the round but has not
formally approved it.

1. **A failed attack (user).** In the context of a paralysed player bumping an enemy,
   facing what a failed 75% roll costs, we decided for using the turn (poison and
   paralysis tick) with no damage and no hit-back, and neglected a hit-back anyway and
   treating it as a non-turn, to achieve paralysis that slows fights without trapping the
   player (enemies still act only when hit, R2.3), accepting that a failed attack is
   free apart from the turn.
2. **What counts as a turn (user).** In the context of "for 3 turns", facing which
   actions count down, we decided for every turn, as with poison (moves, attacks, drinks;
   not wall bumps or refused drinks), and neglected counting only attack attempts, to
   achieve the same turn rule as R10, accepting that a player can walk away for 3 turns
   to wait it out.
3. **When it's inflicted (user).** In the context of level 3 hit-backs, facing how often
   they paralyse, we decided for every hit-back, as well as poison, with a new hit
   resetting it to 3 rather than stacking, and neglected a chance per hit-back and
   paralysis instead of poison, to achieve a single random roll in the game and an
   unchanged R10.1, accepting that level 3 hit-backs always carry both statuses.
4. **The cure (user).** In the context of the potion, facing how it cures paralysis, we
   decided for one drink curing both statuses, and allowed at full HP while paralysed,
   and neglected refusing the drink at full HP, to achieve the same rule as poison
   (R5.4 as changed in round 4), accepting that R5.4 changed again.
5. **Paralysis stored on each enemy (ADR 0010).** In the context of knowing whether a
   hit-back paralyses, facing per-enemy storage versus checking `Game.level` at hit time,
   we decided for an `Enemy.paralyses` flag set from the level number when the level
   loads, and neglected deriving it at hit time, to achieve the same pattern as
   `attack` (ADR 0009) and room for future enemy types, accepting a new per-enemy save
   field.
6. **Random generator held by `Game` (ADR 0011).** In the context of making the roll
   testable, facing global randomness versus an injected source, we decided for
   `Game.rng` (a `random.Random`, left out of equality and repr, not saved), and
   neglected the module-level `random`, saving the generator state or a seed, and a fixed
   fail pattern, to achieve exact control of the roll in tests and plain saves, accepting
   that save, attack, reload can give a new roll (save-scumming).
7. **Roll boundary.** In the context of "75% chance", facing the comparison to use, we
   decided for failing when `rng.random() < 0.75`, and neglected `<=` and integer rolls,
   to achieve exactly 75% with `random()` in [0, 1), accepting that tests must use 0.75
   as the first landing value.
8. **Tick order.** In the context of a turn with both statuses, facing which goes first,
   we decided for poison, then paralysis, then the action, and neglected the reverse, to
   achieve "poison that kills stops the action" (R10.4) with no roll on a lost game,
   accepting that paralysis doesn't tick on the turn poison kills (that doesn't matter,
   because the game is over).
9. **Save v6 validation.** In the context of `from_dict`, facing how strict to be, we
   decided for `paralysis` an integer from 0 to 3 and `paralyses` exactly `true`/`false`
   (0, 1, `"true"` and `null` are rejected), and neglected accepting truthy values, to
   achieve the same strictness as the other fields, accepting that a hand-edited save
   may still give a level 1 enemy `paralyses: true` (there is no cross-check with the
   level).
10. **Round 5 save upgrade.** In the context of `_upgrade_v5`, facing what an old save's
    enemies should do, we decided for the player unparalysed and enemies on a saved level
    3 or later paralysing, and neglected no paralysis until the next level, to achieve a
    saved level 3 that plays by the R12 rules, accepting that a round 5 save's level 3
    gets harder on load. As with `_upgrade_v4`, a bad level or enemy list is left alone
    for `from_dict` to reject.
11. **Messages and warning.** In the context of the player knowing about paralysis,
    facing how to show it, we decided for messages on the hit-back, the failed attack,
    wearing off and the cure, a `Paralysed: n turns` status field after poison, and
    "Their hits also paralyse you." on reaching level 3, and neglected the status line
    only, to achieve a rule the player can see, accepting a longer status line while both
    statuses are active.
12. **British spelling.** In the context of new words, facing "paralyse" versus
    "paralyze", we decided for "paralyse/paralysed", and neglected American spelling, to
    achieve consistency with "behaviour" and "colour" already in the repo, accepting
    that `problem.md`'s readers may expect "paralyze". Tests check `"paraly"` so they
    pass with either spelling.
13. **New `CLAUDE.md` rule (uncommitted).** In the context of standing rules, facing
    future random rules and tests that fight on level 3 becoming flaky, we decided for a
    rule that chance goes through `Game.rng` and tests fix the roll, and neglected
    leaving it only in this handoff, to achieve every session seeing it, accepting one
    more rule to read. **Check that it is wanted.**
14. **Balance reasoned, not searched.** In the context of level 3 still being winnable,
    facing re-running the slow round 5 search with randomness, we decided for a hand
    argument: waiting out paralysis for 3 steps costs the same 3 poison HP as before, so
    an Atk 15 player loses 7 HP per level 3 enemy either way. We neglected a new search
    or simulation, to achieve a round without a long script outside the repo, accepting
    that the claim isn't proved (it is written in ADR 0010).

## Unresolved / open questions

- **Winnability isn't re-checked** under R12 (see decision 14). The round 5 search script
  was in that session's scratchpad and is gone. Lines without weapons, where level 3
  kills take 3-4 hits, cost more HP per enemy when the player waits out paralysis.
- **Save-scumming:** reloading resets the generator, so a failed attack can be retried by
  `save`/`load`. Not discussed with the user.
- **The game is still easy with every weapon** (round 5 finding). Ask before changing
  numbers or maps.
- **Cross-field save checks still missing:** `playing` on `X`, `lost` with HP > 0, `won`
  off `X` or with levels left, two enemies on one tile, `poison`/`paralysis` > 0 in a
  `won` save, and enemy stats or `paralyses` that don't match the level.
- **Round 4 saves' current level keeps 12 HP enemies** (user's choice), and round 3 saves'
  current level keeps 8 HP enemies.
- **Enemy HP isn't visible** except in the attack message.
- **Level 2's exit is only reachable through an enemy** (row 8, col 9). Still not discussed.
- **"Enemies left" counts only the current level.** Still not chosen by the user.
- **Round 1 UX questions still open:** no `load` after the game ends, `save` overwrites
  silently, `quit` doesn't offer to save, `savegame.json` is in the current directory.
- **Game length vs `problem.md`** (a short break): waiting out paralysis makes level 3
  longer.
- **No full hand playtest in a real terminal.**

## Warnings for the next session

- **Bare `pytest` fails** to import `dungeon`. Use `py -m pytest` inside `.venv`. Don't add
  `conftest.py`/`pythonpath` without asking.
- **Tests that attack on level 3 are random unless fixed.** Set `game.rng` to a stub
  (`FixedRoll`/`NoRoll` in `tests/test_r12_paralysis.py`) or reset `game.paralysis = 0`
  between hits, as `test_r11_hits_needed_by_attack` does. `NoRoll` raises if a roll is
  made, which is useful for proving that moves and drinks never roll.
- **`Game.rng` is excluded from `==`.** Round-trip tests (`loaded == game`) rely on that.
  Don't make it a compared field, and don't write it to the save.
- **`Game.from_map(LEVELS[i])` is always level 1 strength**, so it has no paralysis. To test
  level 3, reach it through `Game.from_levels(LEVELS)` (see `_default_game_on_level` in
  the R11 and R12 tests), or use a custom `from_levels([["@X"], ["@X"], <map>])`.
- **Level-changing tests:** the exit is at (9, 9) on levels 1 and 2, and (9, 11) on
  level 3. Level 2's (9, 8) is a wall, so approach its exit from (8, 9). Clear
  `game.enemies` first.
- **A v7 save format** needs `_upgrade_v6` (6 → 7), added after the five existing steps in
  `from_dict`. Update `test_r4_save_writes_json_with_full_state` (exact v6 JSON) and every
  assertion of `["version"] == 6` (8 in `test_r4_save_load.py`).
- **The upgrade steps use the current tables.** `_upgrade_v4` takes attack from
  `ENEMY_LEVEL_STATS` and `_upgrade_v5` takes paralysis from `PARALYSIS_LEVEL`. If either
  changes, old saves get the new values. Decide whether that's wanted first.
- **Changing `ENEMY_LEVEL_STATS` or the paralysis constants** breaks R7.5, R9.1, R11,
  R12 and the R4 next-level tests (20/4, `paralyses` true on level 3).
- **Validation in `from_dict`:** anything after the `try` block must only raise `SaveError`.
  Convert raw values with `_int`/`_bool`/`_str`/`_str_list`/`_map_list` inside the `try`.
- **Every new command or action must be placed in "Turns" in `spec.md`.** `move` ticks
  poison, then paralysis, after the wall check. `drink` ticks neither. `_poison_tick()`
  returns a message ending in a space (except when the player died). `_paralysis_tick()`
  returns `(paralysed, message)`, where the message starts with a space and is appended
  after the action's message.
- **`LEVELS[0] is DEFAULT_MAP`** (same list). Never mutate `LEVELS` or `DEFAULT_MAP` in
  tests. `game.tiles` is a fresh list and may be changed.
- **Adding a map symbol** touches `ITEM_CHARS` (or `from_map`), `render`, the help text, and
  the legends in `spec.md` and the README. It must not be `w a s d p` in either case.
- **Shell quirks:** in Git Bash, a heredoc containing `'''` fails to parse (it happened
  again this round). Write such scripts to the scratchpad with the Write tool. Git prints
  LF→CRLF warnings on every add (harmless). Python on this machine prints in cp1252
  unless `PYTHONUTF8=1` is set. Open edited files with `encoding="utf-8"`.
