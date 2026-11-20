# 0001: Save file format

- Status: accepted
- Date: 2026-11-20
- Requirement: R4 (save the game to a file and load it again)

## Decision (Y-statement)

In the context of **R4 saving and loading a game in progress**,
facing **the need for a file that is safe to load, survives code changes, and
can be checked in tests**,
we decided for **a versioned JSON document (`{"version": 1, "map", "player",
"enemies", "status"}`) that is validated field by field on load**
and neglected **Python `pickle`, a custom plain-text format, and SQLite**,
to achieve **a format that is easy to read and edit by hand, loading that
cannot run code, clear `SaveError` messages for bad files, and a version
field for future migrations**,
accepting **that we must write and maintain explicit `to_dict` / `from_dict`
conversion and validation code, and that players can easily edit (cheat in)
their save**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| `pickle` | Almost no code needed, but loading a tampered file can run arbitrary code. Saves also break when classes are renamed or moved, and they cannot be read or compared in tests. |
| Custom text (e.g. the map plus `HP=17` lines) | Readable, but we would have to write and test our own parser. Nested data like the enemy list is awkward. |
| SQLite (`sqlite3`) | Robust, but far too heavy for one small game state and not readable by people. |
| JSON (chosen) | Standard library, readable, safe to parse, and maps directly to the game state. |

## Consequences

- `Game.to_dict` and `Game.from_dict` must be updated whenever the game state
  gains a field. The round-trip tests in `tests/test_r4_save_load.py` catch any that are missed.
- Saves are written to a temp file and then moved into place, so a crash while
  saving does not destroy the previous save.
- A future format change bumps `version`. Old saves are then either migrated
  or rejected with a clear message.
