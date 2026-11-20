"""Tests for R1: move through a grid-based dungeon using keyboard commands."""
import pytest

from dungeon.cli import parse_command
from dungeon.game import Game

OPEN_MAP = [
    "#####",
    "#...#",
    "#.@.#",
    "#...#",
    "####X",
]


@pytest.mark.parametrize(
    "direction, expected",
    [("up", (1, 2)), ("down", (3, 2)), ("left", (2, 1)), ("right", (2, 3))],
)
def test_r1_move_onto_floor(direction, expected):
    """R1.1: a move onto floor moves the player one tile."""
    game = Game.from_map(OPEN_MAP)
    game.move(direction)
    assert game.player == expected


def test_r1_wall_blocks_movement():
    """R1.2: walls block movement and leave the state unchanged."""
    game = Game.from_map(["#####", "#@..#", "####X"])
    before = game.to_dict()
    message = game.move("up")
    assert game.player == (1, 1)
    assert game.to_dict() == before
    assert "wall" in message.lower()


def test_r1_grid_edge_blocks_movement():
    """R1.3: moving off the grid edge is blocked like a wall."""
    game = Game.from_map(["@.X"])
    game.move("up")
    game.move("left")
    assert game.player == (0, 0)


def test_r1_several_moves_follow_a_path():
    """R1.1: consecutive moves accumulate on the grid."""
    game = Game.from_map(OPEN_MAP)
    for direction in ["up", "left", "down", "down"]:
        game.move(direction)
    assert game.player == (3, 1)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("w", ("move", "up")),
        ("s", ("move", "down")),
        ("a", ("move", "left")),
        ("d", ("move", "right")),
        ("  D  ", ("move", "right")),
        ("save", ("save", None)),
        ("LOAD", ("load", None)),
        ("quit", ("quit", None)),
        ("help", ("help", None)),
        ("jump", ("unknown", None)),
        ("", ("unknown", None)),
    ],
)
def test_r1_keyboard_commands_map_to_actions(text, expected):
    """R1.4: typed keyboard commands map to directions and actions."""
    assert parse_command(text) == expected
