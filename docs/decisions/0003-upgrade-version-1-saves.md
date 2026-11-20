# 0003: Upgrade version 1 saves instead of rejecting them

- Status: accepted (the user chose this option)
- Date: 2026-11-20
- Requirements: R4 (save and load), R5, R6

## Decision (Y-statement)

In the context of **round 2 adding potions, weapons and map items to the save
format (`SAVE_VERSION` 1 → 2)**,
facing **players who still have a round 1 save on disk**,
we decided for **upgrading a version 1 save while loading it (`_upgrade_v1`):
it becomes a version 2 game with 0 potions, no weapons and no items on the map,
and is then validated like any other save**
and neglected **rejecting version 1 saves with a clear `SaveError`, and filling
the old map with the new default items**,
to achieve **old saves that keep working, and one validation path for every
save**,
accepting **that an upgraded game has no potions or weapons to find, and that
the upgrade code must be kept as long as version 1 saves are supported**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Reject version 1 with a readable message | Least code, but the player loses their game in progress. |
| Add the default map's items to an upgraded save | The save stores its own map, which may not be `DEFAULT_MAP`, and items could land on tiles that already hold enemies or the player. |
| Upgrade with no items (chosen) | Small, safe, and leaves the old game exactly as it was. |

## Consequences

- Saving an upgraded game writes version 2.
- The round 1 HP rule gets stricter: a save with HP above 20 is now rejected
  in either version.
