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
