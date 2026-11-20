# Spec: Terminal Dungeon Crawler (round 2)

A short, turn-based dungeon game that runs in a terminal. One game should take
a few minutes. Python 3.12, standard library only (pytest for tests).

## Map

The dungeon is a fixed, hand-made grid written as text:

| Char | Meaning |
|------|---------|
| `#`  | Wall, which cannot be entered |
| `.`  | Floor |
| `@`  | Player start (floor underneath) |
| `E`  | Enemy (floor underneath) |
| `X`  | Exit |
| `!`  | Potion (floor underneath) |
| `d`  | Dagger, Atk +1 (floor underneath) |
| `s`  | Sword, Atk +3 (floor underneath) |
| `a`  | Axe, Atk +5 (floor underneath) |

Positions are `(row, col)`, with `(0, 0)` at the top left. Every map must contain
exactly one `@` and exactly one `X`, and all rows must have the same length.
Any other map is rejected with a `ValueError`.

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
`HP: 17/20   Atk: 8   Potions: 1   Weapons: sword   Enemies left: 5`.

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

## R3: Winning and losing

- R3.1 When the player moves onto the exit tile, the game ends with status `won`.
- R3.2 When the player's HP reaches 0, the game ends with status `lost`.
- R3.3 Once the game is over (`won` or `lost`), move and drink commands change
  nothing and return a "game over" message. The terminal program prints the
  result and exits.
- While the game is still going, its status is `playing`.

## R4: Save and load

- R4.1 Saving writes the full game state (map, player position, HP, potions
  carried and weapons collected, every enemy's position and HP, every item
  still on the map, status) to a JSON file.
- R4.2 Loading that file restores a game equal to the one that was saved, so
  play continues exactly where it left off.
- R4.3 Loading a missing, unreadable or malformed file raises `SaveError`
  with a readable message. In the terminal program, the current game keeps
  going unchanged. Besides the round 1 checks, a save is malformed if: HP is
  above the maximum; the potion count is negative or not an integer; a weapon
  name is unknown; an item has an unknown kind, is not on a floor tile, or
  shares a tile with another item, an enemy or the player.
- R4.4 The program can be started from a save: `py -m dungeon --load`.
- R4.5 The save file has `"version": 2`. A round 1 save (`"version": 1`) still
  loads: it becomes a game with 0 potions, no weapons and no items on the map.
  Any other version is rejected with `SaveError`.

Version 2 layout:

```json
{
  "version": 2,
  "map": ["#####", "#...#", "####X"],
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
  different attack bonus: dagger `d` +1, sword `s` +3, axe `a` +5.
- R6.2 Moving onto a weapon's tile equips it automatically: it is removed from
  the map and its bonus is added to the player's attack.
- R6.3 Bonuses stack. The player's attack is 5 plus the sum of the bonuses of
  all weapons collected, including several of the same kind
  (e.g. dagger + sword = 5 + 1 + 3 = 9).
- R6.4 Weapons only change attack. They cannot be dropped or unequipped.

## Default map

```
###########
#@d.#....!#
#.#.#.###.#
#.#E..#Es.#
#.#####.#.#
#!..E...#.#
###.###.#E#
#a....#...#
#.###E#####
#...E..!.X#
###########
```

Six enemies, three potions, and one of each weapon.

## Out of scope for round 2

Random maps, multiple levels, enemy movement, dropping or swapping weapons,
items other than potions and the three weapons, defense or max-HP stats,
single-keypress input, colour, and named save slots.
