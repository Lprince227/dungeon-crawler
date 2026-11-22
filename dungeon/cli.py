"""Terminal front end: reads typed commands, prints the map and messages."""
from __future__ import annotations

import argparse
import sys

from dungeon.game import (
    ENEMY,
    ITEM_CHARS,
    LEVELS,
    PLAYER,
    PLAYER_MAX_HP,
    Game,
    SaveError,
    load_game,
    save_game,
)

KEYS = {"w": "up", "s": "down", "a": "left", "d": "right"}
ACTIONS = {"save", "load", "quit", "help", "drink"}
ALIASES = {"p": "drink"}
SAVE_FILE = "savegame.json"
ITEM_SYMBOLS = {kind: char for char, kind in ITEM_CHARS.items()}


def parse_command(text: str) -> tuple[str, str | None]:
    """Turn typed input into (action, argument), e.g. 'w' -> ('move', 'up')."""
    word = text.strip().lower()
    if word in KEYS:
        return ("move", KEYS[word])
    word = ALIASES.get(word, word)
    if word in ACTIONS:
        return (word, None)
    return ("unknown", None)


HELP = """Commands (type, then press Enter):
  w / a / s / d   move up / left / down / right (walk into an enemy to attack)
  p / drink       drink a potion (heals 10 HP, up to 20, and cures poison)
  save            save to savegame.json
  load            load savegame.json
  help            show this list
  quit            leave without saving
Walk over ! to pick up a potion. Walk over a weapon to equip it:
  - dagger (Atk +1)   / sword (Atk +3)   T axe (Atk +5)
Weapon bonuses stack.
Enemies have 12 HP. When one survives your hit it hits back for 3 and poisons
you: you lose 1 HP on each of your next 3 moves. A potion cures poison.
Reach X to go down to the next level. HP, potions and weapons come with you.
Reach X on the last level to win. If your HP hits 0 you lose."""


def render(game: Game) -> str:
    """Draw the map with items, enemies and the player on top of the tiles."""
    rows = [list(row) for row in game.tiles]
    for item in game.items:
        rows[item.pos[0]][item.pos[1]] = ITEM_SYMBOLS[item.kind]
    for enemy in game.enemies:
        rows[enemy.pos[0]][enemy.pos[1]] = ENEMY
    rows[game.player[0]][game.player[1]] = PLAYER
    grid = "\n".join("".join(row) for row in rows)
    status = (
        f"Level: {game.level}/{game.total_levels}   HP: {game.player_hp}/{PLAYER_MAX_HP}   Atk: {game.attack}   "
        f"Potions: {game.potions}   Weapons: {', '.join(game.weapons) or 'none'}   "
        f"Enemies left: {len(game.enemies)}"
    )
    if game.poison:
        status += f"   Poisoned: {game.poison} turn{'s' if game.poison != 1 else ''}"
    return f"{grid}\n{status}"


def run(game: Game, save_path: str = SAVE_FILE, read=input, write=print) -> Game:
    """Main loop. Returns the final game when it ends or the player quits."""
    write(HELP)
    while True:
        write("")
        write(render(game))
        if game.status != "playing":
            write("*** You win! ***" if game.status == "won" else "*** You lost. ***")
            return game
        try:
            action, arg = parse_command(read("> "))
        except EOFError:
            return game
        if action == "move":
            write(game.move(arg))
        elif action == "drink":
            write(game.drink())
        elif action == "save":
            try:
                save_game(game, save_path)
                write(f"Game saved to {save_path}.")
            except OSError as exc:
                write(f"Could not save: {exc}")
        elif action == "load":
            try:
                game = load_game(save_path)
                write(f"Loaded {save_path}.")
            except SaveError as exc:
                write(f"Could not load: {exc}")
        elif action == "help":
            write(HELP)
        elif action == "quit":
            write("Bye!")
            return game
        else:
            write("Unknown command. Type 'help' for the list.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="A short terminal dungeon crawler.")
    parser.add_argument("--load", action="store_true", help=f"start from {SAVE_FILE}")
    args = parser.parse_args(argv)
    game = Game.from_levels(LEVELS)
    if args.load:
        try:
            game = load_game(SAVE_FILE)
        except SaveError as exc:
            print(f"Could not load: {exc}", file=sys.stderr)
            return 1
    run(game)
    return 0
