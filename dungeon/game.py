"""Game logic for the dungeon crawler: map, movement, combat, win/loss, save/load.

Nothing in this module reads input or prints; the terminal front end lives in cli.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

WALL, FLOOR, EXIT, PLAYER, ENEMY = "#", ".", "X", "@", "E"

DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

DEFAULT_MAP = [
    "###########",
    "#@..#.....#",
    "#.#.#.###.#",
    "#.#E..#E..#",
    "#.#####.#.#",
    "#...E...#.#",
    "###.###.#E#",
    "#.....#...#",
    "#.###E#####",
    "#...E....X#",
    "###########",
]


@dataclass
class Game:
    """Complete state of one game. `tiles` holds only walls, floor and the exit."""

    tiles: list[str]
    player: tuple[int, int]
    status: str = "playing"

    @classmethod
    def from_map(cls, lines: list[str]) -> Game:
        """Build a new game from a text map (see spec.md for the legend)."""
        if not lines or len({len(row) for row in lines}) != 1:
            raise ValueError("map must be non-empty and rectangular")
        players, exits, tiles = [], [], []
        for r, row in enumerate(lines):
            clean = []
            for c, ch in enumerate(row):
                if ch == PLAYER:
                    players.append((r, c))
                    ch = FLOOR
                elif ch == EXIT:
                    exits.append((r, c))
                elif ch not in (WALL, FLOOR):
                    raise ValueError(f"unknown map character {ch!r} at {(r, c)}")
                clean.append(ch)
            tiles.append("".join(clean))
        if len(players) != 1 or len(exits) != 1:
            raise ValueError("map needs exactly one '@' and one 'X'")
        return cls(tiles=tiles, player=players[0])

    @property
    def height(self) -> int:
        return len(self.tiles)

    @property
    def width(self) -> int:
        return len(self.tiles[0])

    def tile_at(self, pos: tuple[int, int]) -> str:
        """Tile at pos; anything outside the grid counts as wall."""
        r, c = pos
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.tiles[r][c]
        return WALL

    def move(self, direction: str) -> str:
        """Try to move the player one tile. Returns a message describing the result."""
        dr, dc = DIRECTIONS[direction]
        target = (self.player[0] + dr, self.player[1] + dc)
        if self.tile_at(target) == WALL:
            return "A wall blocks your way."
        self.player = target
        return f"You move {direction}."

    def to_dict(self) -> dict:
        return {
            "version": 1,
            "map": list(self.tiles),
            "player": {"row": self.player[0], "col": self.player[1]},
            "status": self.status,
        }
