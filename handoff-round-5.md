# Handoff: end of round 5

Written for a fresh session starting round 6. Standing rules for every session are in
`CLAUDE.md`. Read it first, then `problem.md`, `spec.md`, `docs/decisions/` (0001-0009)
and this file. The older handoffs (`handoff-round-1.md` to `handoff-round-4.md`) are
history. Where they differ from this file, this file wins.

## Current state

- R1-R11 from `problem.md` are implemented. R11 changed R2 (enemy stats), R7.5 and R9.1.
  **219 tests pass** with `py -m pytest` (Python 3.12.10, pytest 9.2.0 in `.venv`). Tests
  per file: R1 18, R2 6, R3 9, R4 74, R5 14, R6 13, R7 16, R8 9, R9 11, R10 20, R11 29.
  Each parametrized case counts as one test.
- Round 5 is 5 commits after the user's requirements commit `8730f07`, from `2596ab5`
  (spec) to `33d3ca1` (ADR 0009). See them with `git log --oneline 8730f07..HEAD`. The
  working tree was clean after the last commit.
- Round 5 order: user questions answered → spec → failing tests (R11, rewritten R7.5/R9.1,
  R4 v5) → implementation and save v5 → help text and README → ADR 0009.
- **Uncommitted on purpose:** this file and one new `CLAUDE.md` rule (see decision 12). The
  user reviews them first.
- A short session was piped into `py -m dungeon` (`d d s quit`) and ran without error. A
  full 3-level game was **not** played by hand in a real terminal.

### What round 5 added

| Area | What changed |
|------|--------------|
| `dungeon/game.py` | New `ENEMY_LEVEL_STATS = [(12, 3), (16, 3), (20, 4)]` and `enemy_stats(level)`. Levels past the end of the table use its last row. `ENEMY_START_HP` and `ENEMY_ATTACK` stay, as the level 1 values (12, 3). `Enemy` gains `attack: int = ENEMY_ATTACK`. `Game.from_map(lines, level=1)` gives enemies that level's stats. `_next_level` raises `level` first, then builds the map with it. Its message ends `Enemies here have N HP and hit for M.` `_attack` uses `enemy.attack`. `SAVE_VERSION = 5`: each enemy is saved as `{"row", "col", "hp", "attack"}`, and `attack` must be an integer ≥ 1. New `_upgrade_v4`. |
| `dungeon/cli.py` | Help text gives the per-level enemy stats. The status line is unchanged. |
| `tests/` | New `test_r11_difficulty.py`. Rewritten for the changed rules on the default game: `test_r7_enemies_get_stronger_on_later_levels` (was `..._have_the_same_stats`), `test_r9_level_1_enemies_of_the_default_game_have_12_hp` and `test_r9_enemies_on_level_2_of_the_default_game_have_more_than_12_hp`, which replace the two "12 HP on every level" tests. Their docstrings say "changed in round 5". `test_r4_save_load.py`: exact v5 layout, 7 new malformed `attack` cases, a valid v5 base save, a level 3 round trip, v4 upgrade tests (levels 1-4), a v4 → next level test, and a 3 → 4 → 5 chain test. The v3 next-level test now expects 20/4 enemies, and the v2 chain test now ends at version 5. |
| `spec.md` | Round 5: R2 stats, R2.3 "that enemy's attack", R4.1/R4.3/R4.5, v5 layout, R7.5 and R9.1 changed, new R11.1-R11.6, out-of-scope list. The "Turns" section is unchanged (no new command or action). |
| `docs/decisions/` | 0009 (stats by level number, attack stored per enemy, save v5). |
| `README.md` | Per-level enemy stats, round 4 saves, R1-R11. |

## How to run

```
py -m dungeon            # new game, level 1 of 3
py -m dungeon --load     # continue from savegame.json in the current directory
```

In the game: `w a s d` move, `p` or `drink` drinks a potion (heals 10, cures poison), then
`save`, `load`, `help`, `quit`.
Map: `@` you, `E` enemy, `X` exit, `#` wall, `.` floor, `!` potion, `-` dagger, `/` sword, `T` axe.
Enemies: level 1 12 HP / hit 3, level 2 16 / 3, level 3 20 / 4. All poison for 3 turns.

## How to run the tests

```
.\.venv\Scripts\Activate.ps1              # PowerShell (Git Bash: source .venv/Scripts/activate)
py -m pytest
```

If `.venv` is missing: `py -m venv .venv`, activate it, then `py -m pip install -r requirements-dev.txt`.
Without activating: `.venv/Scripts/python -m pytest`.

## Decisions made in round 5, and why

Decisions 1-4 are the user's answers to the round 5 questions. The rest are mine. The user
saw the list of my decisions in chat at the end of the round but has not formally approved it.

1. **Enemy numbers (user).** In the context of R11, facing how steep the difficulty curve
   should be, we decided for 12 HP / 3 Atk on level 1, 16 / 3 on level 2 and 20 / 4 on
   level 3, and neglected a gentler 12/15/18 (Atk 4 on level 3) and a steeper 12/18/24
   (Atk 5 on level 3), to achieve a clear step on each level that keeps level 3 (11 enemies,
   1 potion) winnable, accepting that the full weapon set still makes the game comfortable
   (see "Unresolved").
2. **Poison unchanged (user).** In the context of R11, facing whether poison should grow
   too, we decided for 1 damage for 3 turns on every level, and neglected stronger poison on
   level 3, to achieve a change limited to what R11 names (HP and attack), accepting that
   poison does not take part in the difficulty curve.
3. **Round 4 saves keep enemy HP (user, ADR 0009).** In the context of upgrading v4 saves,
   facing unhurt 12 HP enemies stored on a saved level 2 or 3, we decided for keeping saved
   HP and giving each enemy the attack for the saved level, and neglected raising HP to the
   new level stats, to achieve a save that loads as saved (the same rule as ADR 0007),
   accepting that a round 4 save's current level stays a bit easier until the next exit.
4. **Balance check before changing maps (user).** In the context of the new numbers,
   facing a possibly unwinnable level 3, we decided for an exhaustive search outside the
   repo with any map change put to the user first, and neglected changing maps on my own
   and not checking, to achieve proof the game can still be won, accepting a 5-minute
   script that isn't a test. It found the game winnable, so no maps changed.
5. **Stats by level number (ADR 0009).** In the context of where enemy stats come from,
   facing a table keyed by level number versus stats attached to each map, we decided for
   `ENEMY_LEVEL_STATS` keyed by level number, with levels past 3 using the last row, and
   neglected a stats header in each map and a separate stats list next to `LEVELS`, to
   achieve one place to tune and unchanged maps, `from_levels` and `next_levels`, accepting
   that a map's strength depends on its position (the level 3 map played alone is level 1).
6. **Attack stored on each enemy, save v5 (ADR 0009).** In the context of the hit-back
   needing an enemy's attack, facing a save format bump, we decided for an `attack` field
   on `Enemy`, saved per enemy, and neglected deriving attack from `Game.level` at hit time
   (no save change), to achieve an `Enemy` that says how hard it hits and room for future
   enemy types, accepting a new version, upgrade step and validation.
7. **`_upgrade_v4` doesn't check the level.** In the context of upgrading a v4 save, facing
   an invalid `level` or `enemies` value, we decided for leaving the data alone so
   `from_dict` rejects it with `SaveError`, and neglected raising in the upgrade step, to
   achieve all validation in one place, accepting that the upgrade only acts on a valid
   level number (an integer of 1 or more) and an enemy list.
8. **Attack validation.** In the context of `from_dict`, facing how strict to be, we
   decided for an integer of 1 or more, and neglected an upper bound or requiring the exact
   level stat, to achieve the same strictness as enemy HP, accepting that a hand-edited save
   can hold an enemy with any attack.
9. **Arrival message (R11.5).** In the context of players not seeing enemy stats, facing
   how to show the change, we decided for adding "Enemies here have N HP and hit for M." to
   the level-change message, and neglected a status line field or showing nothing, to
   achieve a one-time hint with no wider status line, accepting that it is easy to scroll
   past. It is printed even on a level with no enemies.
10. **`from_map` takes `level`.** In the context of building a level's enemies, facing
    where to pass the level number, we decided for an optional `level=1` argument, and
    neglected changing stats after the map was built, to achieve enemies created with the
    right stats, accepting that the returned `Game.level` is still 1 (`_next_level` copies
    only the tiles, enemies, items and player position).
11. **Old tests reach later levels through the default game.** In the context of
    rewriting R7.5/R9.1 tests, facing `Game.from_map(LEVELS[i])` building every map as
    level 1 (so a 12 HP test would still pass), we decided for clearing each level and
    stepping onto its exit in `Game.from_levels(LEVELS)`, and neglected passing `level=` to
    `from_map`, to achieve tests that check what a player really meets, accepting a small
    helper (`_default_game_on_level` in the R11 tests; inline loops in R4/R7).
12. **New `CLAUDE.md` rule (uncommitted).** In the context of standing rules, facing future
    per-level tests that build a map with `from_map` and silently get level 1 stats, we
    decided for a rule that per-level behaviour is tested on the level as reached in the
    default game, and neglected leaving it only in this handoff, to achieve every session
    seeing it, accepting one more rule to read. **Check that it is wanted.**

## Unresolved / open questions

- **The game is still easy for a player who finds every weapon.** The round 5 search (a
  re-implementation of the rules that imports the real maps and constants, kept in the
  round 5 session scratchpad and not committed) found the best line takes all weapons
  (Atk 15), then ends level 1 at 20/20 HP with 2 potions, level 2 at 20/20 with 2, and
  level 3 at 20/20 with 2. It took about 50 s, 60 s and 180 s for the 3 levels. Lines
  without weapons were not studied. Ask the user before changing numbers or maps.
- **Should a winnability check be a real test?** It is too slow for the suite. Not
  discussed with the user.
- **Round 4 saves' current level keeps 12 HP enemies** (user's choice), and round 3 saves'
  current level keeps 8 HP enemies (round 4 choice, not the user's).
- **Enemy HP and attack in saves have no upper bound.** Cross-field checks are still
  missing: `playing` on `X`, `lost` with HP > 0, `won` off `X` or with levels left, two
  enemies on one tile, `poison > 0` in a `won` save, and enemy stats that don't match the
  level.
- **Enemy HP isn't visible** except in the attack message, and enemy stats show only on
  arrival and in help.
- **Level 2's exit is only reachable through an enemy** (row 8, col 9). Still not discussed.
- **"Enemies left" counts only the current level.** Still not chosen by the user.
- **Round 1 UX questions still open:** no `load` after the game ends, `save` overwrites
  silently, `quit` doesn't offer to save, `savegame.json` is in the current directory.
- **Game length vs `problem.md`** (a short break): tougher later levels make it longer.
- **No full hand playtest in a real terminal.**

## Warnings for the next session

- **Bare `pytest` fails** to import `dungeon`. Use `py -m pytest` inside `.venv`. Don't add
  `conftest.py`/`pythonpath` without asking.
- **`Game.from_map(LEVELS[i])` is always level 1 strength.** To test levels 2 and 3, reach
  them through `Game.from_levels(LEVELS)` (see `_default_game_on_level` in
  `tests/test_r11_difficulty.py`). The R8 tests and `test_r7_every_built_in_level_...` use
  `from_map` only for map shape. That's fine.
- **Level-changing tests:** the exit is at (9, 9) on levels 1 and 2, and (9, 11) on
  level 3. Level 2's (9, 8) is a wall, so approach its exit from (8, 9), which is floor
  under an enemy. Clear `game.enemies` first.
- **Changing `ENEMY_LEVEL_STATS`** breaks R7.5, R9.1, R11 (stats, hit-backs, hits table,
  arrival message) and the R4 v3/v4 next-level tests (20/4). Level 1 values are also
  pinned in R2, R4 (exact JSON: enemy HP 4 and 7, attack 3), R6, R9 and R10 tests.
- **A v6 save format** needs `_upgrade_v5` (5 → 6), added after the four existing steps in
  `from_dict`. Update `test_r4_save_writes_json_with_full_state` (exact v5 JSON) and the
  tests that assert `"version"] == 5` (4 of them) or `to_dict()["version"] == 5`.
- **`_upgrade_v4` uses the current table.** If the level stats change in a later round,
  v4 saves get the new attack for their level, not round 5's. Decide whether that's
  wanted before changing the table.
- **Validation in `from_dict`:** anything after the `try` block must only raise `SaveError`.
  Convert raw values with `_int`/`_str`/`_str_list`/`_map_list` inside the `try`.
- **Every new command or action must be placed in "Turns" in `spec.md`.** `move` ticks
  poison after the wall check, and `drink` never ticks. `_poison_tick()` returns a message
  ending in a space, except when the player died.
- **Fights cost more on later levels.** On level 3 at Atk 5, a kill takes 4 hits: 3
  hit-backs of 4 HP plus poison ticks on the 2nd-4th attacks. Tests that fight there should
  reset `player_hp`/`poison` between hits, as the R11 hits table does.
- **`LEVELS[0] is DEFAULT_MAP`** (same list). Never mutate `LEVELS` or `DEFAULT_MAP` in
  tests. `game.tiles` is a fresh list and may be changed.
- **Adding a map symbol** touches `ITEM_CHARS` (or `from_map`), `render`, the help text, and
  the legends in `spec.md` and the README. It must not be `w a s d p` in either case.
- **Shell quirks:** Git prints LF→CRLF warnings on every add (harmless). In Git Bash, a
  heredoc containing `'''` failed to parse once. Writing the script to the scratchpad with
  the Write tool worked. Python on this machine prints in cp1252 unless `PYTHONUTF8=1` is
  set, which matters when a script writes `→`. Open edited files with `encoding="utf-8"`.
