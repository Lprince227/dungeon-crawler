# 0002: Store collected weapons as a list and derive attack

- Status: accepted
- Date: 2026-11-20
- Requirement: R6 (weapon pickups with varying attack bonuses that stack)

## Decision (Y-statement)

In the context of **R6 weapons whose attack bonuses stack as more are collected**,
facing **the need to keep attack, the save file and the status line consistent
with each other**,
we decided for **storing the names of the collected weapons (`Game.weapons`,
e.g. `["dagger", "sword"]`) and computing `Game.attack` as base attack plus the
sum of their bonuses from the `WEAPONS` table**
and neglected **a stored attack number that grows on each pickup, a single
"equipped weapon" slot, and a separate `attack_bonus` counter**,
to achieve **one source of truth: attack can never disagree with the weapons
the player holds, saves record what was picked up, and changing a bonus in
`WEAPONS` applies to old saves too**,
accepting **that the save stores names that must be checked against `WEAPONS`
on load, and that renaming a weapon kind would break saves that use the old name**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Store `player_attack` and add the bonus on pickup | Simplest, but the number and the items picked up can drift apart, and a save could hold any attack value with no way to check it. |
| One equipped-weapon slot (new weapon replaces old) | Does not meet R6: bonuses must stack. |
| Store an `attack_bonus` integer | Stacks correctly, but loses which weapons were collected (nothing to show the player) and a hand-edited save could set any bonus. |
| List of weapon names, derived attack (chosen) | Small, readable in the save, validated against the `WEAPONS` table. |

## Consequences

- `PLAYER_ATTACK` is now the base attack. Combat uses `Game.attack`.
- `from_dict` rejects unknown weapon names with `SaveError`.
- New stats (e.g. defense) would need their own table entry per weapon. They
  are out of scope for round 2.
