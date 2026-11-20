# Dungeon Crawler

A short, turn-based dungeon game for the terminal, built for a quick break.
Walk through a hand-made grid dungeon, fight enemies by walking into them, and
reach the exit before your health runs out. You can save at any time and pick
up again later.

```
###########
#@..#.....#     @  you        E  enemy
#.#.#.###.#     #  wall       X  exit
#.#E..#E..#     .  floor
...
HP: 20   Enemies left: 6
>
```

Type a command and press Enter:

| Command | Effect |
|---------|--------|
| `w` `a` `s` `d` | Move up / left / down / right. Walking into an enemy attacks it. |
| `save` / `load` | Save to or load from `savegame.json` |
| `help` / `quit` | Show the commands / leave without saving |

You start with 20 HP and deal 5 damage. Enemies have 8 HP and deal 3 damage
each time they survive one of your hits. Reach `X` to win. If your HP hits 0, you lose.

## Run it

Requires Python 3.10+ (developed on 3.12). The game itself has no dependencies.

```
py -m dungeon            # new game
py -m dungeon --load     # continue from savegame.json
```

## Run the tests

```
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements-dev.txt
py -m pytest
```

Each test names the requirement (R1-R4 in `problem.md`) it checks. The detailed
rules are in `spec.md`.
