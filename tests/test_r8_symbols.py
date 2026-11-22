"""Tests for R8: map symbols that are not the movement keys w, a, s, d."""
import pytest

from dungeon.cli import ALIASES, HELP, KEYS
from dungeon.game import ENEMY, EXIT, FLOOR, ITEM_CHARS, LEVELS, PLAYER, WALL, Game

COMMAND_KEYS = set(KEYS) | set(ALIASES)


def test_r8_weapon_symbols():
    """R8.1: dagger '-', sword '/', axe 'T'; potion stays '!'."""
    assert ITEM_CHARS == {"!": "potion", "-": "dagger", "/": "sword", "T": "axe"}


def test_r8_no_map_symbol_is_a_command_key():
    """R8.1: no map symbol is w, a, s, d or p, in either case."""
    symbols = {WALL, FLOOR, PLAYER, ENEMY, EXIT} | set(ITEM_CHARS)
    assert COMMAND_KEYS == {"w", "a", "s", "d", "p"}
    assert not {s.lower() for s in symbols} & COMMAND_KEYS


@pytest.mark.parametrize("old", ["d", "s", "a"])
def test_r8_old_weapon_letters_are_rejected(old):
    """R8.1: the round 2 weapon letters are no longer map symbols."""
    with pytest.raises(ValueError):
        Game.from_map([f"@{old}X"])


@pytest.mark.parametrize("index", range(3))
def test_r8_built_in_levels_use_no_command_keys(index):
    """R8.2: no built-in level contains w, a, s, d or p."""
    text = "".join(LEVELS[index]).lower()
    assert not set(text) & COMMAND_KEYS


def test_r8_help_text_explains_new_symbols():
    """R8.2: the help text names the new weapon symbols."""
    for line in ("- dagger", "/ sword", "T axe"):
        assert line in " ".join(HELP.split())
