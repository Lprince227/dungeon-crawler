"""Tests for R5: potions on the map that the player collects and can drink on any turn."""
import pytest

from dungeon.cli import parse_command
from dungeon.game import PLAYER_MAX_HP, POTION_HEAL, Game, Item


def test_r5_potions_are_read_from_the_map():
    """R5.1: '!' on the map becomes a potion item on a floor tile."""
    game = Game.from_map(["@!.X"])
    assert game.items == [Item((0, 1), "potion")]
    assert game.tiles == ["...X"]
    assert game.potions == 0


def test_r5_stepping_on_potion_picks_it_up():
    """R5.1: moving onto a potion adds it to the player's potions and removes it from the map."""
    game = Game.from_map(["@!.X"])
    message = game.move("right")
    assert game.player == (0, 1)
    assert game.potions == 1
    assert game.items == []
    assert "potion" in message.lower()


def test_r5_no_carry_limit():
    """R5.1: the player can carry any number of potions."""
    game = Game.from_map(["@!!!!!X"])
    for _ in range(5):
        game.move("right")
    assert game.potions == 5


def test_r5_drink_heals_and_uses_potion():
    """R5.2: drinking uses one potion and restores POTION_HEAL HP."""
    game = Game.from_map(["@!X"])
    game.move("right")
    game.player_hp = 5
    message = game.drink()
    assert POTION_HEAL == 10
    assert game.player_hp == 15
    assert game.potions == 0
    assert "10" in message


def test_r5_drink_never_heals_above_max():
    """R5.2: healing is capped at the maximum HP of 20."""
    game = Game.from_map(["@.X"])
    game.potions = 1
    game.player_hp = 17
    game.drink()
    assert game.player_hp == PLAYER_MAX_HP == 20
    assert game.potions == 0


def test_r5_drink_with_no_potions_changes_nothing():
    """R5.3: drinking with no potions only returns a message."""
    game = Game.from_map(["@.X"])
    game.player_hp = 5
    message = game.drink()
    assert game.player_hp == 5
    assert game.potions == 0
    assert "no potion" in message.lower()


def test_r5_drink_at_full_hp_keeps_potion():
    """R5.4: drinking at full HP is refused and the potion is kept."""
    game = Game.from_map(["@.X"])
    game.potions = 2
    message = game.drink()
    assert game.player_hp == PLAYER_MAX_HP
    assert game.potions == 2
    assert "full" in message.lower()


def test_r5_drink_after_combat_damage():
    """R5.2/R5.5: a potion can be drunk between attacks; enemies do not act on a drink."""
    game = Game.from_map(["#####", "!@E.#", "####X"])
    game.move("left")
    game.move("right")
    game.move("right")
    assert game.player_hp == 20 - 3
    enemy_hp = game.enemies[0].hp
    game.drink()
    assert game.player_hp == 20
    assert game.enemies[0].hp == enemy_hp
    assert game.player == (1, 1)


@pytest.mark.parametrize("status", ["won", "lost"])
def test_r5_drink_after_game_over_does_nothing(status):
    """R3.3/R5.2: drinking is only possible while the game is playing."""
    game = Game.from_map(["@.X"])
    game.potions = 1
    game.player_hp = 5
    game.status = status
    message = game.drink()
    assert game.potions == 1
    assert game.player_hp == 5
    assert "game over" in message.lower()


@pytest.mark.parametrize("text", ["p", "drink", " P ", "DRINK"])
def test_r5_drink_command_parses(text):
    """R5.2: 'p' and 'drink' are the drink command."""
    assert parse_command(text) == ("drink", None)
