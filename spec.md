# Spec: Terminal Dungeon Crawler (round 3)

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
"Enemies left" counts the current level only.

## R1: Movement on a grid

- R1.1 A move command moves the player one tile in that direction if the
  target tile is floor (an item on the floor does not block movement).
- R1.2 Walls block movement. The player stays put, gets a message, and the
  game state does not change.
- R1.3 Moving off the edge of the grid is blocked in the same way as a wall.
- R1.4 Keyboard commands map to directions: `w` up, `s` down, `a` left, `d` right.

## R2: Enemies, health and damage

Combat is "bump to attack" and has no randomness:

- The player starts with 20 HP (also the maximum HP) and a base attack of 5.
  The player's attack is the base attack plus every weapon bonus (R6).
- Each enemy starts with 8 HP and deals 3 damage per attack.
- R2.1 Moving into an enemy's tile attacks it instead of moving. The enemy
  loses HP equal to the player's attack.
- R2.2 If the enemy's HP drops to 0 or below, it is removed from the map. The
  player stays on their original tile and can step into the freed tile next turn.
- R2.3 If the enemy survives, it hits back right away. The player loses HP
  equal to the enemy's attack.
- R2.4 Enemies do not move. Each enemy keeps its own HP between attacks.
- HP is never shown below 0. It is clamped to 0.

## R3: Winning and losing (changed in round 3)

- R3.1 When the player moves onto the exit tile of the **last** level, the
  game ends with status `won`. Reaching the exit of any earlier level is not a
  win: the player goes on to the next level (R7.2). A game built from a single
  map has one level, so its exit wins.
- R3.2 When the player's HP reaches 0, the game ends with status `lost`.
- R3.3 Once the game is over (`won` or `lost`), move and drink commands change
  nothing and return a "game over" message. The terminal program prints the
  result and exits.
- While the game is still going, its status is `playing`.

## R4: Save and load

- R4.1 Saving writes the full game state (current level's map, level number,
  the maps of the levels still to come, player position, HP, potions carried
  and weapons collected, every enemy's position and HP, every item still on
  the map, status) to a JSON file.
- R4.2 Loading that file restores a game equal to the one that was saved, so
  play continues exactly where it left off.
- R4.3 Loading a missing, unreadable or malformed file raises `SaveError`
  with a readable message. In the terminal program, the current game keeps
  going unchanged. Besides the round 1 checks, a save is malformed if: HP is
  above the maximum; the potion count is negative or not an integer; a weapon
  name is unknown; an item has an unknown kind, is not on a floor tile, or
  shares a tile with another item, an enemy or the player. Round 3 adds: the
  level number is not an integer of 1 or more; `next_levels` is not a list of
  maps that each pass the map rules above.
- R4.4 The program can be started from a save: `py -m dungeon --load`.
- R4.5 The save file has `"version": 3`. Older saves still load:
  - A round 2 save (`"version": 2`) becomes level 1, followed by levels 2 and
    3 of the built-in levels. A round 2 save whose status is `won` stays won
    and gets no further levels.
  - A round 1 save (`"version": 1`) is first upgraded to version 2 (0 potions,
    no weapons, no items on the map), then as above.
  - Any other version is rejected with `SaveError`.

Version 3 layout (`map` is the current level with only `#`, `.` and `X`;
`next_levels` holds the full text maps, with `@`, enemies and items, of the
levels still to come, in order):

```json
{
  "version": 3,
  "level": 1,
  "map": ["#####", "#...#", "####X"],
  "next_levels": [["@.X"]],
  "player": {"row": 1, "col": 1, "hp": 17, "potions": 0, "weapons": ["sword"]},
  "enemies": [{"row": 1, "col": 2, "hp": 3}],
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
  maximum of 20.
- R5.3 Drinking with no potions does nothing except return a message.
- R5.4 Drinking at full HP (20) is refused: the potion is kept and a message
  is returned.
- R5.5 Drinking takes the player's turn but nothing else happens, because
  enemies only act when attacked.

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
- R7.5 Every enemy has the same stats on every level (8 HP, 3 damage). Later
  levels are harder through more enemies and fewer potions.
- R7.6 Every built-in level follows the map rules, and its exit can be reached
  from its `@` (walking through enemy tiles counts, since enemies can be killed).

## R8: Map symbols

- R8.1 No map symbol is one of the movement keys `w`, `a`, `s`, `d`, or the
  drink key `p`. The weapons use `-` (dagger), `/` (sword) and `T` (axe).
- R8.2 The built-in levels and the help text use the new symbols.
- R8.3 Saves store item kinds by name (`"sword"`), not by symbol, so no save
  format change is needed for R8.

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

## Out of scope for round 3

Random maps, stronger enemies on later levels, healing between levels,
going back to an earlier level, enemy movement, dropping or swapping weapons,
items other than potions and the three weapons, defense or max-HP stats,
single-keypress input, colour, and named save slots.
