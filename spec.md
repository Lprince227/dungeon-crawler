# Spec: Terminal Dungeon Crawler (round 6)

A short, turn-based dungeon game that runs in a terminal. One game should take
a few minutes. Python 3.12, standard library only (pytest for tests).

## Map

The dungeon is a series of fixed, hand-made levels (R7). Each level is a grid
written as text:

| Char | Meaning |
|------|---------|
| `#`  | Wall, which cannot be entered |
| `.`  | Floor |
| `@`  | Player start (floor underneath) |
| `E`  | Enemy (floor underneath) |
| `X`  | Exit |
| `!`  | Potion (floor underneath) |
| `-`  | Dagger, Atk +1 (floor underneath) |
| `/`  | Sword, Atk +3 (floor underneath) |
| `T`  | Axe, Atk +5 (floor underneath) |

Positions are `(row, col)`, with `(0, 0)` at the top left. Every map must contain
exactly one `@` and exactly one `X`, and all rows must have the same length.
Any other map, including one using another character such as the round 2
weapon letters `d`, `s` or `a`, is rejected with a `ValueError`.

## Input

The player types a command and presses Enter. Commands are case-insensitive
and surrounding spaces are ignored.

| Command | Effect |
|---------|--------|
| `w` / `a` / `s` / `d` | Move up / left / down / right by one tile |
| `p` / `drink` | Drink one potion (R5) |
| `save`  | Save the game to `savegame.json` |
| `load`  | Replace the current game with the one in `savegame.json` |
| `help`  | Show the command list |
| `quit`  | Leave the game without saving |

An unknown command prints a short hint and changes nothing.

The status line under the map shows HP out of max HP, attack, potions carried,
weapons collected and enemies left, e.g.
`Level: 2/3   HP: 17/20   Atk: 8   Potions: 1   Weapons: sword   Enemies left: 5`.
"Enemies left" counts the current level only. While the player is poisoned
(R10), the line ends with the poison turns left, e.g. `   Poisoned: 2 turns`.
While the player is paralysed (R12), it then shows `   Paralysed: 2 turns`.

## Turns

A **turn** is a move onto a floor, item or exit tile, an attack on an enemy,
or a drink that is not refused. An attack that fails because the player is
paralysed (R12.4) is still a turn. A bump into a wall or the grid edge, a refused
drink (no potions, or full HP while not poisoned), any command after the game
is over, and `save`, `load`, `help`, `quit` or an unknown command are **not**
turns: they change nothing, so poison (R10) and paralysis (R12) do not tick
on them. At the start of a turn, poison ticks first, then paralysis (R12.3).
A drink ticks neither: it cures both (R10.5, R12.5).

## R1: Movement on a grid

- R1.1 A move command moves the player one tile in that direction if the
  target tile is floor (an item on the floor does not block movement).
- R1.2 Walls block movement. The player stays put, gets a message, and the
  game state does not change.
- R1.3 Moving off the edge of the grid is blocked in the same way as a wall.
- R1.4 Keyboard commands map to directions: `w` up, `s` down, `a` left, `d` right.

## R2: Enemies, health and damage

Combat is "bump to attack". Its only random part is paralysis (R12, added in
round 6). Without paralysis, an attack always hits:

- The player starts with 20 HP (also the maximum HP) and a base attack of 5.
  The player's attack is the base attack plus every weapon bonus (R6).
- Each enemy's HP and damage depend on the level it is on (R11): 12 HP and
  3 damage on level 1, 16 HP and 3 damage on level 2, 20 HP and 4 damage on
  level 3. (Before round 5 every enemy had 12 HP and 3 damage; before round 4,
  8 HP.)
- R2.1 Moving into an enemy's tile attacks it instead of moving. The enemy
  loses HP equal to the player's attack.
- R2.2 If the enemy's HP drops to 0 or below, it is removed from the map. The
  player stays on their original tile and can step into the freed tile next turn.
- R2.3 If the enemy survives, it hits back right away. The player loses HP
  equal to that enemy's attack, and is poisoned (R10). A level 3 enemy's
  hit-back also paralyses (R12).
- R2.4 Enemies do not move. Each enemy keeps its own HP between attacks.
- HP is never shown below 0. It is clamped to 0.

## R3: Winning and losing (changed in round 3)

- R3.1 When the player moves onto the exit tile of the **last** level, the
  game ends with status `won`. Reaching the exit of any earlier level is not a
  win: the player goes on to the next level (R7.2). A game built from a single
  map has one level, so its exit wins.
- R3.2 When the player's HP reaches 0, from an enemy's hit or from poison
  (R10), the game ends with status `lost`.
- R3.3 Once the game is over (`won` or `lost`), move and drink commands change
  nothing and return a "game over" message. The terminal program prints the
  result and exits.
- While the game is still going, its status is `playing`.

## R4: Save and load

- R4.1 Saving writes the full game state (current level's map, level number,
  the maps of the levels still to come, player position, HP, potions carried
  and weapons collected, poison and paralysis turns left, every enemy's
  position, HP, attack and whether it paralyses,
  every item still on the map, status) to a JSON file.
- R4.2 Loading that file restores a game equal to the one that was saved, so
  play continues exactly where it left off.
- R4.3 Loading a missing, unreadable or malformed file raises `SaveError`
  with a readable message. In the terminal program, the current game keeps
  going unchanged. Besides the round 1 checks, a save is malformed if: HP is
  above the maximum; the potion count is negative or not an integer; a weapon
  name is unknown; an item has an unknown kind, is not on a floor tile, or
  shares a tile with another item, an enemy or the player. Round 3 adds: the
  level number is not an integer of 1 or more; `next_levels` is not a list of
  maps that each pass the map rules above. Round 4 adds: the player's
  `poison` is not an integer from 0 to 3. Round 5 adds: an enemy's `attack`
  is missing or is not an integer of 1 or more. Round 6 adds: the player's
  `paralysis` is not an integer from 0 to 3; an enemy's `paralyses` is
  missing or is not `true`/`false`.
- R4.4 The program can be started from a save: `py -m dungeon --load`.
- R4.5 The save file has `"version": 6`. Older saves still load:
  - A round 5 save (`"version": 5`) loads with the player not paralysed
    (`paralysis` 0). Each enemy on the saved level paralyses if the save's
    level number is 3 or more (R12.1). Levels still to come are built from
    their maps.
  - A round 4 save (`"version": 4`) gives each enemy on the saved level the
    attack for that save's level number (R11: 3 on levels 1 and 2, 4 on
    level 3 and later). Enemies keep the HP stored in the save, so unhurt
    enemies on a saved level 2 or 3 still have 12 HP. Levels still to come
    are built from their maps and get the round 5 stats for their level.
  - A round 3 save (`"version": 3`) loads with the player not poisoned
    (`poison` 0). Its enemies keep the HP stored in the save (so an unhurt
    enemy on the saved level still has 8 HP), while enemies on the levels
    still to come are built from their maps and get the round 4 HP of 12.
  - A round 2 save (`"version": 2`) becomes level 1, followed by levels 2 and
    3 of the built-in levels. A round 2 save whose status is `won` stays won
    and gets no further levels.
  - A round 1 save (`"version": 1`) is first upgraded to version 2 (0 potions,
    no weapons, no items on the map), then as above.
  - Each upgrade goes up one version: 1 → 2 → 3 → 4 → 5 → 6.
  - Any other version is rejected with `SaveError`.

Version 6 layout (`map` is the current level with only `#`, `.` and `X`;
`next_levels` holds the full text maps, with `@`, enemies and items, of the
levels still to come, in order):

```json
{
  "version": 6,
  "level": 1,
  "map": ["#####", "#...#", "####X"],
  "next_levels": [["@.X"]],
  "player": {"row": 1, "col": 1, "hp": 17, "potions": 0, "weapons": ["sword"], "poison": 3, "paralysis": 0},
  "enemies": [{"row": 1, "col": 2, "hp": 3, "attack": 3, "paralyses": false}],
  "items": [{"row": 1, "col": 3, "kind": "potion"}],
  "status": "playing"
}
```

## R5: Potions

- R5.1 Potions (`!`) lie on floor tiles. Moving onto a potion's tile picks it
  up automatically: it is removed from the map and the player's potion count
  goes up by 1. There is no carry limit.
- R5.2 The drink command (`p` / `drink`) can be used on any turn while the game
  is `playing`. It uses one potion and restores 10 HP, but never above the
  maximum of 20. It also cures poison (R10.5, added in round 4) and
  paralysis (R12.5, added in round 6).
- R5.3 Drinking with no potions does nothing except return a message.
- R5.4 Drinking at full HP (20) while neither poisoned nor paralysed is
  refused: the potion is kept and a message is returned. (Changed in round 4:
  a poisoned player at full HP may drink, to cure the poison. Changed in
  round 6: so may a paralysed one.)
- R5.5 Drinking takes the player's turn but nothing else happens, because
  enemies only act when attacked, and poison does not hurt on a drink turn.

## R6: Weapons

- R6.1 Weapons lie on floor tiles. There are three kinds, each with a
  different attack bonus: dagger `-` +1, sword `/` +3, axe `T` +5 (symbols
  changed in round 3, R8).
- R6.2 Moving onto a weapon's tile equips it automatically: it is removed from
  the map and its bonus is added to the player's attack.
- R6.3 Bonuses stack. The player's attack is 5 plus the sum of the bonuses of
  all weapons collected, including several of the same kind
  (e.g. dagger + sword = 5 + 1 + 3 = 9).
- R6.4 Weapons only change attack. They cannot be dropped or unequipped.

## R7: Levels

- R7.1 The game has 3 built-in levels, played in order. A new game starts on
  level 1 at that level's `@`.
- R7.2 Moving onto the exit of a level that is not the last one loads the
  next level: its walls, enemies and items replace the current ones, the
  player is placed on the new level's `@`, the level number goes up by 1, the
  status stays `playing`, and the message says which level was reached.
- R7.3 HP, potions carried and weapons collected (and so attack) carry over
  unchanged. HP is not restored between levels.
- R7.4 Items and enemies left behind on a level are gone; only what the player
  collected carries over.
- R7.5 (changed in round 5 by R11) Later levels are harder: more enemies,
  no more potions, and stronger enemies (R11). All enemies on one level have
  the same stats, and every enemy on every level poisons on hit (R10).
- R7.6 Every built-in level follows the map rules, and its exit can be reached
  from its `@` (walking through enemy tiles counts, since enemies can be killed).

## R8: Map symbols

- R8.1 No map symbol is one of the movement keys `w`, `a`, `s`, `d`, or the
  drink key `p`. The weapons use `-` (dagger), `/` (sword) and `T` (axe).
- R8.2 The built-in levels and the help text use the new symbols.
- R8.3 Saves store item kinds by name (`"sword"`), not by symbol, so no save
  format change is needed for R8.

## R9: Tougher enemies (round 4)

- R9.1 (changed in round 5 by R11) Level 1 enemies start with 12 HP instead
  of 8, and deal 3 damage. Enemies on later levels have more (R11).
- R9.2 So more hits are needed. Hits to kill an unhurt level 1 enemy, by attack:
  5 → 3 hits; 6, 8, 10 or 11 → 2 hits; 12 or more → 1 hit. The sword alone
  (Atk 8) and the axe alone (Atk 10) no longer kill in one hit; the sword and
  axe together (Atk 13) do.
- R9.3 Enemies in a round 3 save keep their saved HP (R4.5).

## R10: Poison (round 4)

- R10.1 Every enemy is poisonous. Whenever an enemy hits back (R2.3), the
  player is poisoned for 3 turns. An attack that kills the enemy causes no
  hit-back and so no poison.
- R10.2 At the start of each turn (see Turns) while poisoned, before the
  action is carried out, poison deals 1 damage and the turns left go down by
  1. At 0 turns left the poison wears off. The turn of the hit-back itself
  costs no poison damage; the next 3 turns cost 1 HP each.
- R10.3 Poison does not stack. A hit-back while already poisoned resets the
  turns left to 3 (after that turn's own poison damage).
- R10.4 If poison brings HP to 0, the game is `lost` and the action of that
  turn is not carried out (e.g. the player does not move).
- R10.5 Drinking a potion cures poison: it heals as in R5.2 and sets the
  turns left to 0, and poison does not hurt on that turn. A poisoned player
  at full HP may drink: the potion is used, heals 0 HP and cures the poison.
- R10.6 Things that are not turns (wall bumps, refused drinks, commands after
  game over, `save`/`load`/`help`/`quit`) do not make poison tick.
- R10.7 Poison carries over to the next level like HP (R7.3). Moving onto an
  exit is a turn, so poison ticks before the level changes or the game is won.
- R10.8 Poison turns left are saved and loaded (R4).

## R11: Difficulty rises by level (round 5)

- R11.1 Enemy stats by level number:

  | Level | Enemy HP | Enemy damage |
  |-------|----------|--------------|
  | 1     | 12       | 3            |
  | 2     | 16       | 3            |
  | 3     | 20       | 4            |

  A level past 3 (only possible in a custom game) uses the level 3 stats.
- R11.2 The stats go by the level's number in the game, not by which map it
  is: a game built from a single map is level 1, and the second map of any
  game built from several maps is level 2.
- R11.3 An enemy gets its stats when its level is loaded (a new game, or
  reaching the exit of the level before). Each enemy keeps its own HP and
  attack; both are saved and loaded with it (R4).
- R11.4 Poison is the same on every level: 1 damage for 3 turns (R10).
  Level 3 enemies also paralyse (R12).
- R11.5 Reaching a new level says how strong its enemies are, e.g.
  `Enemies here have 16 HP and hit for 3.` On a level whose enemies
  paralyse (R12), it adds `Their hits also paralyse you.`
- R11.6 Hits to kill an unhurt enemy are its HP divided by the player's
  attack, rounded up. Level 2 (16 HP): Atk 5 → 4 hits; 6 or 7 → 3; 8 to 15 →
  2; 16 or more → 1. Level 3 (20 HP): Atk 5 or 6 → 4 hits; 7 to 9 → 3; 10 to
  19 → 2; 20 or more → 1. The default game has at most Atk 15, so no level 2
  or 3 enemy dies in one hit there. On level 3 these counts assume every
  attack lands, i.e. the player is not paralysed (R12.4, changed in round 6).

## R12: Paralysis (round 6)

- R12.1 Only enemies on level 3 can paralyse. As with R11.2, this goes by
  the level number, so a level past 3 in a custom game also paralyses, and
  the level 3 map played on its own (level 1) does not. Each enemy gets this
  when its level is loaded and keeps it (saved per enemy, R4).
- R12.2 Whenever a paralysing enemy hits back (R2.3), the player is
  paralysed for 3 turns, as well as poisoned (R10.1). It does not stack: a
  new paralysing hit resets the turns left to 3. An attack that kills the
  enemy causes no hit-back and so no paralysis.
- R12.3 At the start of each turn (see Turns) while paralysed, after poison
  has ticked, the turns left go down by 1 and that turn is a paralysed turn.
  At 0 turns left the paralysis wears off. The turn of the hit-back itself is
  not one of the 3. If poison kills the player first, nothing else happens
  (R10.4).
- R12.4 On a paralysed turn, an attack has a 75% chance to fail: the enemy
  takes no damage and does not hit back, and the message says the player
  could not attack. The turn is still used. With the other 25%, the attack
  goes ahead as normal (and its hit-back can paralyse again). Moving,
  picking up items, reaching an exit and drinking are not affected.
- R12.5 Drinking a potion cures paralysis as well as poison, in one drink:
  it heals as in R5.2 and sets both turns left to 0. A paralysed player at
  full HP may drink: the potion is used, heals 0 HP and cures it (R5.4).
- R12.6 Paralysis carries over to the next level like HP (R7.3), is saved
  and loaded (R4), and is shown in the status line.
- R12.7 The roll comes from a random number generator held by the game, so
  tests can give it a fixed one. The generator's state is not saved: a loaded
  game gets a new one. An attack fails when the generator's `random()`
  returns a number below 0.75.

## Level 1 (the round 2 default map, new symbols)

```
###########
#@-.#....!#
#.#.#.###.#
#.#E..#E/.#
#.#####.#.#
#!..E...#.#
###.###.#E#
#T....#...#
#.###E#####
#...E..!.X#
###########
```

Six enemies, three potions, and one of each weapon.

## Level 2

```
###########
#@..E...#.#
#.###.#.#.#
#.#!..#E..#
#.#.###.###
#E..E.#..E#
###.#.#.#.#
#-..#E..#.#
#.#####.#E#
#..E..!.#X#
###########
```

Eight enemies, two potions, and a dagger.

## Level 3

```
#############
#@.E..#..E..#
#.###.#.###.#
#.#E..E...#.#
#.#.#####.#E#
#E..#!..E.#.#
###.#.###.#.#
#...E.....E.#
#.#######.###
#.E.....E..X#
#############
```

Eleven enemies, one potion, no weapons.

## Out of scope for round 6

Random maps, enemies that differ from each other on the same level (a
separate poison enemy type), poison that grows stronger by level, poison or
paralysis that stacks, paralysis that stops moving or drinking, a chance that
a level 3 hit-back does not paralyse, separate cures for poison and
paralysis, saving the random generator's state, other status effects, enemy HP shown on the map, healing between levels,
going back to an earlier level, enemy movement, dropping or swapping weapons,
items other than potions and the three weapons, defense or max-HP stats,
single-keypress input, colour, and named save slots.
