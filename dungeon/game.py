"""Game logic for the dungeon crawler: map, movement, combat, win/loss, save/load.

Nothing in this module reads input or prints; the terminal front end lives in cli.py.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

WALL, FLOOR, EXIT, PLAYER, ENEMY = "#", ".", "X", "@", "E"

POTION = "potion"
# Attack bonus of each weapon kind (R6).
WEAPONS = {"dagger": 1, "sword": 3, "axe": 5}
# Map character for each item kind.
ITEM_CHARS = {"!": POTION, "d": "dagger", "s": "sword", "a": "axe"}
ITEM_KINDS = set(ITEM_CHARS.values())

PLAYER_START_HP = 20
PLAYER_MAX_HP = PLAYER_START_HP
POTION_HEAL = 10
PLAYER_ATTACK = 5
ENEMY_START_HP = 8
ENEMY_ATTACK = 3

SAVE_VERSION = 2
GAME_OVER = "Game over. Start a new game or load a save."
STATUSES = ("playing", "won", "lost")

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

DEFAULT_MAP = [
    "###########",
    "#@d.#....!#",
    "#.#.#.###.#",
    "#.#E..#Es.#",
    "#.#####.#.#",
    "#!..E...#.#",
    "###.###.#E#",
    "#a....#...#",
    "#.###E#####",
    "#...E..!.X#",
    "###########",
]


class SaveError(Exception):
    """A save file could not be read or does not hold a valid game."""


@dataclass
class Enemy:
    pos: tuple[int, int]
    hp: int = ENEMY_START_HP


@dataclass
class Item:
    """Something lying on a floor tile that the player picks up by stepping on it."""

    pos: tuple[int, int]
    kind: str


@dataclass
class Game:
    """Complete state of one game. `tiles` holds only walls, floor and the exit."""

    tiles: list[str]
    player: tuple[int, int]
    player_hp: int = PLAYER_START_HP
    enemies: list[Enemy] = field(default_factory=list)
    status: str = "playing"
    potions: int = 0
    weapons: list[str] = field(default_factory=list)
    items: list[Item] = field(default_factory=list)

    @classmethod
    def from_map(cls, lines: list[str]) -> Game:
        """Build a new game from a text map (see spec.md for the legend)."""
        if not lines or len({len(row) for row in lines}) != 1:
            raise ValueError("map must be non-empty and rectangular")
        players, exits, enemies, items, tiles = [], [], [], [], []
        for r, row in enumerate(lines):
            clean = []
            for c, ch in enumerate(row):
                if ch == PLAYER:
                    players.append((r, c))
                    ch = FLOOR
                elif ch == ENEMY:
                    enemies.append(Enemy((r, c)))
                    ch = FLOOR
                elif ch in ITEM_CHARS:
                    items.append(Item((r, c), ITEM_CHARS[ch]))
                    ch = FLOOR
                elif ch == EXIT:
                    exits.append((r, c))
                elif ch not in (WALL, FLOOR):
                    raise ValueError(f"unknown map character {ch!r} at {(r, c)}")
                clean.append(ch)
            tiles.append("".join(clean))
        if len(players) != 1 or len(exits) != 1:
            raise ValueError("map needs exactly one '@' and one 'X'")
        return cls(tiles=tiles, player=players[0], enemies=enemies, items=items)

    @property
    def height(self) -> int:
        return len(self.tiles)

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    @property
    def attack(self) -> int:
        """Base attack plus the bonus of every weapon collected (bonuses stack)."""
        return PLAYER_ATTACK + sum(WEAPONS[w] for w in self.weapons)

    def tile_at(self, pos: tuple[int, int]) -> str:
        """Tile at pos; anything outside the grid counts as wall."""
        r, c = pos
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.tiles[r][c]
        return WALL

    def enemy_at(self, pos: tuple[int, int]) -> Enemy | None:
        return next((e for e in self.enemies if e.pos == pos), None)

    def item_at(self, pos: tuple[int, int]) -> Item | None:
        return next((i for i in self.items if i.pos == pos), None)

    def move(self, direction: str) -> str:
        """Try to move the player one tile. Returns a message describing the result."""
        if self.status != "playing":
            return GAME_OVER
        dr, dc = DIRECTIONS[direction]
        target = (self.player[0] + dr, self.player[1] + dc)
        if self.tile_at(target) == WALL:
            return "A wall blocks your way."
        enemy = self.enemy_at(target)
        if enemy is not None:
            return self._attack(enemy)
        self.player = target
        if self.tile_at(target) == EXIT:
            self.status = "won"
            return "You reach the exit. You win!"
        message = f"You move {direction}."
        item = self.item_at(target)
        if item is not None:
            message += " " + self._pick_up(item)
        return message

    def _pick_up(self, item: Item) -> str:
        """Collect the item the player is standing on."""
        self.items.remove(item)
        if item.kind == POTION:
            self.potions += 1
            return f"You pick up a potion (potions: {self.potions})."
        self.weapons.append(item.kind)
        return f"You equip a {item.kind}: Atk +{WEAPONS[item.kind]} (Atk {self.attack})."

    def drink(self) -> str:
        """Drink one potion: heal POTION_HEAL HP, never above PLAYER_MAX_HP."""
        if self.status != "playing":
            return GAME_OVER
        if self.potions == 0:
            return "You have no potions."
        if self.player_hp >= PLAYER_MAX_HP:
            return "You are already at full health. You keep the potion."
        healed = min(POTION_HEAL, PLAYER_MAX_HP - self.player_hp)
        self.player_hp += healed
        self.potions -= 1
        return f"You drink a potion and heal {healed} HP (HP {self.player_hp}/{PLAYER_MAX_HP})."

    def _attack(self, enemy: Enemy) -> str:
        """Bump attack: hit the enemy; if it survives it hits back."""
        damage = self.attack
        enemy.hp -= damage
        if enemy.hp <= 0:
            self.enemies.remove(enemy)
            return f"You hit the enemy for {damage} and defeat it!"
        self.player_hp = max(0, self.player_hp - ENEMY_ATTACK)
        message = (
            f"You hit the enemy for {damage} (enemy HP {enemy.hp}). "
            f"It hits back for {ENEMY_ATTACK}."
        )
        if self.player_hp == 0:
            self.status = "lost"
            message += " You have fallen. You lost!"
        return message

    def to_dict(self) -> dict:
        return {
            "version": SAVE_VERSION,
            "map": list(self.tiles),
            "player": {
                "row": self.player[0],
                "col": self.player[1],
                "hp": self.player_hp,
                "potions": self.potions,
                "weapons": list(self.weapons),
            },
            "enemies": [{"row": e.pos[0], "col": e.pos[1], "hp": e.hp} for e in self.enemies],
            "items": [{"row": i.pos[0], "col": i.pos[1], "kind": i.kind} for i in self.items],
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: object) -> Game:
        """Rebuild a game from to_dict() output. Raises SaveError if invalid.

        Version 1 saves (round 1, no items) are upgraded to the current version.
        """
        if isinstance(data, dict) and data.get("version") == 1:
            data = _upgrade_v1(data)
        try:
            if not isinstance(data, dict) or data.get("version") != SAVE_VERSION:
                raise SaveError("unsupported or missing save version")
            tiles = data["map"]
            if (
                not isinstance(tiles, list)
                or not tiles
                or not all(isinstance(row, str) for row in tiles)
                or len({len(row) for row in tiles}) != 1
                or any(ch not in (WALL, FLOOR, EXIT) for row in tiles for ch in row)
                or sum(row.count(EXIT) for row in tiles) != 1
            ):
                raise SaveError("save map is malformed")
            p = data["player"]
            game = cls(
                tiles=list(tiles),
                player=(_int(p["row"]), _int(p["col"])),
                player_hp=_int(p["hp"]),
                enemies=[
                    Enemy((_int(e["row"]), _int(e["col"])), _int(e["hp"]))
                    for e in data["enemies"]
                ],
                status=data["status"],
                potions=_int(p["potions"]),
                weapons=_str_list(p["weapons"]),
                items=[Item((_int(i["row"]), _int(i["col"])), _str(i["kind"])) for i in data["items"]],
            )
        except (KeyError, TypeError) as exc:
            raise SaveError(f"save data is incomplete: {exc!r}") from exc
        if game.status not in STATUSES:
            raise SaveError(f"unknown status {game.status!r}")
        if game.tile_at(game.player) == WALL or not 0 <= game.player_hp <= PLAYER_MAX_HP:
            raise SaveError("player position or HP is invalid")
        if game.potions < 0:
            raise SaveError("potion count is invalid")
        if any(w not in WEAPONS for w in game.weapons):
            raise SaveError("unknown weapon in save")
        for enemy in game.enemies:
            if game.tile_at(enemy.pos) != FLOOR or enemy.hp <= 0 or enemy.pos == game.player:
                raise SaveError("enemy position or HP is invalid")
        taken = {game.player} | {e.pos for e in game.enemies}
        for item in game.items:
            if item.kind not in ITEM_KINDS or game.tile_at(item.pos) != FLOOR or item.pos in taken:
                raise SaveError("item kind or position is invalid")
            taken.add(item.pos)
        return game


def _upgrade_v1(data: dict) -> dict:
    """Turn a round 1 save into a version 2 save: no potions, weapons or items."""
    data = dict(data, version=SAVE_VERSION, items=[])
    if isinstance(data.get("player"), dict):
        data["player"] = dict(data["player"], potions=0, weapons=[])
    return data


def _str(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(f"expected a string, got {value!r}")
    return value


def _str_list(value: object) -> list[str]:
    if not isinstance(value, list):
        raise TypeError(f"expected a list of strings, got {value!r}")
    return [_str(v) for v in value]


def _int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"expected an integer, got {value!r}")
    return value


def save_game(game: Game, path: str | os.PathLike) -> None:
    """Write the game to path as JSON. Writes a temp file first so a crash cannot corrupt an old save."""
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(game.to_dict(), indent=2), encoding="utf-8")
    os.replace(tmp, path)


def load_game(path: str | os.PathLike) -> Game:
    """Read a game saved by save_game. Raises SaveError on any problem."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SaveError(f"no save file at {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SaveError(f"could not read save file: {exc}") from exc
    return Game.from_dict(data)
