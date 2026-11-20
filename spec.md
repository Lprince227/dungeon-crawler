# Spec: Terminal Dungeon Crawler (round 1)

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

Positions are `(row, col)`, with `(0, 0)` at the top left. Every map must contain
exactly one `@` and exactly one `X`, and all rows must have the same length.
Any other map is rejected with a `ValueError`.

## Input

The player types a command and presses Enter. Commands are case-insensitive
and surrounding spaces are ignored.

| Command | Effect |
|---------|--------|
| `w` / `a` / `s` / `d` | Move up / left / down / right by one tile |
| `save`  | Save the game to `savegame.json` |
| `load`  | Replace the current game with the one in `savegame.json` |
| `help`  | Show the command list |
| `quit`  | Leave the game without saving |

An unknown command prints a short hint and changes nothing.

## R1: Movement on a grid

- R1.1 A move command moves the player one tile in that direction if the
  target tile is floor.
- R1.2 Walls block movement. The player stays put, gets a message, and the
  game state does not change.
- R1.3 Moving off the edge of the grid is blocked in the same way as a wall.
- R1.4 Keyboard commands map to directions: `w` up, `s` down, `a` left, `d` right.

## R2: Enemies, health and damage

Combat is "bump to attack" and has no randomness:

- The player starts with 20 HP and deals 5 damage per attack.
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
- R3.3 Once the game is over (`won` or `lost`), move commands change nothing
  and return a "game over" message. The terminal program prints the result
  and exits.
- While the game is still going, its status is `playing`.

## R4: Save and load

- R4.1 Saving writes the full game state (map, player position and HP, every
  enemy's position and HP, status) to a JSON file.
- R4.2 Loading that file restores a game equal to the one that was saved, so
  play continues exactly where it left off.
- R4.3 Loading a missing, unreadable or malformed file raises `SaveError`
  with a readable message. In the terminal program, the current game keeps
  going unchanged.
- R4.4 The program can be started from a save: `py -m dungeon --load`.
- The save file includes a `"version": 1` field so the format can change later.

## Out of scope for round 1

Random maps, multiple levels, items, enemy movement, single-keypress input,
colour, and named save slots.
