# CLAUDE.md

Standing rules for working in this repository.

- **Language:** Python. The spec is in `spec.md` and the requirements are in `problem.md`.
- **Run tests:** `py -m pytest`, with `.venv` activated (system Python has no pytest).
  Use `py -m pytest`, not bare `pytest`. Bare `pytest` cannot import the `dungeon` package.
- **Test naming:** every test names the requirement it checks in its function
  name and docstring (e.g. `test_r2_enemy_hits_back`, `"""R2: ..."""`).
  Only game logic needs tests (movement, combat, win/loss, save/load), not drawing.
- **Commits:** keep them small. The message says what changed and why.
- **Never commit** `.venv/` or `*.jsonl` files.
- Never undo or amend a commit. Fix forward with a new commit.
- Keep game rules in `dungeon/game.py` with no `input()`/`print()`. Terminal I/O belongs in
  `dungeon/cli.py`.
- When game behaviour changes, update `spec.md` in the same piece of work. Tests follow `spec.md`.
- When `Game` or `Enemy` gains or changes state, update `to_dict`, `from_dict` (including
  validation) and the R4 tests. Bump `SAVE_VERSION` if the save format changes.
- Older save versions keep loading: when bumping `SAVE_VERSION`, add an upgrade step in
  `from_dict` (like `_upgrade_v1`) and a test for it, rather than rejecting old saves.
- Record decisions that had real alternatives as `docs/decisions/NNNN-<topic>.md` Y-statements,
  using this template (handoff decision lists use it too):
  "In the context of <use case or component>, facing <concern>, we decided for <option>
  and neglected <alternatives>, to achieve <benefit>, accepting that <drawback>."
  Number files after the highest existing one. If the user made the choice, say so in `Status`.
- Ask the user before writing code when a requirement is unclear.
- At the end of each round, write `handoff-round-<N>.md` for the next session. Don't commit it.
  The user reviews it first.
