# Handoff: end of round 2

Written for a fresh session starting round 3. Standing rules for every session
are in `CLAUDE.md`. Read that first, then `problem.md`, `spec.md`,
`docs/decisions/` and this file. `handoff-round-1.md` still has useful history,
but this file replaces it where they differ.

## Current state

- R1-R6 from `problem.md` are implemented. **85 tests pass** with `py -m pytest`
  (Python 3.12.10, pytest 9.2.0 in `.venv`).
- Round 2 is 8 commits, from `211c799` (spec) to `784af3c` (ADR 0003). Run
  `git log --oneline 6713eca..HEAD` to see them. The working tree was clean after the last commit.
- Round 2 order: spec → failing tests → R5 → R6 → save v2 → README → ADRs.
- A scripted game was played through `run()`: dagger pickup, a fight, drink, save, load.
  A full game was **not** played by hand in a real terminal this round.

### What round 2 added

| Area | What changed |
|------|--------------|
| `dungeon/game.py` | New `Item(pos, kind)` dataclass. `Game` gains `potions: int`, `weapons: list[str]`, `items: list[Item]`. New constants `PLAYER_MAX_HP` (=20), `POTION_HEAL` (=10), `WEAPONS` (`dagger` 1, `sword` 3, `axe` 5), `ITEM_CHARS`, `ITEM_KINDS`, `GAME_OVER`. New `attack` property, `item_at()`, `drink()`, `_pick_up()`. `move()` picks up items. `_attack()` uses `self.attack`. `SAVE_VERSION = 2`. `_upgrade_v1`, `_str`, `_str_list` helpers. `DEFAULT_MAP` has 3 potions and one of each weapon. |
| `dungeon/cli.py` | `p` / `drink` command (via `ALIASES`), items drawn on the map, longer status line (`HP: x/20   Atk   Potions   Weapons   Enemies left`), help text explains items. |
| `tests/` | New `test_r5_potions.py` (10 tests) and `test_r6_weapons.py` (9 tests). `test_r4_save_load.py` rewritten for v2 (10 test functions, the malformed-save one has 19 cases). R1-R3 tests are unchanged. |
| `spec.md` | Round 2 spec: map legend, R4.3 extra checks, R4.5 versions, R5.1-R5.5, R6.1-R6.4, default map, out-of-scope list. |
| `docs/decisions/` | `0002-weapons-stored-as-list.md`, `0003-upgrade-version-1-saves.md`. |
| `README.md` | Potions, weapons, the drink command, old saves. |

## How to run

```
py -m dungeon            # new game
py -m dungeon --load     # continue from savegame.json in the current directory
```

In the game: `w a s d` move, `p` or `drink` drinks a potion, then `save`, `load`, `help`, `quit`.

## How to run the tests

```
.\.venv\Scripts\Activate.ps1              # PowerShell (Git Bash: source .venv/Scripts/activate)
py -m pytest
```

If `.venv` is missing: `py -m venv .venv`, activate it, then `py -m pip install -r requirements-dev.txt`.
Without activating: `.venv/Scripts/python -m pytest`.

## Decisions made in round 2, and why

The user chose 1-4 when asked. The rest are my choices. The user has seen the list but has not
formally approved it.

1. **Potion heal (user).** In the context of R5 potions, facing how strong a potion should be,
   we decided for healing 10 HP capped at the 20 HP maximum, and refusing to drink at full HP
   (the potion is kept), and neglected heal-to-full and uncapped healing, to achieve potions that
   matter without letting the player stockpile HP, accepting that a potion drunk at 15 HP wastes 5.
2. **Pickup (user).** In the context of collecting potions, facing how the player gets them, we
   decided for automatic pickup on stepping and no carry limit, and neglected a carry limit of 3 and an
   explicit `get` command, to achieve the fewest commands in a short game, accepting that the player
   can't leave a potion on the floor for later.
3. **Weapon stats (user).** In the context of R6 "varying stats such as attack", facing which stats
   weapons change, we decided for attack only, and neglected attack + defense and attack + max HP,
   to achieve simple, easy-to-test balance, accepting that weapons are only a damage boost.
4. **Old saves (user, ADR 0003).** In the context of the save format going from v1 to v2, facing
   players with round 1 saves, we decided for upgrading v1 saves on load (0 potions, no weapons,
   no items), and neglected rejecting them and copying the default map's items into them, to achieve
   old games that keep working through one validation path, accepting that upgraded games have
   nothing to pick up.
5. **Weapon state (ADR 0002).** In the context of stacking weapon bonuses, facing keeping
   attack, the save and the display consistent, we decided for storing collected weapon names and
   deriving `attack`, and neglected a stored attack number, a single weapon slot and an
   `attack_bonus` counter, to achieve one source of truth that saves can validate, accepting that
   renaming a weapon kind breaks saves that use the old name.
6. **Weapon kinds and bonuses.** In the context of R6 "varying stats", facing picking concrete
   values, we decided for dagger +1, sword +3, axe +5, every weapon giving some bonus, and
   neglected 0-bonus weapons (the user's "some improve player stats" could be read that way),
   to achieve visibly different weapons, accepting that the sword or the axe makes every enemy a one-hit kill.
7. **Duplicates stack, nothing is dropped.** In the context of R6 "stats stack", facing repeat
   pickups, we decided for every copy adding its bonus and no unequip, and neglected
   ignoring duplicates and a drop command, to achieve the literal reading of "stack", accepting that
   a map with many axes would make the player very strong.
8. **Map symbols.** In the context of the text map, facing new tile characters, we decided for
   `!` potion and `d`/`s`/`a` for dagger/sword/axe, and neglected digits and punctuation such as
   `/` and `|`, to achieve symbols that are easy to read and remember, accepting that the weapon
   letters are the same as three movement keys. This is only a visual overlap, not a command clash.
9. **Drinking and turns.** In the context of R5 "use on any turn", facing whether drinking costs
   anything, we decided for drinking taking the turn with nothing else happening, and when there are
   no potions or the game is over it only returns a message, and neglected having enemies react, to
   achieve consistency with enemies that only act when hit, accepting that "taking a turn" currently means nothing.
10. **Default map placement.** In the context of `DEFAULT_MAP`, facing where to put the
    items, we decided for 3 potions and one of each weapon on existing floor tiles, with the 6 enemies
    and the walls unchanged, and neglected redesigning the map, to achieve the smallest change to a
    tested map, accepting that balance was not tuned (see Unresolved).
11. **Save layout.** In the context of save v2, facing where the new fields go, we decided for
    `potions` and `weapons` under `player` and a top-level `items` list, and neglected a separate
    `inventory` object, to achieve a shape that matches the `Game` fields, accepting one more
    top-level key.
12. **Stricter validation.** In the context of loading saves, facing hand-edited or corrupt
    files, we decided for rejecting HP above 20 (in v1 saves too), negative or non-integer potion
    counts, unknown weapon names, non-string or unknown item kinds, and items that are off floor tiles or share
    a tile with another item, an enemy or the player, and neglected accepting them, to achieve no
    impossible games after a load, accepting that a v1 save with HP above 20 no longer loads.
13. **Status line.** In the context of the CLI, facing showing the new state, we decided for
    `HP: x/20   Atk: n   Potions: n   Weapons: a, b   Enemies left: n`, and neglected a separate
    `inventory` command, to achieve everything visible on every turn, accepting a long line.
14. **Test changes.** In the context of the R4 tests, facing the v2 format, we decided for
    rewriting the exact-layout test for v2 and adding a test that the sample save used by the
    malformed cases is itself valid, and neglected keeping a v1 exact-layout test, to achieve
    malformed cases that fail for the intended reason, accepting that the v1 layout is now only checked
    by the upgrade test.
15. **Two ADRs.** In the context of step 5 ("at least one decision record"), facing which
    decisions to record, we decided for 0002 (my choice) and 0003 (the user's choice), and
    neglected recording only one, to achieve a record of the save-format choice too, accepting
    that 0003 records a decision the user made, not me.
16. **CLAUDE.md edits at the end of round 2 (uncommitted).** I added two standing rules: keep
    old save versions loading via an upgrade step, and the Y-statement template the user gave.
    The first one generalises the user's one-off v1 choice. Check it's wanted.

## Unresolved / open questions

- **Balance is now even easier.** Base attack (5) and dagger (6) kill an enemy in 2 hits.
  The sword alone (Atk 8) or the axe (Atk 10) kills every enemy in one hit, so they never hit back. Potions are rarely needed. Ask the
  user before changing any numbers, because tests and `spec.md` use them.
- **Some cross-field checks are still missing in `from_dict`.** Items are now checked against
  enemies and the player, but these still load: `playing` while standing on `X`, `lost` with HP > 0,
  `won` while not on `X`, and two enemies on the same tile.
- **Item and enemy order matter for equality.** `Game ==` compares lists, so two saves with the same
  items in a different order are "different" games. That's fine for round trips, but don't rely on it otherwise.
- **`run()`, `render()` and `main()` have no tests** (drawing doesn't need them, per `CLAUDE.md`).
  `run` accepts `read`/`write` arguments if tests are wanted.
- **Round 1 UX questions are still open:** you can't `load` after the game ends (`run` returns),
  `save` overwrites silently, `quit` doesn't offer to save, and `savegame.json` goes in the current directory.
- **No hand playtest in a real terminal this round.**

## Warnings for the next session

- **Bare `pytest` fails** to import `dungeon`. Use `py -m pytest` inside `.venv`. Don't add
  `conftest.py`/`pythonpath` without asking (it would be a new decision).
- **Adding state to `Game`, `Enemy` or `Item`** means updating `to_dict`, `from_dict` and its
  validation checks, the R4 tests, `SAVE_VERSION`, and an upgrade step for v2 saves (`_upgrade_v1`
  currently goes straight to the current version, so a v3 bump needs a v1→v2→v3 chain or similar).
- **Validation runs outside the `try` block.** Anything after the `try` in `from_dict` must not raise
  anything except `SaveError`. A list as an item kind once crashed with `TypeError` from a set lookup.
  Convert raw values with `_int`/`_str`/`_str_list` inside the `try`.
- **Exact-shape test:** `test_r4_save_writes_json_with_full_state` asserts the full v2 JSON. Any
  format change fails it (on purpose).
- **Literal numbers in tests:** 20 HP, 5 base attack, 8/3 enemy stats, 10 heal, weapon bonuses
  1/3/5, and `test_r6_default_map_has_items` checks the item mix on `DEFAULT_MAP`.
- **`PLAYER_ATTACK` is the base attack.** Combat must use `game.attack`, not the constant.
- **Adding a map symbol** touches `ITEM_CHARS` (or `from_map`), `render` (through `ITEM_SYMBOLS`),
  the help text, and the legend in `spec.md` and the README. Make sure it doesn't clash with `@ E X # .`.
- **Shell quirks:** scripted Python string replacements through a Bash heredoc mangled a `\n`
  escape once. For multi-line or escaped edits, the Edit/Write tools are safer. Git prints LF→CRLF
  warnings on every add (harmless, no `.gitattributes`).
- **Uncommitted on purpose:** `handoff-round-2.md` and the `CLAUDE.md` edits. The user reviews them first.
