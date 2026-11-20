# Handoff: end of round 1

Written for a fresh session starting round 2. Standing rules for every
session are in `CLAUDE.md`. Read that first, then `problem.md` and `spec.md`.

## Current state

- R1-R4 from `problem.md` are implemented. **41 tests pass** with `py -m pytest`.
- The last round 1 commit is `3ed85d2` ("Add ADR 0001: versioned JSON save format").
  Run `git log --oneline` for the full history. There are 12 commits on top of the two `problem.md` commits.
- The game has been played by hand from the terminal: save, `--load`, combat, winning, and a corrupt save
  were all tried.

### Layout

| Path | What it is |
|------|------------|
| `dungeon/game.py` | All game rules: `Game`, `Enemy`, `DEFAULT_MAP`, the stat constants, `move()`, `to_dict`/`from_dict`, `save_game`/`load_game`, `SaveError`. No I/O except the save file. |
| `dungeon/cli.py` | Terminal front end: `parse_command`, `render`, `run` loop, `main` (argparse, `--load`). |
| `dungeon/__main__.py` | Lets `py -m dungeon` start the game. |
| `tests/test_r1_movement.py` ... `test_r4_save_load.py` | One file per requirement. Every test has the requirement ID in its name and docstring. |
| `spec.md` | Detailed rules (R1.1, R2.3, ...) that the tests are built on. |
| `docs/decisions/0001-save-file-format.md` | Y-statement ADR: versioned JSON instead of pickle, custom text or SQLite. |
| `README.md`, `requirements-dev.txt` | User docs. pytest is the only dev dependency. |

## How to run

```
py -m dungeon            # new game
py -m dungeon --load     # continue from savegame.json in the current directory
```

## How to run the tests

```
py -m venv .venv                          # only if .venv is missing
.venv\Scripts\activate                    # PowerShell: .\.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
py -m pytest
```

A `.venv` with pytest 9.2.0 already exists on this machine, but it is git-ignored.
Without activating it you can run `.venv/Scripts/python -m pytest`.

## Decisions made in round 1, and why

The user chose 1-4 when asked. The rest are my choices, which the user has
seen but not formally approved.

1. **Typed command + Enter** (`w/a/s/d`, `save`, `load`, `help`, `quit`). User's choice.
   Works on every OS with only the standard library and is easy to test.
2. **Bump-to-attack, enemies stand still.** User's choice. Kept simple for short sessions.
3. **One fixed hand-made map** (`DEFAULT_MAP`, 11×11, 6 enemies). User's choice.
   Both routes to the exit force at least one fight.
4. **One JSON save file, `savegame.json`.** User's choice. The ADR explains why JSON was picked over the alternatives.
5. **Fixed stats, no randomness:** the player has 20 HP and deals 5 damage. Enemies have 8 HP and deal 3. This makes
   tests deterministic. Each enemy costs the player 3 HP, so the game is easy to win.
6. **Combat details:** killing an enemy does not move the player into its tile, and a dying enemy
   does not hit back. HP is clamped at 0.
7. **Walls and the grid edge block movement** with a message and no state change.
8. **After the game ends,** `move()` is a no-op that returns "Game over...". The CLI prints
   the result and exits.
9. **Save file details:** saves include `"version": 1` and are fully validated on load. Any problem raises `SaveError`, and
   the CLI keeps the current game. Saves are written to `savegame.json.tmp` and then moved into place with
   `os.replace`, so a crash cannot corrupt the previous save.
10. **The save stores the map itself,** not just positions on `DEFAULT_MAP`. Old saves keep working if
    the default map changes later.
11. **Code layout:** the rules (`game.py`) are kept apart from input and output (`cli.py`), so all logic can be tested without a terminal.
12. **`.gitignore`** also ignores `savegame.json` and `*.tmp`, beyond what the user listed.
13. **Tests were committed first** (failing), then the code one requirement per commit.
14. **Git identity:** the machine had no git identity configured, so `user.name=Lprince227` and
    `user.email=ladarrien123@gmail.com` are set in this repo's **local** config, copied from the
    existing commits. Global config was not touched.

## Unresolved / open questions

- **No round 2 requirements yet.** Wait for the user. `spec.md` lists what is out of scope so far: random
  maps, multiple levels, items, enemy movement, single-keypress input, colour,
  and named save slots.
- **Balance has not been tuned.** The default map is hard to lose. Ask before changing the stats, because the tests and
  `spec.md` use those numbers.
- **`from_dict` does not check that the fields agree with each other.** It accepts a save with `status: "playing"` while
  the player is standing on `X`, a `lost` save with HP above 0, or two enemies on the same tile. Fields are
  validated one at a time, not against each other.
- **No load after the game ends:** `run()` returns as soon as the game is won or lost, so the player cannot
  type `load` after losing. They have to restart with `--load`. Whether that is acceptable is a UX question for the user.
- **`save` silently overwrites** the existing save. `quit` does not ask for confirmation or offer to save.
- **`savegame.json` is written to the current directory,** not a fixed per-user location.
- **`run()` and `main()` have no tests,** because the brief said drawing doesn't need them. `run` already accepts
  `read`/`write` arguments, so it could be tested with scripted input if wanted.
- **Python 3.10+** is stated in the README but was only tested on 3.12.10.

## Warnings for the next session

- **Bare `pytest` fails** with 4 import errors during collection. Only `py -m pytest` works, because it
  puts the repo root on `sys.path`. There is no `pyproject.toml` or `conftest.py`. Don't "fix" it by
  changing the test command without asking. Adding a root `conftest.py` or a `pythonpath` setting would be a new decision.
- **System Python has no pytest.** `py -m pytest` only works inside the activated `.venv`.
- **Changing the game state** (a new field on `Game` or `Enemy`) means updating `to_dict`,
  `from_dict` and its validation, and the R4 round-trip tests. Otherwise saves silently lose
  data. If the format changes, bump `SAVE_VERSION`.
- **Exact JSON shape:** `test_r4_save_writes_json_with_full_state` checks the save's exact layout. Any format
  change will (correctly) fail it.
- **Fixed stat values in tests:** `test_r2_starting_stats` asserts literal `20` and `8`, and the R4 test asserts HP `17`/`3`.
  Changing the stat constants breaks these on purpose. Update `spec.md` at the same time.
- **Line endings:** git warns "LF will be replaced by CRLF" on every add. It's harmless, but there is no
  `.gitattributes`, so line endings depend on each machine's `core.autocrlf` setting.
- **Shell quirk:** one large Bash heredoc that wrote several files with lots of quotes failed
  with "unexpected EOF". Writing the files with the Write tool worked.
- `handoff-round-1.md` and the latest `CLAUDE.md` edits are **uncommitted on purpose.** The user is
  reviewing them. Don't commit them unless asked.
