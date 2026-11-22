# 0004: Store the levels still to come as full maps in the save

- Status: accepted
- Date: 2026-11-21
- Requirements: R7 (multiple levels), R4 (save and load)

## Decision (Y-statement)

In the context of **R7 levels and saving a game partway through them**,
facing **the need to resume on the right level with the right maps ahead,
for the built-in levels and for the small custom level lists used in tests**,
we decided for **storing the level number plus `next_levels`, the full text
maps (with `@`, enemies and items) of every level still to come, in the save
(version 3), and keeping the same two fields on `Game`**
and neglected **storing only a level index into the built-in `LEVELS`, and
storing a level index plus a name for which level set is being played**,
to achieve **saves that hold everything needed to finish the game, one
`Game` type that works the same for built-in and custom levels, and
validation that can check every map ahead of time**,
accepting **bigger save files (two extra maps on level 1), and that a save
keeps the level maps it was made with even if `LEVELS` is changed later**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Level index only (`"level": 2`), maps looked up in `LEVELS` | Smallest save, but a game built from any other level list (as in the tests) cannot be saved correctly, and editing `LEVELS` would silently change or break existing saves. |
| Level index plus a level-set name | Works for several level sets, but needs a registry of named sets and still breaks when one is edited. More machinery than one small game needs. |
| Full maps of the remaining levels (chosen) | Self-contained and validated with the same `from_map` rules as new games. |

## Consequences

- `from_dict` runs every map in `next_levels` through `Game.from_map` and
  turns a `ValueError` into `SaveError`.
- Upgrading a version 2 save copies `LEVELS[1:]` into it (see ADR 0005).
- `Enemies left` and the other counts only cover the current level. Upcoming
  levels stay as text until they are reached.
