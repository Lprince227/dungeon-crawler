"""Tests for R2: enemies the player can fight, with health and damage logic."""
from dungeon.game import ENEMY_ATTACK, ENEMY_START_HP, PLAYER_ATTACK, PLAYER_START_HP, Game

ONE_ENEMY = ["#####", "#@E.#", "####X"]


def test_r2_starting_stats():
    """R2: player and enemies start with the specified HP."""
    game = Game.from_map(ONE_ENEMY)
    assert game.player_hp == PLAYER_START_HP == 20
    assert [e.hp for e in game.enemies] == [ENEMY_START_HP] == [8]
    assert game.enemies[0].pos == (1, 2)


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
    """R2.2: an enemy at 0 HP or less is removed and does not hit back."""
    game = Game.from_map(ONE_ENEMY)
    game.move("right")  # enemy 8 -> 3, player 20 -> 17
    message = game.move("right")  # enemy 3 -> -2, dies
    assert game.enemies == []
    assert game.player_hp == PLAYER_START_HP - ENEMY_ATTACK
    assert game.player == (1, 1)
    assert "defeat" in message.lower()


def test_r2_player_can_walk_into_freed_tile():
    """R2.2: after an enemy dies its tile is walkable."""
    game = Game.from_map(ONE_ENEMY)
    game.move("right")
    game.move("right")
    game.move("right")
    assert game.player == (1, 2)


def test_r2_enemies_keep_separate_hp_and_do_not_move():
    """R2.4: each enemy tracks its own HP and stays in place."""
    game = Game.from_map(["#####", "#E@E#", "####X"])
    game.move("left")
    left, right = sorted(game.enemies, key=lambda e: e.pos)
    assert left.hp == ENEMY_START_HP - PLAYER_ATTACK
    assert right.hp == ENEMY_START_HP
    assert (left.pos, right.pos) == ((1, 1), (1, 3))
