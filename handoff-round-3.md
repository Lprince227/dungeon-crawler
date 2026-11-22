# Handoff: end of round 3

Written for a fresh session starting round 4. Standing rules for every session
are in `CLAUDE.md`. Read that first, then `problem.md`, `spec.md`,
`docs/decisions/` (0001-0006) and this file. The older handoffs
(`handoff-round-1.md`, `handoff-round-2.md`) are history. This file replaces them
where they differ.

## Current state

- R1-R8 from `problem.md` are implemented, including the round 3 change to R3.
  **133 tests pass** with `py -m pytest` (Python 3.12.10, pytest 9.2.0 in `.venv`).
  Per file: R1 18, R2 6, R3 9, R4 48, R5 14, R6 13, R7 16, R8 9. Parametrized cases
  count separately.
- Round 3 is 9 commits after the user's requirements commit `b3ad86f`, from
  `7adc72d` (spec) to `e02869c` (ADR 0006). Run `git log --oneline b3ad86f..HEAD`.
  The working tree was clean after the last commit.
- Round 3 order: spec → failing tests → R8 → R7/R3 → save v3 → README → ADRs 0004/0005 →
  (user follow-up) old R3 tests rewritten → ADR 0006.
- **Uncommitted on purpose:** this file and two `CLAUDE.md` edits (see decision 14). The user
  reviews them first.
- A scripted session was played through `run()`: a weapon pickup, a level change, then
  save and load on level 2. A full 3-level game was **not** played by hand in a real terminal.

### What round 3 added

| Area | What changed |
|------|--------------|
| `dungeon/game.py` | `LEVELS` (3 maps, `LEVELS[0] is DEFAULT_MAP`). `Game` gains `level: int = 1` and `next_levels: list[list[str]]` (full text maps still to come), a `total_levels` property, `Game.from_levels()` and `_next_level()`. `move()` onto `X` loads the next level if any are left, otherwise sets `won`. `ITEM_CHARS` is now `! - / T`. `SAVE_VERSION = 3`, new `_upgrade_v2` and `_map_list`, and `_upgrade_v1` now outputs version 2 (a chain). |
| `dungeon/cli.py` | `main()` starts `Game.from_levels(LEVELS)`. The status line starts with `Level: n/3`. The help text explains levels and the new symbols. |
| `tests/` | New `test_r7_levels.py` and `test_r8_symbols.py`. `test_r3_win_loss.py`: the two old "exit wins" tests rewritten to play `LEVELS`, plus 3 small-map level tests and a `_step_onto_exit` helper. `test_r4_save_load.py`: v3 exact layout, v2 upgrade tests, a round trip on level 2, 15 new malformed cases, and a valid v3 base save. `test_r6` maps use the new symbols. |
| `spec.md` | Round 3: R3.1 rewritten, R4.1/R4.3/R4.5 for v3, new R7.1-R7.6 and R8.1-R8.3, all three level maps, out-of-scope list. |
| `docs/decisions/` | 0004 (save upcoming levels as maps), 0005 (v2 saves become level 1, the user's choice), 0006 (the R3 change). |
| `README.md` | Levels, new symbols, old saves. |

## How to run

```
py -m dungeon            # new game, level 1 of 3
py -m dungeon --load     # continue from savegame.json in the current directory
```

In the game: `w a s d` move, `p` or `drink` drinks a potion, then `save`, `load`, `help`, `quit`.
Map: `@` you, `E` enemy, `X` exit, `#` wall, `.` floor, `!` potion, `-` dagger, `/` sword, `T` axe.

## How to run the tests

```
.\.venv\Scripts\Activate.ps1              # PowerShell (Git Bash: source .venv/Scripts/activate)
py -m pytest
```

If `.venv` is missing: `py -m venv .venv`, activate it, then `py -m pip install -r requirements-dev.txt`.
Without activating: `.venv/Scripts/python -m pytest`.

## Decisions made in round 3, and why

The user chose 1-4 when asked, and asked for the R3 test rewrite and ADR 0006 (decision 5). The
rest are my choices. The user has seen the list in chat but has not formally approved it.

1. **Level count (user).** In the context of R7 "at least 3 levels", facing how long a game should
   be, we decided for exactly 3 levels with the old default map as level 1, and neglected 4 or 5
   levels, to achieve a game that still fits a short break, accepting that a full game is now about
   three times as long as in round 2.
2. **Weapon symbols (user).** In the context of R8, facing weapon letters `d`/`s`/`a` that matched
   movement keys, we decided for `-` dagger, `/` sword, `T` axe, and neglected the bonus digits
   `1 3 5` and other letters (`k b h`), to achieve symbols that look a bit like the weapon and
   are not command keys, accepting that round 2 maps written with `d s a` no longer parse.
   Saves were not affected, since they store item kinds by name.
3. **Difficulty (user).** In the context of later levels, facing how to make them harder, we
   decided for the same enemy stats everywhere (8 HP, 3 damage) with more enemies and fewer potions,
   and neglected stronger enemies per level, to achieve no new enemy state and no save change for
   enemies, accepting that the balance problem from round 2 remains (sword/axe one-hit everything).
4. **Round 2 saves (user, ADR 0005).** In the context of save v2 → v3, facing old saves with one map
   and no level number, we decided for making the saved map level 1, followed by built-in levels
   2 and 3, and neglected treating it as the last level and rejecting v2 saves, to achieve old games
   that follow the new win rule, accepting that a custom (non-default) v2 map is still followed by
   the built-in levels.
5. **R3 change and its tests (user asked, ADR 0006).** In the context of R3 once R7 adds levels,
   facing an "any exit wins" rule that would end the game on level 1, we decided for only the last
   level's exit winning, with earlier exits loading the next level, and rewrote the old R3 tests to
   play the default 3-level game, and neglected a separate stairs tile, a clear-all-enemies or score
   win, and a per-level `won` status, to achieve one rule for any number of levels with the exit
   meaning "leave this level", accepting longer games and HP loss that carries forward. The old
   tests had kept passing because `Game.from_map` is a one-level game, so they never exercised the
   change.
6. **Self-contained saves (ADR 0004).** In the context of saving mid-game, facing resuming on the
   right level, we decided for storing `level` plus `next_levels` as full text maps, and neglected a
   level index into `LEVELS` and an index plus a level-set name, to achieve saves that hold
   everything needed to finish and work for custom level lists in tests, accepting bigger saves and
   that a save keeps its old maps if `LEVELS` is edited later.
7. **Won v2 saves stay won.** In the context of upgrading v2 saves, facing a save that was already
   won, we decided for keeping it won with no further levels, and neglected reopening it at level 1,
   to achieve no change to games finished under the old rules, accepting a small exception to the
   user's "level 1, then go on" choice. A `lost` v2 save does get levels 2 and 3, which has no
   effect because it can't be played.
8. **v1 saves go through v2.** In the context of the upgrade path, facing a round 1 save, we decided
   for a chain (v1 → v2 → v3), so v1 saves also become level 1 of 3, and neglected a direct v1 → v3
   step, to achieve one upgrade step per version, accepting that a v1 save passes through two steps.
9. **Level maps.** In the context of R7, facing designing levels 2 and 3, we decided for level 2
   with 8 enemies, 2 potions and a dagger, and level 3 with 11 enemies, 1 potion and no weapons, and
   neglected adding more weapons, to achieve visibly harder levels, accepting that the balance was
   not tuned. Tests check each map is valid, its exit is reachable, enemies go up and potions don't.
10. **API shape.** In the context of `Game`, facing how to represent levels, we decided for
    `Game.from_levels()` with `Game.from_map()` kept as a one-level game, and neglected making every
    game multi-level by default, to achieve unchanged R1/R2/R5/R6 tests, accepting two constructors.
11. **Check every level up front.** In the context of building a game or loading a save, facing a
    broken map further ahead, we decided for validating all maps at once (`ValueError` /
    `SaveError`), and neglected checking each one when it is reached, to achieve errors at load
    time, not mid-game, accepting a little more work at start-up.
12. **Messages and status line.** In the context of the CLI, facing showing levels, we decided for
    `Level: n/3` at the start of the status line, "You reach the exit and go down to level 2 of 3."
    and "You reach the exit of the last level. You win!", and neglected a separate level-change
    screen, to achieve the level always being visible, accepting an even longer status line.
13. **R8 also covers `p`.** In the context of R8, facing which keys count as clashes, we decided for
    no map symbol equal to `w a s d p` in either case, and neglected checking only `w a s d`, to
    achieve no clash with any one-letter command, accepting that `test_r8_no_map_symbol_is_a_command_key`
    fails if a new one-letter command is added (on purpose: re-check symbols then).
14. **Two `CLAUDE.md` rules (uncommitted).** In the context of standing rules, facing lessons from
    this round, we decided for adding: (a) when a requirement changes, rewrite its old tests on the
    default game, mark them "changed in round N" and record an ADR, which generalises the user's R3
    request; (b) upgrade steps go up one version each, and `Item` is now named in the save-state rule.
    We neglected leaving them only in this handoff, to achieve rules that every session sees,
    accepting that (a) generalises a one-off request. **Check that they are wanted.**

## Unresolved / open questions

- **Balance is still easy, and games are longer.** The sword or the axe on level 1 makes every
  enemy on all 3 levels a one-hit kill. Without them, level 3 (11 enemies, 1 potion) is hard.
  Nobody has played a full run by hand. Ask the user before changing numbers or maps, since
  tests and `spec.md` use them.
- **Level 2's exit is only reachable through an enemy tile** (the `E` at row 8, col 9). It's
  intentional (a forced fight), but it was not discussed with the user.
- **Cross-field checks still missing in `from_dict`:** `playing` while standing on `X`, `lost` with
  HP > 0, `won` while not on `X` or with `next_levels` left, and two enemies on one tile all still
  load. A `playing` save standing on `X` with levels left never advances until the player steps off and back on.
- **"Enemies left" counts only the current level.** It's in `spec.md`, but the user didn't choose it.
- **The round 1 UX questions are still open:** you can't `load` after the game ends (`run`
  returns), `save` overwrites silently, `quit` doesn't offer to save, and `savegame.json` is in
  the current directory.
- **Game length vs `problem.md`.** The goal is a game for a short break, and 3 levels make it longer.
- **No full hand playtest in a real terminal.**

## Warnings for the next session

- **Bare `pytest` fails** to import `dungeon`. Use `py -m pytest` inside `.venv`. Don't add
  `conftest.py`/`pythonpath` without asking.
- **Passing old tests don't prove a changed rule.** In round 3 the old R3 tests passed untouched,
  because `Game.from_map` builds a one-level game where the exit still wins. Test changed rules on
  `Game.from_levels(LEVELS)` (the new `CLAUDE.md` rule (a)).
- **`LEVELS[0] is DEFAULT_MAP`** (same list object). `from_levels` copies the later maps, but never
  mutate `LEVELS` or `DEFAULT_MAP` in tests, or other tests will see it.
- **A v4 save format** needs `_upgrade_v3` (3 → 4), added after the existing two steps in
  `from_dict`. Don't change `_upgrade_v1`/`_upgrade_v2` to jump to the current version. Also
  update the exact-shape test `test_r4_save_writes_json_with_full_state`, which asserts the whole v3 JSON.
- **Validation in `from_dict`:** anything after the `try` block must only raise `SaveError`. The
  `next_levels` maps go through `Game.from_map` *inside* the `try`, and its `ValueError` becomes
  `SaveError`. Convert raw values with `_int`/`_str`/`_str_list`/`_map_list` inside the `try`.
- **Tests that pin the level maps:** `test_r7_there_are_three_built_in_levels` (exactly 3, level 1
  is `DEFAULT_MAP`), `test_r7_later_levels_are_harder` (strictly more enemies, never more potions),
  `test_r6_default_map_has_items` (level 1's item mix), the R8 tests (no `w a s d p` in any level),
  and the v2 upgrade tests (which expect `LEVELS[1:]`). Changing a map means updating `spec.md` too.
- **`_step_onto_exit` in `test_r3_win_loss.py`** teleports the player next to the exit and
  removes any enemy on that tile. It skips the real route, so it doesn't prove a level can be won
  in play. `test_r7_every_built_in_level_is_valid_and_finishable` only checks that the exit is reachable.
- **Adding a map symbol** touches `ITEM_CHARS` (or `from_map`), `render` (through `ITEM_SYMBOLS`),
  the help text (an R8 test checks the weapon names in it), and the legend in `spec.md` and the
  README. It must not be `w a s d p` in either case, or clash with `@ E X # .`.
- **Literal numbers in tests:** 20 HP, 5 base attack, 8/3 enemy stats, 10 heal, weapon bonuses
  1/3/5, 3 levels.
- **Shell quirks:** Git prints LF→CRLF warnings on every add (harmless). Throwaway experiments
  (e.g. running tests against an old rule) were done in a scratch copy outside the repo, so the
  repo was never left modified.
