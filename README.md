# Dungeon Crawler

A short, turn-based dungeon game for the terminal, built for a quick break.
Walk through three hand-made dungeon levels, fight enemies by walking into
them, and reach the exit of the last level before your health runs out. Pick up potions to heal and
weapons to hit harder. You can save at any time and pick up again later.

```
###########
#@-.#....!#     @  you        E  enemy      !  potion
#.#.#.###.#     #  wall       X  exit       -  dagger (Atk +1)
#.#E..#E/.#     .  floor                    /  sword  (Atk +3)
...                                         T  axe    (Atk +5)
Level: 1/3   HP: 20/20   Atk: 5   Potions: 0   Weapons: none   Enemies left: 6
>
```

Type a command and press Enter:

| Command | Effect |
|---------|--------|
| `w` `a` `s` `d` | Move up / left / down / right. Walking into an enemy attacks it. |
| `p` / `drink` | Drink a potion: heals 10 HP, up to the maximum of 20, and cures poison and paralysis |
| `save` / `load` | Save to or load from `savegame.json` |
| `help` / `quit` | Show the commands / leave without saving |

You start with 20 HP and deal 5 damage. Enemies get tougher on each level:
12 HP on level 1, 16 HP on level 2, and 20 HP on level 3. They deal 3 damage
(4 on level 3) each time they survive one of your hits. That hit also poisons you: each of
your next 3 moves or attacks costs 1 HP (another hit resets it to 3; a potion
cures it). The status line shows `Poisoned: n turns` while it lasts. Level 3 enemies
also paralyse you: for your next 3 turns, each attack has a 75% chance to fail
(the enemy doesn't hit back then). Walking and drinking still work, and the same
potion cures it. The status line shows `Paralysed: n turns`. Walking onto a potion picks it up.
Walking onto a weapon equips it and adds its bonus to your attack; bonuses
stack. Reaching `X` takes you down to the next level, keeping your HP,
potions and weapons (HP is not restored). Each level has more enemies and
fewer potions. Reach `X` on level 3 to win. If your HP hits 0, you lose.

Saves from earlier versions of the game still load. Round 5 saves start
unparalysed, and enemies on a saved level 3 paralyse. Round 4 saves keep
their enemies' saved HP, and those enemies hit for their level's damage.
Round 3 saves start unpoisoned and keep their enemies' saved HP. Older saves' map becomes level 1,
followed by levels 2 and 3. Saves from the first version start with no potions
or weapons and no items on the map.

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

Each test names the requirement (R1-R12 in `problem.md`) it checks. The detailed
rules are in `spec.md`.
