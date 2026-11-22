"""Tests for R10: enemies poison the player (1 damage per turn for 3 turns)."""
import json

from dungeon.cli import render
from dungeon.game import (
    ENEMY_ATTACK,
    LEVELS,
    PLAYER_MAX_HP,
    POISON_DAMAGE,
    POISON_TURNS,
    Game,
    load_game,
    save_game,
)

# Player at (1, 1), enemy at (1, 2), a corridor going down from the player.
ARENA = ["#####", "#@E.#", "#...#", "#...X"]


def _hit_once(game, direction="right"):
    """Attack an enemy that survives, so the player is hit back and poisoned."""
    game.move(direction)
    assert game.poison == POISON_TURNS


def test_r10_poison_constants():
    """R10.1/R10.2: poison lasts 3 turns and deals 1 damage per turn."""
    assert (POISON_TURNS, POISON_DAMAGE) == (3, 1)


def test_r10_new_game_is_not_poisoned():
    """R10.1: a fresh game starts without poison."""
    assert Game.from_levels(LEVELS).poison == 0


def test_r10_hit_back_poisons_on_the_default_game():
    """R10.1: on level 1 of the default game, the first enemy's hit-back poisons the player."""
    game = Game.from_levels(LEVELS)
    game.player = (3, 4)  # next to the enemy at (3, 3)
    message = game.move("left")
    assert game.player_hp == 20 - ENEMY_ATTACK  # no poison damage on the hit-back turn
    assert game.poison == 3
    assert "poison" in message.lower()


def test_r10_poison_ticks_for_three_turns_then_wears_off():
    """R10.2: each of the next 3 turns costs 1 HP before the action, then the poison ends."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    assert game.player_hp == 17
    game.move("down")
    assert (game.player_hp, game.poison) == (16, 2)
    game.move("down")
    assert (game.player_hp, game.poison) == (15, 1)
    message = game.move("right")
    assert (game.player_hp, game.poison) == (14, 0)
    assert "wears off" in message.lower()
    game.move("right")
    assert (game.player_hp, game.poison) == (14, 0)


def test_r10_attacks_count_as_turns():
    """R10.2: attacking while poisoned ticks the poison before the attack."""
    game = Game.from_map(ARENA)
    _hit_once(game)  # enemy 12 -> 7, player 17, poison 3
    game.move("right")  # poison 17 -> 16, enemy 7 -> 2, hit back 16 -> 13, poison reset to 3
    assert game.enemies[0].hp == 2
    assert game.player_hp == 17 - POISON_DAMAGE - ENEMY_ATTACK
    assert game.poison == 3


def test_r10_poison_resets_and_does_not_stack():
    """R10.3: a hit while poisoned sets the turns left back to 3, never more."""
    game = Game.from_map(ARENA)
    game.enemies[0].hp = 1000
    for _ in range(4):
        game.move("right")
        assert game.poison == 3


def test_r10_killing_blow_does_not_poison():
    """R10.1: an attack that kills the enemy causes no hit-back and no poison."""
    game = Game.from_map(ARENA)
    game.weapons = ["sword", "axe"]  # Atk 13 kills a 12 HP enemy in one hit
    game.move("right")
    assert game.enemies == []
    assert (game.player_hp, game.poison) == (20, 0)


def test_r10_killing_blow_still_ticks_existing_poison():
    """R10.2: the poison from an earlier hit still ticks on the turn the enemy dies."""
    game = Game.from_map(ARENA)
    _hit_once(game)  # enemy 12 -> 7
    game.weapons = ["sword"]  # Atk 8
    game.move("right")
    assert game.enemies == []
    assert (game.player_hp, game.poison) == (16, 2)


def test_r10_poison_can_kill_and_stops_the_action():
    """R10.4: poison bringing HP to 0 loses the game, and the player does not move."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.player_hp = 1
    message = game.move("down")
    assert game.player_hp == 0
    assert game.status == "lost"
    assert game.player == (1, 1)
    assert "lost" in message.lower()


def test_r10_poison_death_happens_before_the_attack():
    """R10.4: if poison kills at the start of an attack turn, the enemy is not hit."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    enemy_hp = game.enemies[0].hp
    game.player_hp = 1
    game.move("right")
    assert game.status == "lost"
    assert game.enemies[0].hp == enemy_hp


def test_r10_potion_cures_poison_without_ticking():
    """R10.5/R5.2: drinking heals 10, ends the poison, and poison does not hurt that turn."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.potions = 1
    game.player_hp = 5
    message = game.drink()
    assert (game.player_hp, game.poison, game.potions) == (15, 0, 0)
    assert "cure" in message.lower()
    game.move("down")
    assert game.player_hp == 15


def test_r10_drink_at_1_hp_while_poisoned_saves_the_player():
    """R10.5: poison does not tick on a drink turn, so a potion at 1 HP keeps the player alive."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.potions = 1
    game.player_hp = 1
    game.drink()
    assert game.status == "playing"
    assert (game.player_hp, game.poison) == (11, 0)


def test_r10_poisoned_player_at_full_hp_may_drink_to_cure():
    """R10.5/R5.4 (changed in round 4): at full HP a poisoned player can drink; it heals 0 and cures."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.player_hp = PLAYER_MAX_HP
    game.potions = 2
    message = game.drink()
    assert (game.player_hp, game.poison, game.potions) == (20, 0, 1)
    assert "cure" in message.lower()


def test_r10_wall_bump_and_refused_drink_do_not_tick():
    """R10.6: a bump into a wall and a drink with no potions are not turns."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    before = game.to_dict()
    game.move("up")  # wall
    game.move("left")  # wall
    game.drink()  # no potions
    assert game.to_dict() == before
    assert (game.player_hp, game.poison) == (17, 3)


def test_r10_no_tick_after_game_over():
    """R10.6/R3.3: commands after the game is over do not make poison tick."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.status = "won"
    game.move("down")
    game.drink()
    assert (game.player_hp, game.poison) == (17, 3)


def test_r10_poison_ticks_on_exit_and_carries_to_next_level():
    """R10.7: moving onto an exit ticks poison first, and the rest carries to the next level."""
    game = Game.from_levels([["@EX", "..."], ["@..X"]])
    game.enemies[0].hp = 1000
    game.move("right")  # hit back, poison 3, HP 17
    game.enemies = []
    game.move("right")  # tick: HP 16, poison 2
    game.move("right")  # tick: HP 15, poison 1, onto the exit -> level 2
    assert game.level == 2
    assert (game.player_hp, game.poison) == (15, 1)
    game.move("right")
    assert (game.player_hp, game.poison) == (14, 0)


def test_r10_poison_on_the_last_exit_can_lose_instead_of_win():
    """R10.4/R10.7: poison killing the player on the step onto the last exit loses the game."""
    game = Game.from_map(["@EX"])
    game.enemies[0].hp = 1000
    game.move("right")
    game.enemies = []
    game.player = (0, 1)
    game.player_hp = 1
    game.move("right")
    assert game.status == "lost"
    assert game.player == (0, 1)


def test_r10_poison_survives_a_save_round_trip(tmp_path):
    """R10.8/R4.2: the poison turns left are saved and loaded."""
    game = Game.from_map(ARENA)
    _hit_once(game)
    game.move("down")
    path = tmp_path / "save.json"
    save_game(game, path)
    assert json.loads(path.read_text(encoding="utf-8"))["player"]["poison"] == 2
    loaded = load_game(path)
    assert loaded == game
    assert loaded.poison == 2


def test_r10_status_line_shows_poison_only_while_poisoned():
    """R10: the status line shows the poison turns left while poisoned."""
    game = Game.from_map(ARENA)
    assert "Poison" not in render(game)
    _hit_once(game)
    assert render(game).splitlines()[-1].endswith("Poisoned: 3 turns")
    game.move("down")
    game.move("down")
    assert render(game).splitlines()[-1].endswith("Poisoned: 1 turn")


def test_r10_full_hp_drink_without_poison_still_refused():
    """R5.4/R10.5: at full HP and not poisoned, drinking is still refused."""
    game = Game.from_map(ARENA)
    game.potions = 1
    message = game.drink()
    assert game.potions == 1
    assert "full" in message.lower()
