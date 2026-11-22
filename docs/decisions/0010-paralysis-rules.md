# 0010: A failed paralysed attack uses the turn without a hit-back; paralysis counts turns like poison (R12)

- Status: accepted. The user chose all four rules: a failed attack uses the
  turn and the enemy does not hit back; the 3 turns count every kind of turn,
  as poison does; every level 3 hit-back paralyses (as well as poisoning);
  one potion cures both, and a paralysed player at full HP may drink. Storing
  "paralyses" on each enemy, ticking paralysis after poison, and the messages
  are my choices.
- Date: 2026-11-22
- Requirements: R12 (paralysis), which changes R2 (combat had no randomness),
  R5.4 (drinking at full HP) and R11.6 (hit counts on level 3); R4 (save)

## Background

R12 says level 3 enemies can paralyse, giving "a 75% chance to not be able to
attack that turn for 3 turns", cured by a potion. It does not say what a
failed attack costs, what counts as one of the 3 turns, how often a level 3
hit-back paralyses, or how the cure fits the round 4 potion rules (R5.4,
R10.5). Enemies here act only when hit (R2.3), so whether a failed attack
causes a hit-back decides whether paralysis can trap a player.

## Decision (Y-statement)

In the context of **R12 paralysis in a turn-based game where enemies act only
when attacked**,
facing **what a failed attack costs and how the 3 turns are counted**,
we decided for **a failed attack that uses the turn (poison and paralysis
tick) with no damage and no hit-back, 3 turns counted like poison (any move,
attack or drink, ticking after poison), a paralysis on every level 3
hit-back that resets to 3 rather than stacking, and one potion that cures
both statuses, also at full HP**
and neglected **a failed attack that still draws a hit-back, a failed attack
that is not a turn, counting only attack attempts, a chance that a level 3
hit-back paralyses, paralysis instead of poison on level 3, and a cure that
is still refused at full HP**,
to achieve **a status that slows fights without trapping the player (walking
away for 3 turns always ends it), the same turn rule and cure as poison, and
only one random roll in the game**,
accepting **that combat is no longer fully predictable (R2 changed), that a
patient player can wait out paralysis at the cost of poison ticks, and a new
save field on the player and on each enemy (version 6)**.

## Alternatives considered

| Option | Why not |
|--------|---------|
| Failed attack still draws a hit-back | Each hit-back paralyses again, so a player who keeps attacking stays paralysed and loses HP every turn. It also breaks R2.3 (enemies act only when hit). |
| Failed attack is not a turn | Paralysis would never tick down on attacks, and a refused action that still rolls is confusing. |
| Count only attack attempts | Walking away would not help, and it would differ from poison's turn rule. |
| Chance that a hit-back paralyses | A second random roll, plus a number the requirement does not give. |
| Level 3 paralyses instead of poisoning | Changes R10.1 (every enemy poisons) without being asked to. |
| Cure refused at full HP | A paralysed player at full HP could not cure it, unlike poison (R5.4 as changed in round 4). |
| Turn used, no hit-back, poison's turn rule, one cure (chosen) | Reuses the R10 turn model, so it fits the existing Turns section. |

## Consequences

- `Enemy.paralyses` (from `enemy_paralyses(level)`, true from level 3) and
  `Game.paralysis` (0 to 3). `move` ticks poison, then paralysis, and then
  `_step` rolls only when the target is an enemy on a paralysed turn.
- R5.4 changed: drinking at full HP is refused only when the player is
  neither poisoned nor paralysed. The R11.6 level 3 hit counts assume no
  paralysis, and that test clears paralysis between hits.
- `SAVE_VERSION = 6`, with `player.paralysis` and each enemy's `paralyses`.
  `_upgrade_v5` loads round 5 saves unparalysed, with enemies on a saved
  level 3 or later paralysing.
- Balance: waiting out paralysis (3 steps) costs the same 3 poison HP that the
  same turns would cost anyway. So an Atk 15 player still pays 7 HP per
  level 3 enemy (one hit-back of 4, then 3 poison) and only spends more turns.
  The round 5 winnability search was not re-run.
