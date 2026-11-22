"""Tests for R3: the game ends by reaching the last level's exit (win) or reaching 0 HP (loss).

R3 changed in round 3: before, the first exit reached won the game. Now only the exit of
the last level wins (see docs/decisions/0006-win-on-last-level-exit.md).
"""
from dungeon.game import DIRECTIONS, EXIT, FLOOR, LEVELS, Game


def _step_onto_exit(game):
    """Test shortcut: put the player on a floor tile next to this level's exit, then step onto it.

    An enemy on that tile is removed first, so the step is a move, not an attack.
    Returns the message from the step.
    """
    exit_pos = next(
        (r, c) for r, row in enumerate(game.tiles) for c, ch in enumerate(row) if ch == EXIT
    )
    for direction, (dr, dc) in DIRECTIONS.items():
        start = (exit_pos[0] - dr, exit_pos[1] - dc)
        if game.tile_at(start) == FLOOR:
            game.enemies = [e for e in game.enemies if e.pos != start]
            game.player = start
            return game.move(direction)
    raise AssertionError("exit has no floor tile next to it")


def test_r3_new_game_is_playing():
    """R3: a fresh game has status 'playing'."""
    assert Game.from_map(["@.X"]).status == "playing"


def test_r3_reaching_exit_wins_only_on_last_level():
    """R3.1 (changed in round 3): in the default 3-level game, the exits of levels 1 and 2
    do not win, only the exit of level 3 does. Before round 3 the first exit won."""
    game = Game.from_levels(LEVELS)
    for level in (1, 2):
        assert game.level == level
        message = _step_onto_exit(game)
        assert game.status == "playing"
        assert "win" not in message.lower()
    assert game.level == 3
    message = _step_onto_exit(game)
    assert game.status == "won"
    assert game.level == 3
    assert game.tile_at(game.player) == EXIT
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
    """R3.3 (R3.1 changed in round 3): after winning the default game on level 3's exit,
    moves and drinking change nothing. Before round 3 the game was over after the first exit."""
    game = Game.from_levels(LEVELS)
    for _ in range(3):
        _step_onto_exit(game)
    assert game.status == "won"
    game.potions = 1
    game.player_hp = 10
    before = game.to_dict()
    for direction in DIRECTIONS:
        assert "game over" in game.move(direction).lower()
    assert "game over" in game.drink().lower()
    assert game.to_dict() == before


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
