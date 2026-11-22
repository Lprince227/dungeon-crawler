"""Tests for R6: weapon pickups with varying attack bonuses that stack."""
import pytest

from dungeon.game import DEFAULT_MAP, ENEMY_START_HP, PLAYER_ATTACK, WEAPONS, Game, Item


def test_r6_weapon_kinds_have_varying_bonuses():
    """R6.1: dagger +1, sword +3, axe +5."""
    assert WEAPONS == {"dagger": 1, "sword": 3, "axe": 5}


@pytest.mark.parametrize("char, kind", [("-", "dagger"), ("/", "sword"), ("T", "axe")])
def test_r6_weapons_are_read_from_the_map(char, kind):
    """R6.1/R8.1: weapon symbols on the map become weapon items on floor tiles."""
    game = Game.from_map([f"@{char}X"])
    assert game.items == [Item((0, 1), kind)]
    assert game.tiles == ["..X"]


def test_r6_base_attack_without_weapons():
    """R6.3: with no weapons, attack is the base attack of 5."""
    game = Game.from_map(["@.X"])
    assert game.weapons == []
    assert game.attack == PLAYER_ATTACK == 5


@pytest.mark.parametrize("char, kind, bonus", [("-", "dagger", 1), ("/", "sword", 3), ("T", "axe", 5)])
def test_r6_stepping_on_weapon_equips_it(char, kind, bonus):
    """R6.2: moving onto a weapon equips it, removes it and raises attack by its bonus."""
    game = Game.from_map([f"@{char}X"])
    message = game.move("right")
    assert game.player == (0, 1)
    assert game.weapons == [kind]
    assert game.items == []
    assert game.attack == 5 + bonus
    assert kind in message.lower() and f"+{bonus}" in message


def test_r6_weapon_bonuses_stack():
    """R6.3: every weapon collected adds its bonus (dagger + sword = 9)."""
    game = Game.from_map(["@-/.X"])
    game.move("right")
    game.move("right")
    assert game.weapons == ["dagger", "sword"]
    assert game.attack == 9


def test_r6_same_weapon_kind_stacks():
    """R6.3: two of the same kind both count."""
    game = Game.from_map(["@TT.X"])
    game.move("right")
    game.move("right")
    assert game.attack == 5 + 5 + 5


def test_r6_attack_uses_weapon_bonus():
    """R6.2/R2.1: an attack deals the boosted damage."""
    game = Game.from_map(["#####", "-@E.#", "####X"])
    game.move("left")
    game.move("right")
    game.move("right")
    assert game.enemies[0].hp == ENEMY_START_HP - 6


def test_r6_strong_attack_kills_in_one_hit_without_hit_back():
    """R6.2/R2.2: with an axe (attack 10) an 8 HP enemy dies in one hit and does not hit back."""
    game = Game.from_map(["#####", "T@E.#", "####X"])
    game.move("left")
    game.move("right")
    message = game.move("right")
    assert game.enemies == []
    assert game.player_hp == 20
    assert "10" in message


def test_r6_default_map_has_items():
    """R5.1/R6.1: the default map holds three potions and one of each weapon."""
    game = Game.from_map(DEFAULT_MAP)
    kinds = sorted(item.kind for item in game.items)
    assert kinds == ["axe", "dagger", "potion", "potion", "potion", "sword"]
