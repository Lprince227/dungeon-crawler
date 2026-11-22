"""Tests for R9: enemies are harder because they have more HP (12 instead of 8 on level 1)."""
import pytest

from dungeon.game import ENEMY_ATTACK, ENEMY_START_HP, LEVELS, PLAYER_ATTACK, Game


def test_r9_enemy_start_hp_is_12():
    """R9.1: a level 1 enemy starts with 12 HP; its damage stays 3."""
    assert ENEMY_START_HP == 12
    assert ENEMY_ATTACK == 3


def test_r9_level_1_enemies_of_the_default_game_have_12_hp():
    """R9.1 (changed in round 5 by R11): all level 1 enemies of the default game start with
    12 HP and 3 attack. In round 4 this held on every built-in level."""
    game = Game.from_levels(LEVELS)
    assert len(game.enemies) == 6
    assert {(e.hp, e.attack) for e in game.enemies} == {(12, 3)}


def test_r9_enemies_on_level_2_of_the_default_game_have_more_than_12_hp():
    """R9.1 (changed in round 5 by R11): after reaching level 1's exit in the default game,
    level 2's enemies have 16 HP, not 12 as in round 4."""
    game = Game.from_levels(LEVELS)
    game.enemies = [e for e in game.enemies if e.pos != (9, 8)]
    game.player = (9, 8)  # next to level 1's exit at (9, 9)
    game.move("right")
    assert game.level == 2
    assert {e.hp for e in game.enemies} == {16}


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
    """R9.2: hits needed to kill an unhurt level 1 enemy, for each weapon mix."""
    game = Game.from_map(["@E.X"])
    game.weapons = list(weapons)
    count = 0
    while game.enemies:
        game.move("right")
        count += 1
    assert count == hits
