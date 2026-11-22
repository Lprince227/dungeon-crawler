"""Tests for R9: enemies are harder because they have more HP (12 instead of 8)."""
import pytest

from dungeon.game import ENEMY_ATTACK, ENEMY_START_HP, LEVELS, PLAYER_ATTACK, Game


def test_r9_enemy_start_hp_is_12():
    """R9.1: an enemy starts with 12 HP; its damage stays 3."""
    assert ENEMY_START_HP == 12
    assert ENEMY_ATTACK == 3


@pytest.mark.parametrize("index", range(3))
def test_r9_every_enemy_on_every_built_in_level_has_12_hp(index):
    """R9.1: all enemies on each built-in level start with 12 HP."""
    game = Game.from_map(LEVELS[index])
    assert game.enemies
    assert {e.hp for e in game.enemies} == {12}


def test_r9_enemies_on_later_levels_of_the_default_game_have_12_hp():
    """R9.1: after reaching level 1's exit in the default game, level 2's enemies have 12 HP."""
    game = Game.from_levels(LEVELS)
    game.enemies = [e for e in game.enemies if e.pos != (9, 8)]
    game.player = (9, 8)  # next to level 1's exit at (9, 9)
    game.move("right")
    assert game.level == 2
    assert {e.hp for e in game.enemies} == {12}


def test_r9_base_attack_needs_three_hits():
    """R9.2: with base attack 5, an enemy takes 3 hits (12 -> 7 -> 2 -> dead)."""
    game = Game.from_map(["@E.X"])
    assert PLAYER_ATTACK == 5
    game.move("right")
    assert game.enemies[0].hp == 7
    game.move("right")
    assert game.enemies[0].hp == 2
    message = game.move("right")
    assert game.enemies == []
    assert "defeat" in message.lower()


@pytest.mark.parametrize(
    ("weapons", "hits"),
    [
        ([], 3),
        (["dagger"], 2),
        (["sword"], 2),
        (["axe"], 2),
        (["dagger", "axe"], 2),
        (["sword", "axe"], 1),
        (["dagger", "sword", "axe"], 1),
    ],
)
def test_r9_hits_needed_by_attack(weapons, hits):
    """R9.2: hits needed to kill an unhurt enemy, for each weapon mix."""
    game = Game.from_map(["@E.X"])
    game.weapons = list(weapons)
    count = 0
    while game.enemies:
        game.move("right")
        count += 1
    assert count == hits
