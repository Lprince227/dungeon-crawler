"""Tests for R7: several levels in a row, with HP, potions and weapons carried over."""
from collections import deque

import pytest

from dungeon.game import (
    DEFAULT_MAP,
    ENEMY_ATTACK,
    ENEMY_START_HP,
    LEVELS,
    WALL,
    Game,
    Item,
)

TWO_LEVELS = [
    ["@!-X", "E..."],
    ["....", ".E!@", "X..."],
]


def test_r7_there_are_three_built_in_levels():
    """R7.1: the game has 3 built-in levels and level 1 is the round 2 default map."""
    assert len(LEVELS) == 3
    assert LEVELS[0] == DEFAULT_MAP


def test_r7_new_game_starts_on_level_1():
    """R7.1: a new game from the built-in levels starts on level 1 of 3 at level 1's '@'."""
    game = Game.from_levels(LEVELS)
    first = Game.from_map(LEVELS[0])
    assert game.level == 1
    assert game.total_levels == 3
    assert game.next_levels == [list(m) for m in LEVELS[1:]]
    assert (game.tiles, game.player, game.enemies, game.items) == (
        first.tiles, first.player, first.enemies, first.items
    )
    assert game.status == "playing"


def test_r7_from_levels_needs_at_least_one_level():
    """R7.1: building a game from no levels is an error."""
    with pytest.raises(ValueError):
        Game.from_levels([])


def test_r7_from_levels_rejects_a_bad_later_level():
    """R7.6: every level is checked when the game is built, not only the first."""
    with pytest.raises(ValueError):
        Game.from_levels([["@X"], ["..X"]])


def test_r7_single_map_game_has_one_level():
    """R7.1/R3.1: Game.from_map is a one-level game."""
    game = Game.from_map(["@X"])
    assert (game.level, game.total_levels, game.next_levels) == (1, 1, [])


def test_r7_exit_of_earlier_level_loads_next_level():
    """R7.2: reaching the exit of level 1 loads level 2 and puts the player on its '@'."""
    game = Game.from_levels(TWO_LEVELS)
    game.move("right")
    game.move("right")
    message = game.move("right")
    assert game.status == "playing"
    assert game.level == 2
    assert game.next_levels == []
    assert game.tiles == ["....", "....", "X..."]
    assert game.player == (1, 3)
    assert [e.pos for e in game.enemies] == [(1, 1)]
    assert game.items == [Item((1, 2), "potion")]
    assert "level 2" in message.lower()


def test_r7_stats_and_items_carry_over():
    """R7.3: HP, potions and weapons (and so attack) are unchanged by the level change."""
    game = Game.from_levels(TWO_LEVELS)
    game.player_hp = 7
    game.move("right")  # potion
    game.move("right")  # dagger
    game.move("right")  # exit -> level 2
    assert game.level == 2
    assert game.player_hp == 7
    assert game.potions == 1
    assert game.weapons == ["dagger"]
    assert game.attack == 6


def test_r7_hp_is_not_restored_between_levels():
    """R7.3: a hurt player stays hurt on the next level."""
    game = Game.from_levels([["@.X"], ["@X"]])
    game.player_hp = 4
    game.move("right")
    game.move("right")
    assert game.level == 2
    assert game.player_hp == 4


def test_r7_things_left_behind_do_not_carry_over():
    """R7.4: an item and an enemy left on level 1 are gone on level 2."""
    game = Game.from_levels([["@X", "!E"], ["@.X"]])
    game.move("right")
    assert game.level == 2
    assert game.items == []
    assert game.enemies == []
    assert game.potions == 0


def test_r7_enemies_on_later_levels_have_the_same_stats():
    """R7.5: an enemy on level 2 has 8 HP and hits back for 3."""
    game = Game.from_levels([["@X"], ["@E.X"]])
    game.move("right")
    assert game.enemies[0].hp == ENEMY_START_HP
    game.move("right")
    assert game.enemies[0].hp == ENEMY_START_HP - 5
    assert game.player_hp == 20 - ENEMY_ATTACK


def test_r7_full_run_through_three_levels():
    """R7.2/R3.1: three exits in a row: two level changes, then a win."""
    game = Game.from_levels([["@X"], ["@X"], ["@X"]])
    game.move("right")
    assert (game.level, game.status) == (2, "playing")
    game.move("right")
    assert (game.level, game.status) == (3, "playing")
    game.move("right")
    assert (game.level, game.status) == (3, "won")


def test_r7_from_levels_does_not_share_lists_with_its_input():
    """R7.2: playing through a game does not change the level list it was built from."""
    levels = [["@X"], ["@X"]]
    game = Game.from_levels(levels)
    game.move("right")
    assert levels == [["@X"], ["@X"]]
    assert Game.from_levels(LEVELS).next_levels == [list(m) for m in LEVELS[1:]]


def _exit_reachable(lines):
    """BFS from '@' over every non-wall tile (enemies can be killed, so they don't block)."""
    cells = {(r, c): ch for r, row in enumerate(lines) for c, ch in enumerate(row)}
    start = next(p for p, ch in cells.items() if ch == "@")
    seen, queue = {start}, deque([start])
    while queue:
        r, c = queue.popleft()
        for n in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if cells.get(n, WALL) != WALL and n not in seen:
                seen.add(n)
                queue.append(n)
    return any(cells[p] == "X" for p in seen)


@pytest.mark.parametrize("index", range(3))
def test_r7_every_built_in_level_is_valid_and_finishable(index):
    """R7.6: each built-in level passes the map rules and its exit can be reached from '@'."""
    Game.from_map(LEVELS[index])
    assert _exit_reachable(LEVELS[index])


def test_r7_later_levels_are_harder():
    """R7.5: each level has more enemies and no more potions than the one before."""
    games = [Game.from_map(m) for m in LEVELS]
    enemies = [len(g.enemies) for g in games]
    potions = [sum(i.kind == "potion" for i in g.items) for g in games]
    assert enemies == sorted(enemies) and len(set(enemies)) == 3
    assert potions == sorted(potions, reverse=True)
