"""Tests for R3: the game ends by reaching the exit (win) or reaching 0 HP (loss)."""
from dungeon.game import Game


def test_r3_new_game_is_playing():
    """R3: a fresh game has status 'playing'."""
    assert Game.from_map(["@.X"]).status == "playing"


def test_r3_reaching_exit_wins():
    """R3.1: stepping onto the exit sets status 'won'."""
    game = Game.from_map(["@.X"])
    game.move("right")
    assert game.status == "playing"
    message = game.move("right")
    assert game.status == "won"
    assert game.player == (0, 2)
    assert "win" in message.lower()


def test_r3_hp_reaching_zero_loses():
    """R3.2: when player HP reaches 0 the status becomes 'lost'."""
    game = Game.from_map(["@E.X"])
    game.player_hp = 3  # one enemy hit (3 damage) leaves exactly 0
    message = game.move("right")
    assert game.player_hp == 0
    assert game.status == "lost"
    assert "lost" in message.lower()


def test_r3_hp_is_clamped_at_zero():
    """R3.2: HP never goes below zero."""
    game = Game.from_map(["@E.X"])
    game.player_hp = 1
    game.move("right")
    assert game.player_hp == 0
    assert game.status == "lost"


def test_r3_no_moves_after_game_over():
    """R3.3: once the game is over, moves change nothing."""
    game = Game.from_map(["@X."])
    game.move("right")
    assert game.status == "won"
    before = game.to_dict()
    message = game.move("right")
    assert game.to_dict() == before
    assert "game over" in message.lower()


def test_r3_repeated_combat_ends_in_loss():
    """R3.2: repeated combat against a tough enemy kills the player."""
    game = Game.from_map(["E@.", "...", "..X"])
    game.enemies[0].hp = 1000
    while game.status == "playing":
        game.move("left")
    assert game.status == "lost"
    assert game.player_hp == 0


def test_r3_exit_of_earlier_level_is_not_a_win():
    """R3.1 (changed): reaching the exit of level 1 of 2 does not win the game."""
    game = Game.from_levels([["@X"], ["@.X"]])
    message = game.move("right")
    assert game.status == "playing"
    assert "win" not in message.lower()


def test_r3_exit_of_last_level_wins():
    """R3.1 (changed): only the exit of the last level wins."""
    game = Game.from_levels([["@X"], ["@.X"]])
    game.move("right")
    game.move("right")
    assert game.status == "playing"
    message = game.move("right")
    assert game.status == "won"
    assert game.level == 2
    assert "win" in message.lower()


def test_r3_losing_on_a_later_level():
    """R3.2: HP reaching 0 on level 2 loses the game."""
    game = Game.from_levels([["@X"], ["@E.X"]])
    game.move("right")
    game.player_hp = 3
    game.move("right")
    assert game.status == "lost"
