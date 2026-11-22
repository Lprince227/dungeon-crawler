"""Tests for R4: save the game to a file and load it again."""
import json

import pytest

from dungeon.game import DEFAULT_MAP, LEVELS, Game, SaveError, load_game, save_game


def test_r4_save_writes_json_with_full_state(tmp_path):
    """R4.1/R4.5: the version 3 save holds level, map, next levels, player, enemies, items and status."""
    game = Game.from_map(["######", "#@E.!#", "#/####", "#!###X"])
    game.move("down")
    game.move("up")
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {
        "version": 3,
        "level": 1,
        "map": ["######", "#....#", "#.####", "#.###X"],
        "next_levels": [],
        "player": {"row": 1, "col": 1, "hp": 20, "potions": 0, "weapons": ["sword"]},
        "enemies": [],
        "items": [{"row": 1, "col": 4, "kind": "potion"}, {"row": 3, "col": 1, "kind": "potion"}],
        "status": "playing",
    }


def test_r4_save_records_enemy_hp_and_potions(tmp_path):
    """R4.1: enemy HP and carried potions are saved."""
    game = Game.from_map(["#####", "!@E.#", "####X"])
    game.move("left")
    game.move("right")
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["player"] == {"row": 1, "col": 1, "hp": 17, "potions": 1, "weapons": []}
    assert data["enemies"] == [{"row": 1, "col": 2, "hp": 3}]
    assert data["items"] == []


def test_r4_roundtrip_keeps_items_potions_and_weapons(tmp_path):
    """R4.2: potions, weapons and items left on the map survive a round trip."""
    game = Game.from_map(DEFAULT_MAP)
    game.move("right")
    game.potions = 2
    path = tmp_path / "save.json"
    save_game(game, path)
    loaded = load_game(path)
    assert loaded == game
    assert loaded.weapons == ["dagger"]
    assert loaded.attack == 6
    assert len(loaded.items) == 5


def test_r4_version_1_save_is_upgraded(tmp_path):
    """R4.5: a round 1 save loads with 0 potions, no weapons and no items, as level 1 of 3."""
    v1 = {
        "version": 1,
        "map": ["#####", "#...#", "####X"],
        "player": {"row": 1, "col": 1, "hp": 17},
        "enemies": [{"row": 1, "col": 2, "hp": 3}],
        "status": "playing",
    }
    path = tmp_path / "old.json"
    path.write_text(json.dumps(v1), encoding="utf-8")
    game = load_game(path)
    assert game.player == (1, 1)
    assert game.player_hp == 17
    assert game.enemies[0].hp == 3
    assert (game.potions, game.weapons, game.items) == (0, [], [])
    assert (game.level, game.total_levels) == (1, 3)
    assert game.next_levels == [list(m) for m in LEVELS[1:]]
    save_game(game, path)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 3


V2_SAVE = {
    "version": 2,
    "map": ["#####", "#...#", "####X"],
    "player": {"row": 1, "col": 1, "hp": 12, "potions": 2, "weapons": ["sword"]},
    "enemies": [{"row": 1, "col": 2, "hp": 3}],
    "items": [{"row": 1, "col": 3, "kind": "axe"}],
    "status": "playing",
}


def test_r4_version_2_save_becomes_level_1(tmp_path):
    """R4.5: a round 2 save keeps all its state and becomes level 1, followed by levels 2 and 3."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps(V2_SAVE), encoding="utf-8")
    game = load_game(path)
    assert game.tiles == V2_SAVE["map"]
    assert (game.player, game.player_hp, game.potions, game.weapons) == ((1, 1), 12, 2, ["sword"])
    assert [(e.pos, e.hp) for e in game.enemies] == [((1, 2), 3)]
    assert [(i.pos, i.kind) for i in game.items] == [((1, 3), "axe")]
    assert (game.level, game.total_levels, game.status) == (1, 3, "playing")
    assert game.next_levels == [list(m) for m in LEVELS[1:]]
    save_game(game, path)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 3


def test_r4_upgraded_version_2_save_continues_to_level_2(tmp_path):
    """R4.5/R7.2: walking to the exit of an upgraded round 2 save loads built-in level 2."""
    path = tmp_path / "old.json"
    open_exit = dict(V2_SAVE, map=["#####", "#...X", "#####"], enemies=[], items=[])
    path.write_text(json.dumps(open_exit), encoding="utf-8")
    game = load_game(path)
    for _ in range(3):
        game.move("right")
    assert game.status == "playing"
    assert game.level == 2
    assert game.tiles == Game.from_map(LEVELS[1]).tiles
    assert game.weapons == ["sword"]


def test_r4_won_version_2_save_stays_won(tmp_path):
    """R4.5: a round 2 save that was already won stays won and gets no further levels."""
    won = dict(V2_SAVE, status="won", player=dict(V2_SAVE["player"], row=2, col=4))
    path = tmp_path / "old.json"
    path.write_text(json.dumps(won), encoding="utf-8")
    game = load_game(path)
    assert game.status == "won"
    assert game.next_levels == []
    assert game.total_levels == 1


def test_r4_roundtrip_on_a_later_level(tmp_path):
    """R4.1/R4.2: level number and the levels still to come survive a round trip."""
    game = Game.from_levels([["@X"], ["@!.X"], ["@E.X"]])
    game.move("right")
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["level"] == 2
    assert data["next_levels"] == [["@E.X"]]
    loaded = load_game(path)
    assert loaded == game
    loaded.move("right")
    loaded.move("right")
    assert (loaded.level, loaded.status, len(loaded.enemies)) == (3, "playing", 1)


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
        # R4.3 round 2 checks on version 2 saves
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 21, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": -1, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": "2", "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": ["laser"]}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": "sword"}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 1, "kind": "cake"}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 3, "kind": "potion"}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 1, "kind": "potion"}, {"row": 0, "col": 1, "kind": "axe"}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 2, "kind": "potion"}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 0, "kind": "potion"}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 1}], "status": "playing"}',
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [{"row": 0, "col": 1, "kind": []}], "status": "playing"}',
        # R4.3 round 3 checks on version 3 saves (level and next_levels)
        '{"version": 3, "level": 0, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": -1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": "2", "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": true, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1.5, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": "@X", "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": ["@X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": [["..X"]], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": [["@dX"]], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": [["@X", "."]], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": [[1, 2]], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": [[]], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "next_levels": null, "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 3, "level": 1, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
    ],
)
def test_r4_malformed_file_raises_save_error(tmp_path, content):
    """R4.3: corrupt or invalid save data raises SaveError (including round 2 and 3 fields)."""
    path = tmp_path / "bad.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(SaveError):
        load_game(path)


def test_r4_valid_version_2_save_loads(tmp_path):
    """R4.2/R4.5: the base save used by the malformed cases above is itself valid."""
    content = (
        '{"version": 2, "map": ["...X"], "player": {"row": 0, "col": 0, "hp": 5, "potions": 1, '
        '"weapons": ["axe", "axe"]}, "enemies": [{"row": 0, "col": 2, "hp": 3}], '
        '"items": [{"row": 0, "col": 1, "kind": "sword"}], "status": "playing"}'
    )
    path = tmp_path / "good.json"
    path.write_text(content, encoding="utf-8")
    game = load_game(path)
    assert game.attack == 15
    assert game.potions == 1
    assert [(i.pos, i.kind) for i in game.items] == [((0, 1), "sword")]


def test_r4_valid_version_3_save_loads(tmp_path):
    """R4.2/R4.5: the base version 3 save used by the malformed cases above is itself valid."""
    content = (
        '{"version": 3, "level": 2, "map": ["...X"], "next_levels": [["@X"], ["@E.-X"]], '
        '"player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, '
        '"enemies": [], "items": [], "status": "playing"}'
    )
    path = tmp_path / "good.json"
    path.write_text(content, encoding="utf-8")
    game = load_game(path)
    assert (game.level, game.total_levels) == (2, 4)
    assert game.next_levels == [["@X"], ["@E.-X"]]
