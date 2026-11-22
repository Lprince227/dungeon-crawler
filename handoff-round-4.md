# Handoff: end of round 4

Written for a fresh session starting round 5. Standing rules for every session are in
`CLAUDE.md`. Read that first, then `problem.md`, `spec.md`, `docs/decisions/` (0001-0008)
and this file. The older handoffs (`handoff-round-1.md` to `handoff-round-3.md`) are
history. This file replaces them where they differ.

## Current state

- R1-R10 from `problem.md` are implemented, including the round 4 changes to R2, R5.4 and
  R7.5 that R9/R10 caused. **177 tests pass** with `py -m pytest` (Python 3.12.10,
  pytest 9.2.0 in `.venv`). Per file: R1 18, R2 6, R3 9, R4 59, R5 14, R6 13, R7 16, R8 9,
  R9 13, R10 20. Parametrized cases count separately.
- Round 4 is 9 commits after the user's requirements commit `69c5768`, from `5c32a68`
  (spec) to `3935d4a` (ADR 0008). Run `git log --oneline 69c5768..HEAD`. The working tree
  was clean after the last commit.
- Round 4 order: user questions answered → spec → failing tests (R9 + rewritten old tests,
  then R10 + R4 v4) → R9 → R10 + save v4 → CLI → README → ADRs 0007/0008.
- **Uncommitted on purpose:** this file and one new `CLAUDE.md` rule (see decision 15). The
  user reviews them first.
- A scripted session was played through `run()`: a dagger pickup, a fight with poison
  ticking and wearing off, then save and load. A full 3-level game was **not** played by
  hand in a real terminal.

### What round 4 added

| Area | What changed |
|------|--------------|
| `dungeon/game.py` | `ENEMY_START_HP = 12` (was 8). New `POISON_TURNS = 3`, `POISON_DAMAGE = 1`. `Game` gains `poison: int = 0` (turns left). `move()` now does: game-over check → wall check → `_poison_tick()` → stop if lost → `_step()` (the old body of `move`, split out). `_attack` sets `poison = POISON_TURNS` on every hit-back. `drink()` is allowed at full HP while poisoned, sets `poison = 0`, and never ticks. `SAVE_VERSION = 4`, `player.poison` in `to_dict`/`from_dict` (validated 0..3), new `_upgrade_v3` (adds `poison: 0`, leaves enemies alone). |
| `dungeon/cli.py` | Status line ends with `   Poisoned: n turn(s)` only while poisoned. Help text explains 12 HP enemies, poison and that a potion cures it. |
| `tests/` | New `test_r9_enemy_hp.py` and `test_r10_poison.py`. Rewritten for the changed rules on the default game: `test_r2_starting_stats`, `test_r2_enemy_dies_and_is_removed`, `test_r2_player_can_walk_into_freed_tile`, `test_r6_strong_attack_kills_in_one_hit_without_hit_back`, `test_r7_enemies_on_later_levels_have_the_same_stats` (docstrings say "changed in round 4"); `test_r5_drink_at_full_hp_keeps_potion` docstring updated. `test_r4_save_load.py`: v4 exact layout, 7 new malformed `poison` cases, valid v4 base save, v3 upgrade tests, v2 → v3 → v4 chain test, `test_r4_loaded_game_continues_play` adjusted to 3 hits. |
| `spec.md` | Round 4: new "Turns" section, R2/R3.2/R4.1/R4.3/R4.5/R5.2/R5.4/R5.5/R7.5 updated, new R9.1-R9.3 and R10.1-R10.8, v4 layout, out-of-scope list. |
| `docs/decisions/` | 0007 (12 HP everywhere, old saves keep enemy HP), 0008 (poison timing and what a turn is). |
| `README.md` | Enemy HP, poison, round 3 saves, R1-R10. |

## How to run

```
py -m dungeon            # new game, level 1 of 3
py -m dungeon --load     # continue from savegame.json in the current directory
```

In the game: `w a s d` move, `p` or `drink` drinks a potion (heals 10, cures poison), then
`save`, `load`, `help`, `quit`.
Map: `@` you, `E` enemy, `X` exit, `#` wall, `.` floor, `!` potion, `-` dagger, `/` sword, `T` axe.

## How to run the tests

```
.\.venv\Scripts\Activate.ps1              # PowerShell (Git Bash: source .venv/Scripts/activate)
py -m pytest
```

If `.venv` is missing: `py -m venv .venv`, activate it, then `py -m pip install -r requirements-dev.txt`.
Without activating: `.venv/Scripts/python -m pytest`.

## Decisions made in round 4, and why

Decisions 1-4 are the user's answers to the round 4 questions. The rest are mine. The user
saw the list of my decisions in chat at the end of the round but has not formally approved it.

1. **Enemy HP (user, ADR 0007).** In the context of R9, facing how much HP to add and whether
   it grows per level, we decided for 12 HP for every enemy on every level with damage still
   3, and neglected 12/16/20 per level and 16 everywhere, to achieve no single weapon
   one-hitting while R7.5 ("same stats on every level") and `Enemy` stay unchanged, accepting
   that sword + axe (Atk 13+) still one-hits everything.
2. **Who poisons (user).** In the context of R10, facing which enemies poison, we decided for
   every enemy poisoning on its hit-back, and neglected a separate poison enemy type with its
   own map symbol, to achieve no new symbol, enemy state or save field for enemies, accepting
   that all enemies are still identical.
3. **Poison strength (user).** In the context of R10's damage over time, facing how long and
   how hard, we decided for 1 damage for 3 turns with a new hit resetting the count to 3, and
   neglected stacking turns and 2 damage for 2 turns, to achieve poison that matters but
   cannot pile up in long fights, accepting that repeated hits on one enemy keep the player
   poisoned without making it worse.
4. **Potion cures (user).** In the context of R5 potions meeting R10, facing whether potions
   help against poison, we decided for a drink that heals 10 and cures poison, and neglected
   poison that only wears off, to achieve a way to fight back against poison, accepting that
   R5.4 changed (drinking at full HP is allowed while poisoned).
5. **What a turn is (ADR 0008).** In the context of poison needing a clock, facing which
   commands count, we decided for only state-changing actions (a move onto a non-wall tile,
   an attack, a drink that is not refused), and neglected counting every typed command, to
   achieve no damage for `help`, `save` or a wall bump and keeping R1.2 ("a wall bump changes
   nothing") true, accepting a "Turns" definition in `spec.md` that every new command must be
   checked against.
6. **Tick at the start of a move or attack (ADR 0008).** In the context of R10, facing where
   in a turn the 1 damage lands, we decided for before the action, and neglected the end of
   every turn and the end of turn skipping the turn it was applied, to achieve a hit-back
   that costs exactly 3 HP on its own turn and "3 turns" meaning the next 3 actions, accepting
   that poison can kill before the action (the player doesn't move or attack).
7. **No tick on a drink.** In the context of drinking while poisoned, facing a potion at 1 HP
   being followed by a fatal tick, we decided for the drink curing before poison can hurt,
   and neglected ticking on drinks too, to achieve a potion that always saves a poisoned
   player, accepting a special case in the turn rule.
8. **Poison can lose on the last exit.** In the context of the step onto the last level's
   exit, facing a tick that takes HP to 0 on that step, we decided for losing (tick first,
   no move), and neglected letting the win count first, to achieve one order (tick, then act)
   everywhere, accepting that a player at 1 HP and poisoned should drink before the exit.
9. **Re-hit order.** In the context of being hit while already poisoned, facing the order of
   tick and reset, we decided for the old poison ticking first and the hit-back then resetting
   the count to 3, and neglected resetting first, to achieve the order following from the
   tick-then-act rule, accepting that a re-hit turn costs 3 + 1 HP.
10. **Killing blows don't poison, and poison carries to the next level.** In the context of
    R10 with R2.2 and R7.3, facing whether these follow the poison rule, we decided for no
    poison without a hit-back and poison carrying like HP, and neglected clearing poison on a
    level change, to achieve no exceptions to the existing rules, accepting that a poisoned
    player arrives on the next level still losing HP.
11. **Round 3 saves keep their enemy HP (ADR 0007).** In the context of upgrading v3 saves,
    facing unhurt 8 HP enemies on the saved level, we decided for keeping saved enemy HP as is
    with `poison: 0`, and neglected raising it (+4 or ×1.5), to achieve a save that loads exactly
    as saved, accepting that the saved level stays easier; later levels get 12 HP from their maps.
12. **Save validation.** In the context of `from_dict`, facing which new checks to add, we
    decided for only checking `poison` is an integer 0..3, and neglected adding a maximum enemy
    HP, to achieve a minimal change, accepting that enemy HP in saves is still only checked > 0.
13. **Status line.** In the context of the CLI, facing showing poison, we decided for adding
    `Poisoned: n turns` at the end only while poisoned, and neglected an always-shown
    `Poison: 0`, to achieve no longer line in the common case, accepting that the line's
    length changes during play.
14. **Tests on the default game use teleporting.** In the context of rewriting the changed R2,
    R6 and R7.5 tests on `LEVELS`, facing long real routes to an enemy, we decided for setting
    `game.player` next to an enemy (level 1: player (3, 4), enemy (3, 3)), and neglected
    scripted walks, to achieve short, clear tests, accepting that they skip the real route.
15. **New `CLAUDE.md` rule (uncommitted).** In the context of standing rules, facing new
    commands or actions silently changing what a turn is, we decided for a rule that every new
    command or game action must be placed in `spec.md`'s "Turns" section and tested for whether
    poison ticks, and neglected leaving it only in this handoff, to achieve every session seeing
    it, accepting one more rule to read. **Check that it is wanted.**

## Unresolved / open questions

- **Balance is still easy for a player who finds every weapon.** A search over every move of
  the default game (a re-implementation of the rules, run outside the repo, not committed)
  found it winnable: the best line takes all three level 1 weapons (Atk 14, 15 with level 2's
  dagger), one-hits everything and finishes level 3 at 20/20 HP with 5 potions. Without the
  weapons it is much harder. Ask the user before changing numbers or maps.
- **Should a winnability check be a real test?** The search took ~2 minutes for level 1, too
  slow for the suite as written. Not discussed with the user.
- **Round 3 saves' current level keeps 8 HP enemies.** My choice (decision 11), not the user's.
- **Enemy HP in saves has no upper bound** (e.g. 1000 loads). Cross-field checks are also still
  missing: `playing` on `X`, `lost` with HP > 0, `won` off `X` or with levels left, two enemies
  on one tile, and now `poison > 0` in a `won` save.
- **Enemy HP isn't visible** except in the attack message. Out of scope, but players can't see
  how hurt an enemy is.
- **Level 2's exit is only reachable through an enemy** (row 8, col 9); still not discussed.
- **"Enemies left" counts only the current level.** Still not chosen by the user.
- **Round 1 UX questions still open:** no `load` after the game ends, `save` overwrites silently,
  `quit` doesn't offer to save, `savegame.json` is in the current directory.
- **Game length vs `problem.md`** (a short break): 3 levels plus tougher fights make it longer.
- **No full hand playtest in a real terminal.**

## Warnings for the next session

- **Bare `pytest` fails** to import `dungeon`. Use `py -m pytest` inside `.venv`. Don't add
  `conftest.py`/`pythonpath` without asking.
- **Every new command or action must be checked against "Turns" in `spec.md`.** `move` ticks
  poison after the wall check; `drink` never ticks. A new action that changes the game must
  decide whether to call `_poison_tick()` first, and stop if it sets `lost`.
- **`_poison_tick()` returns a message ending in a space** (so it can prefix the action's
  message), except when the player died. Keep that if you add callers.
- **A v5 save format** needs `_upgrade_v4` (4 → 5), added after the three existing steps in
  `from_dict`. Don't change older steps to jump ahead. Update the exact-shape test
  `test_r4_save_writes_json_with_full_state`, which asserts the whole v4 JSON (including
  `poison: 3` and an enemy at 4 HP).
- **Validation in `from_dict`:** anything after the `try` block must only raise `SaveError`.
  Convert raw values with `_int`/`_str`/`_str_list`/`_map_list` inside the `try`.
- **Literal numbers in tests:** 20 HP, 5 base attack, **12**/3 enemy stats, 3 poison turns,
  1 poison damage, 10 heal, weapon bonuses 1/3/5, 3 levels. Changing enemy HP or poison breaks
  R2, R4 (exact JSON, enemy HP 4 and 7), R6, R7, R9 (hits-per-attack table) and R10 tests.
- **Fights now hit back more often.** Any test that attacks an enemy and then checks HP must
  count poison ticks on later turns. E.g. a 3-hit kill at Atk 5 costs 3 + 1 + 3 + 1 = 8 HP by
  the killing blow, and leaves 2 poison turns that cost 2 more HP on the next 2 moves.
- **`LEVELS[0] is DEFAULT_MAP`** (same list). Never mutate `LEVELS` or `DEFAULT_MAP` in tests.
- **Tests that pin the level maps:** `test_r7_there_are_three_built_in_levels`,
  `test_r7_later_levels_are_harder`, `test_r6_default_map_has_items`, the R8 tests, the v2
  upgrade tests, and the R2/R6/R10 tests that use level 1's enemy at (3, 3) with the player at
  (3, 4). Changing level 1 near that spot breaks them.
- **Adding a map symbol** touches `ITEM_CHARS` (or `from_map`), `render`, the help text, and the
  legends in `spec.md` and the README. It must not be `w a s d p` in either case.
- **Shell quirks:** Git prints LF→CRLF warnings on every add (harmless). Throwaway experiments
  (the winnability search) were kept in the session scratchpad, outside the repo.
