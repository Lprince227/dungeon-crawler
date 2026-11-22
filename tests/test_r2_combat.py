"""Tests for R2: enemies the player can fight, with health and damage logic."""
from dungeon.game import (
    ENEMY_ATTACK,
    ENEMY_START_HP,
    LEVELS,
    PLAYER_ATTACK,
    PLAYER_START_HP,
    Game,
)

ONE_ENEMY = ["#####", "#@E.#", "####X"]


def _default_game_next_to_enemy():
    """The default 3-level game with the player at (3, 4), next to level 1's enemy at (3, 3)."""
    game = Game.from_levels(LEVELS)
    game.player = (3, 4)
    return game


def test_r2_starting_stats():
    """R2 (enemy HP changed in round 4 by R9): in the default game the player starts with
    20 HP and every enemy on every level with 12 HP. Before round 4 enemies had 8 HP."""
    game = Game.from_levels(LEVELS)
    assert game.player_hp == PLAYER_START_HP == 20
    assert ENEMY_START_HP == 12
    all_levels = [game] + [Game.from_map(m) for m in game.next_levels]
    assert {e.hp for g in all_levels for e in g.enemies} == {12}
    assert Game.from_map(ONE_ENEMY).enemies[0].pos == (1, 2)


def test_r2_bumping_enemy_attacks_instead_of_moving():
    """R2.1: moving into an enemy damages it and the player stays put."""
    game = Game.from_map(ONE_ENEMY)
    game.move("right")
    assert game.player == (1, 1)
    assert game.enemies[0].hp == ENEMY_START_HP - PLAYER_ATTACK


def test_r2_surviving_enemy_hits_back():
    """R2.3: an enemy that survives the attack deals damage to the player."""
    game = Game.from_map(ONE_ENEMY)
    game.move("right")
    assert game.player_hp == PLAYER_START_HP - ENEMY_ATTACK


def test_r2_enemy_dies_and_is_removed():
    """R2.2 (changed in round 4 by R9 and R10): on the default game, a 12 HP enemy takes
    3 hits at Atk 5, hits back after the first two, and is removed without hitting back on
    the third. Before round 4 an 8 HP enemy died on the second hit."""
    game = _default_game_next_to_enemy()
    game.move("left")  # enemy 12 -> 7, hit back: player 20 -> 17, poisoned
    game.move("left")  # poison 17 -> 16, enemy 7 -> 2, hit back 16 -> 13
    message = game.move("left")  # poison 13 -> 12, enemy 2 -> -3, dies
    assert game.enemy_at((3, 3)) is None
    assert game.player_hp == 20 - 2 * ENEMY_ATTACK - 2
    assert game.player == (3, 4)
    assert "defeat" in message.lower()


def test_r2_player_can_walk_into_freed_tile():
    """R2.2 (changed in round 4 by R9): on the default game, after the third hit kills the
    enemy, its tile is walkable. Before round 4 the second hit killed it."""
    game = _default_game_next_to_enemy()
    for _ in range(3):
        game.move("left")
    assert game.player == (3, 4)
    game.move("left")
    assert game.player == (3, 3)


def test_r2_enemies_keep_separate_hp_and_do_not_move():
    """R2.4: each enemy tracks its own HP and stays in place."""
    game = Game.from_map(["#####", "#E@E#", "####X"])
    game.move("left")
    left, right = sorted(game.enemies, key=lambda e: e.pos)
    assert left.hp == ENEMY_START_HP - PLAYER_ATTACK
    assert right.hp == ENEMY_START_HP
    assert (left.pos, right.pos) == ((1, 1), (1, 3))
