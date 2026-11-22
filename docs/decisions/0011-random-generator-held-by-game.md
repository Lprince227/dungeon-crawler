# 0011: The paralysis roll uses a random generator held by the game and not saved (R12)

- Status: accepted. My choice, named in chat before the code was written; the
  user has not reviewed it yet.
- Date: 2026-11-22
- Requirements: R12.4, R12.7 (75% chance a paralysed attack fails), R4 (save
  and load), and the CLAUDE.md rule that game logic is tested

## Background

R12 brings the first random rule into a game that was fully deterministic
until round 5. Tests must be able to check both outcomes of the roll (a failed
attack and a landed one) and the 0.75 boundary, without flaky results. Saves
must still round-trip to an equal game (R4.2), and the save format should stay
plain JSON data.

## Decision (Y-statement)

In the context of **the 75% paralysis roll in `dungeon/game.py`**,
facing **how to make the roll testable and what a save should hold about it**,
we decided for **a `random.Random` held by each `Game` (`Game.rng`, created
fresh by default, left out of equality and repr, and not saved), with an
attack failing when `rng.random() < 0.75`, so that tests swap in a stub or a
seeded generator**
and neglected **calling the module-level `random.random()` (tests would patch
the global), saving the generator's state or a seed in the save file, and
replacing chance with a fixed pattern (e.g. fail 3 of every 4 paralysed
attacks)**,
to achieve **tests that set the exact roll, a save format that holds only game
state, and a real 75% chance in play**,
accepting **that saving and loading then attacking can give a different roll
than playing on (so save-scumming a failed attack is possible), and that
`Game` equality now ignores one field**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Module-level `random.random()` | Tests would have to monkeypatch the `random` module, and two games would share one generator. |
| Save the generator state or a seed | `getstate()` is a large tuple tied to Python's implementation. Saving a seed would make reloads replay the same rolls. Both add a save field that can be malformed, only to stop save-scumming in a short single-player game. |
| Fixed pattern instead of chance | Exactly predictable, but R12 asks for a 75% chance, and players could learn the pattern. |
| Generator held by `Game`, not saved (chosen) | Small change, fully testable, and the save stays plain state. |

## Consequences

- `Game.rng: random.Random = field(default_factory=random.Random, compare=False, repr=False)`.
  `from_dict` gives a loaded game a new generator, and `to_dict` never writes it.
- Only attacks on a paralysed turn call `rng.random()`. Moves, drinks and
  unparalysed attacks never do, which tests check with a generator that
  raises if called.
- The R12 tests use a fixed roll for each outcome and one seeded run of 2000
  attacks to check the rate is near 75%.
