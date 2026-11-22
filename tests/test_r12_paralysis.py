"""Tests for R12: level 3 enemies paralyse (75% chance an attack fails, for 3 turns)."""
import random

import pytest

from dungeon.cli import render
from dungeon.game import (
    DIRECTIONS,
    EXIT,
    FLOOR,
    LEVELS,
    PARALYSIS_CHANCE,
    PARALYSIS_TURNS,
    PLAYER_MAX_HP,
    POISON_TURNS,
    Game,
    load_game,
    save_game,
)

# Player at (1, 1), enemy at (1, 2), room to walk below. Played as level 3 of a custom game,
# so the enemy has 20 HP, hits for 4 and paralyses (R11.1, R12.1).
ARENA = ["#####", "#@E.#", "#...#", "#...X"]


class FixedRoll:
    """A stand-in random generator whose random() always returns the same number."""

    def __init__(self, value):
        self.value = value
        self.calls = 0

    def random(self):
        self.calls += 1
        return self.value


class NoRoll:
    """A random generator that must not be used."""

    def random(self):
        raise AssertionError("no paralysis roll was expected")


FAIL = 0.0  # below 0.75: a paralysed attack fails
LAND = 0.99  # 0.75 or more: a paralysed attack lands


def _arena_on_level_3():
    game = Game.from_levels([["@X"], ["@X"], ARENA])
    game.move("right")
    game.move("right")
    assert game.level == 3
    return game


def _paralysed_arena():
    """Level 3 arena right after one hit-back: HP 16, poisoned and paralysed for 3 turns."""
    game = _arena_on_level_3()
    game.rng = NoRoll()
    game.move("right")
    assert (game.player_hp, game.poison, game.paralysis) == (16, 3, 3)
    return game


def _default_game_on_level(n):
    """The default game, taken to level n by clearing each earlier level and stepping onto its exit."""
    game = Game.from_levels(LEVELS)
    while game.level < n:
        _step_onto_exit(game)
    assert game.level == n
    return game


def _step_onto_exit(game):
    r, c = next((r, c) for r, row in enumerate(game.tiles) for c, ch in enumerate(row) if ch == EXIT)
    game.enemies, game.items = [], []
    direction, (dr, dc) = next(
        (d, v) for d, v in DIRECTIONS.items() if game.tile_at((r - v[0], c - v[1])) == FLOOR
    )
    game.player = (r - dr, c - dc)
    return game.move(direction)


def _stand_next_to(game, enemy):
    """Put the player on a floor tile next to enemy with only that enemy left; return the direction."""
    game.enemies, game.items = [enemy], []
    r, c = enemy.pos
    direction, (dr, dc) = next(
        (d, v) for d, v in DIRECTIONS.items() if game.tile_at((r - v[0], c - v[1])) == FLOOR
    )
    game.player = (r - dr, c - dc)
    return direction


def test_r12_paralysis_constants():
    """R12: paralysis lasts 3 turns and gives a 75% chance that an attack fails."""
    assert (PARALYSIS_TURNS, PARALYSIS_CHANCE) == (3, 0.75)


def test_r12_new_game_is_not_paralysed():
    """R12: a fresh default game starts without paralysis."""
    assert Game.from_levels(LEVELS).paralysis == 0


@pytest.mark.parametrize(("level", "paralyses"), [(1, False), (2, False), (3, True)])
def test_r12_only_level_3_enemies_of_the_default_game_paralyse(level, paralyses):
    """R12.1: every enemy on level 3 of the default game paralyses; none on levels 1 and 2 do."""
    game = _default_game_on_level(level)
    assert game.enemies
    assert {e.paralyses for e in game.enemies} == {paralyses}


@pytest.mark.parametrize("level", [1, 2])
def test_r12_level_1_and_2_hit_backs_do_not_paralyse(level):
    """R12.1/R12.2: on levels 1 and 2 of the default game a hit-back poisons but never paralyses."""
    game = _default_game_on_level(level)
    game.rng = NoRoll()
    message = game.move(_stand_next_to(game, game.enemies[0]))
    assert (game.poison, game.paralysis) == (POISON_TURNS, 0)
    assert "paraly" not in message.lower()


def test_r12_level_3_hit_back_paralyses_on_the_default_game():
    """R12.2: on level 3 of the default game, a hit-back costs 4 HP, poisons and paralyses
    for 3 turns, and the message says so."""
    game = _default_game_on_level(3)
    game.rng = NoRoll()
    message = game.move(_stand_next_to(game, game.enemies[0]))
    assert (game.player_hp, game.poison, game.paralysis) == (16, POISON_TURNS, PARALYSIS_TURNS)
    assert "paraly" in message.lower()


def test_r12_goes_by_level_number_not_by_map():
    """R12.1: the level 3 map played on its own is level 1 and does not paralyse; the fourth
    map of a custom game does."""
    assert {e.paralyses for e in Game.from_map(LEVELS[2]).enemies} == {False}
    game = Game.from_levels([["@X"], ["@X"], ["@X"], ["@E.X"]])
    for _ in range(3):
        game.move("right")
    assert game.level == 4
    assert [e.paralyses for e in game.enemies] == [True]


def test_r12_killing_blow_does_not_paralyse():
    """R12.2: an attack that kills a level 3 enemy causes no hit-back and so no paralysis."""
    game = _arena_on_level_3()
    game.weapons = ["axe", "axe", "axe"]  # Atk 20
    game.move("right")
    assert game.enemies == []
    assert (game.player_hp, game.poison, game.paralysis) == (20, 0, 0)


def test_r12_new_hit_resets_paralysis_to_3():
    """R12.2: paralysis does not stack. A hit-back while still paralysed sets it back to 3."""
    game = _paralysed_arena()
    game.rng = FixedRoll(LAND)
    game.move("right")  # paralysed turn: 3 -> 2, the roll lands, the enemy hits back
    assert game.paralysis == PARALYSIS_TURNS
    assert game.enemies[0].hp == 10


@pytest.mark.parametrize("roll", [0.0, 0.5, 0.7499])
def test_r12_paralysed_attack_can_fail(roll):
    """R12.4/R12.7: on a paralysed turn, a roll below 0.75 stops the attack. The enemy takes
    no damage and does not hit back, but the turn is used: poison and paralysis tick."""
    game = _paralysed_arena()
    game.rng = FixedRoll(roll)
    message = game.move("right")
    assert game.rng.calls == 1
    assert game.enemies[0].hp == 15  # 20 - 5 from the first hit only
    assert (game.player_hp, game.poison, game.paralysis) == (15, 2, 2)  # 1 poison, no hit-back
    assert game.player == (1, 1)
    assert "paraly" in message.lower()
    assert "can't attack" in message.lower()


@pytest.mark.parametrize("roll", [0.75, 0.9, 0.9999])
def test_r12_paralysed_attack_can_land(roll):
    """R12.4/R12.7: on a paralysed turn, a roll of 0.75 or more lets the attack go ahead as normal."""
    game = _paralysed_arena()
    game.rng = FixedRoll(roll)
    game.move("right")
    assert game.enemies[0].hp == 10
    assert game.player_hp == 16 - 1 - 4  # poison tick, then the hit-back


def test_r12_paralysis_lasts_3_turns_of_any_kind():
    """R12.3: moves count as turns. After 3 moves the paralysis has worn off, and the next
    attack lands without a roll. Moves never roll (R12.4)."""
    game = _paralysed_arena()
    game.move("down")
    assert game.paralysis == 2
    game.move("up")
    assert game.paralysis == 1
    message = game.move("down")
    assert game.paralysis == 0
    assert "wears off" in message.lower() and "paraly" in message.lower()
    game.move("up")
    game.move("right")  # NoRoll would raise if a roll were made
    assert game.enemies[0].hp == 10


def test_r12_paralysed_turns_are_the_3_after_the_hit_back():
    """R12.3: the hit-back turn is not one of the 3; the next 3 attacks each roll, the 4th doesn't."""
    game = _paralysed_arena()
    game.rng = FixedRoll(FAIL)
    for left in (2, 1, 0):
        game.player_hp, game.poison = 20, 0
        game.move("right")
        assert game.paralysis == left
    assert game.rng.calls == 3
    assert game.enemies[0].hp == 15
    game.move("right")
    assert game.rng.calls == 3
    assert game.enemies[0].hp == 10


def test_r12_wall_bump_and_refused_drink_do_not_tick_paralysis():
    """R12.3/Turns: a wall bump and a drink with no potions are not turns."""
    game = _paralysed_arena()
    game.move("up")  # wall
    game.drink()  # no potions
    assert (game.paralysis, game.poison, game.player_hp) == (3, 3, 16)


def test_r12_moving_picking_up_and_exits_are_not_affected():
    """R12.4: while paralysed the player still walks, picks up items and takes the exit."""
    game = Game.from_levels([["@X"], ["@X"], ["@E", "!.", ".X"]])
    game.move("right")
    game.move("right")
    game.rng = NoRoll()
    game.move("right")
    assert game.paralysis == 3
    game.move("down")
    assert game.potions == 1
    game.move("down")
    game.move("right")
    assert game.status == "won"


def test_r12_potion_cures_paralysis_and_poison_in_one_drink():
    """R12.5/R5.2: one drink heals 10 (up to 20) and cures both poison and paralysis."""
    game = _paralysed_arena()
    game.player_hp = 8
    game.potions = 1
    message = game.drink()
    assert (game.player_hp, game.poison, game.paralysis, game.potions) == (18, 0, 0, 0)
    assert "paraly" in message.lower() and "cure" in message.lower()
    game.move("right")  # attacks normally again: NoRoll would raise on a roll
    assert game.enemies[0].hp == 10


def test_r12_paralysed_player_at_full_hp_may_drink():
    """R12.5/R5.4 (changed in round 6): a paralysed but not poisoned player at full HP may
    drink: it heals 0 and cures the paralysis."""
    game = _paralysed_arena()
    game.player_hp, game.poison = PLAYER_MAX_HP, 0
    game.potions = 2
    message = game.drink()
    assert (game.player_hp, game.paralysis, game.potions) == (20, 0, 1)
    assert "cure" in message.lower()


def test_r12_poison_that_kills_comes_before_the_roll():
    """R12.3/R10.4: if poison takes the last HP at the start of the turn, there is no roll and
    no attack."""
    game = _paralysed_arena()
    game.player_hp = 1
    game.move("right")  # NoRoll would raise on a roll
    assert game.status == "lost"
    assert game.enemies[0].hp == 15


def test_r12_failed_attack_can_still_lose_to_poison_later():
    """R12.4/R3.2: a failed attack causes no hit-back, so it cannot lose the game by itself."""
    game = _paralysed_arena()
    game.rng = FixedRoll(FAIL)
    game.player_hp = 2
    game.move("right")
    assert (game.status, game.player_hp) == ("playing", 1)


def test_r12_paralysis_carries_over_to_the_next_level():
    """R12.6/R7.3: paralysis turns left carry over like HP (the exit step itself ticks once)."""
    game = Game.from_levels([["@X"], ["@X"], ["@E", ".X"], ["@X"]])
    game.move("right")
    game.move("right")
    game.rng = NoRoll()
    game.move("right")  # hit-back: paralysed for 3
    game.move("down")
    game.move("right")  # onto the exit of level 3
    assert (game.level, game.paralysis) == (4, 1)


def test_r12_status_line_shows_paralysis():
    """R12.6: the status line shows the paralysis turns left, after poison."""
    game = _paralysed_arena()
    assert render(game).splitlines()[-1].endswith("Poisoned: 3 turns   Paralysed: 3 turns")
    game.move("down")
    game.move("up")
    assert render(game).splitlines()[-1].endswith("Paralysed: 1 turn")
    game.move("down")
    assert "Paralysed" not in render(game)


@pytest.mark.parametrize(("level", "warned"), [(2, False), (3, True)])
def test_r12_reaching_level_3_warns_about_paralysis(level, warned):
    """R12/R11.5: the message on reaching level 3 of the default game says its enemies paralyse;
    the message for level 2 does not."""
    game = _default_game_on_level(level - 1)
    message = _step_onto_exit(game)
    assert game.level == level
    assert ("Their hits also paralyse you." in message) is warned


def test_r12_default_generator_fails_about_75_percent_of_paralysed_attacks():
    """R12.4/R12.7: with a real (seeded) generator, about 3 in 4 paralysed attacks fail."""
    game = _paralysed_arena()
    game.rng = random.Random(12)
    enemy = game.enemies[0]
    failed = 0
    trials = 2000
    for _ in range(trials):
        game.player_hp, game.poison, game.paralysis, enemy.hp = 20, 0, 3, 20
        game.move("right")
        failed += enemy.hp == 20
    assert 0.72 < failed / trials < 0.78


def test_r12_new_games_have_a_random_generator():
    """R12.7: a game made without one gets its own random generator."""
    assert isinstance(Game.from_levels(LEVELS).rng, random.Random)


def test_r12_roundtrip_keeps_paralysis_and_gives_a_new_generator(tmp_path):
    """R12.6/R12.7/R4.2: paralysis is saved and loaded; the generator is not saved, so the
    loaded game has a new one and still equals the saved game."""
    game = _paralysed_arena()
    path = tmp_path / "save.json"
    save_game(game, path)
    loaded = load_game(path)
    assert loaded == game
    assert (loaded.paralysis, [e.paralyses for e in loaded.enemies]) == (3, [True])
    assert isinstance(loaded.rng, random.Random)
    assert "rng" not in path.read_text(encoding="utf-8")
