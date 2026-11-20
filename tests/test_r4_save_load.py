"""Tests for R4: save the game to a file and load it again."""
import json

import pytest

from dungeon.game import DEFAULT_MAP, Game, SaveError, load_game, save_game


def test_r4_save_writes_json_with_full_state(tmp_path):
    """R4.1: the save file is JSON holding player, enemies, map and status."""
    game = Game.from_map(["#####", "#@E.#", "####X"])
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["player"] == {"row": 1, "col": 1, "hp": 17}
    assert data["enemies"] == [{"row": 1, "col": 2, "hp": 3}]
    assert data["status"] == "playing"
    assert data["map"] == ["#####", "#...#", "####X"]


def test_r4_load_restores_equal_game(tmp_path):
    """R4.2: loading restores a game equal to the one saved."""
    game = Game.from_map(DEFAULT_MAP)
    game.move("down")
    game.move("down")
    path = tmp_path / "save.json"
    save_game(game, path)
    assert load_game(path) == game


def test_r4_loaded_game_continues_play(tmp_path):
    """R4.2: play continues from the loaded state exactly as it would have."""
    game = Game.from_map(["#####", "#@E.#", "####X"])
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    loaded = load_game(path)
    game.move("right")
    loaded.move("right")
    assert loaded == game
    assert loaded.enemies == []


def test_r4_finished_game_roundtrips_status(tmp_path):
    """R4.2: the game status survives a save/load round trip."""
    game = Game.from_map(["@X"])
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    assert load_game(path).status == "won"


def test_r4_missing_file_raises_save_error(tmp_path):
    """R4.3: loading a missing file raises SaveError."""
    with pytest.raises(SaveError):
        load_game(tmp_path / "nope.json")


@pytest.mark.parametrize(
    "content",
    [
        "not json at all",
        "[]",
        '{"version": 99}',
        '{"version": 1, "map": ["@X"], "player": {"row": 0}, "enemies": [], "status": "playing"}',
        '{"version": 1, "map": ["#X"], "player": {"row": 0, "col": 0, "hp": 5}, "enemies": [], "status": "playing"}',
        '{"version": 1, "map": [".X"], "player": {"row": 0, "col": 0, "hp": 5}, "enemies": [], "status": "dancing"}',
    ],
)
def test_r4_malformed_file_raises_save_error(tmp_path, content):
    """R4.3: corrupt or invalid save data raises SaveError."""
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(SaveError):
        load_game(path)
