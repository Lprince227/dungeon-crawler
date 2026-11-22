# 0005: Upgrade version 2 saves to level 1 of 3

- Status: accepted (the user chose this option)
- Date: 2026-11-21
- Requirements: R4 (save and load), R7 (levels), R3 (changed win rule)

## Decision (Y-statement)

In the context of **round 3 adding levels to the save format (`SAVE_VERSION`
2 → 3)**,
facing **round 2 saves that hold one map and no level number**,
we decided for **upgrading a version 2 save to level 1, followed by built-in
levels 2 and 3 (`_upgrade_v2`), while a save that was already `won` stays won
with no further levels; version 1 saves go through version 2 first**
and neglected **treating the saved map as the last level (its exit still
wins), and rejecting version 2 saves**,
to achieve **old games that follow the new rule that only the last level's
exit wins, matching the old default map becoming level 1**,
accepting **that an old save whose map was not the default map is still
followed by the built-in levels 2 and 3**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Saved map is the last level | The old game ends exactly as before, but it breaks the round 3 rule that a win needs all three levels. |
| Reject version 2 saves | Least code, but the player loses their game, against the CLAUDE.md rule to keep old saves loading. |
| Level 1, then levels 2 and 3 (chosen) | Small, and an old save plays like a new round 3 game from that point. |

## Consequences

- `_upgrade_v1` now produces version 2, not the current version, so the
  upgrades run as a chain: v1 → v2 → v3.
- A won version 2 save is not re-opened: a game won under the old rules stays
  won. This exception was my choice, not the user's.
