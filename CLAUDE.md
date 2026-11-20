# CLAUDE.md

Standing rules for working in this repository.

- **Language:** Python. The spec is in `spec.md` and the requirements are in `problem.md`.
- **Run tests:** `py -m pytest`
- **Test naming:** every test names the requirement it checks in its function
  name and docstring (e.g. `test_r2_enemy_hits_back`, `"""R2: ..."""`).
  Only game logic needs tests (movement, combat, win/loss, save/load), not drawing.
- **Commits:** keep them small. The message says what changed and why.
- **Never commit** `.venv/` or `*.jsonl` files.
- Never undo or amend a commit. Fix forward with a new commit.
