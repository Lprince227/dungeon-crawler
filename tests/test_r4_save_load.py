"""Tests for R4: save the game to a file and load it again."""
import json

import pytest

from dungeon.game import DEFAULT_MAP, LEVELS, Game, SaveError, load_game, save_game


def test_r4_save_writes_json_with_full_state(tmp_path):
    """R4.1/R4.5/R10.8/R11.3: the version 5 save holds level, map, next levels, player (with
    poison), enemies (with attack), items and status. The 12 HP level 1 enemy (R9) survives
    the sword and poisons the player. Changed in round 5: version 5 and enemy attack."""
    game = Game.from_map(["######", "#@E.!#", "#/####", "#!###X"])
    game.move("down")
    game.move("up")
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {
        "version": 5,
        "level": 1,
        "map": ["######", "#....#", "#.####", "#.###X"],
        "next_levels": [],
        "player": {"row": 1, "col": 1, "hp": 17, "potions": 0, "weapons": ["sword"], "poison": 3},
        "enemies": [{"row": 1, "col": 2, "hp": 4, "attack": 3}],
        "items": [{"row": 1, "col": 4, "kind": "potion"}, {"row": 3, "col": 1, "kind": "potion"}],
        "status": "playing",
    }


def test_r4_save_records_enemy_hp_and_potions(tmp_path):
    """R4.1/R11.3: enemy HP and attack, carried potions and poison are saved."""
    game = Game.from_map(["#####", "!@E.#", "####X"])
    game.move("left")
    game.move("right")
    game.move("right")
    path = tmp_path / "save.json"
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["player"] == {"row": 1, "col": 1, "hp": 17, "potions": 1, "weapons": [], "poison": 3}
    assert data["enemies"] == [{"row": 1, "col": 2, "hp": 7, "attack": 3}]
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
    assert (game.potions, game.weapons, game.items, game.poison) == (0, [], [], 0)
    assert (game.level, game.total_levels) == (1, 3)
    assert game.next_levels == [list(m) for m in LEVELS[1:]]
    save_game(game, path)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 5


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
    assert (game.level, game.total_levels, game.status, game.poison) == (1, 3, "playing", 0)
    assert game.next_levels == [list(m) for m in LEVELS[1:]]
    save_game(game, path)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 5


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
    for _ in range(2):  # 12 HP enemy (R9): 7 -> 2 -> dead, with poison ticking (R10)
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
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": -1}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 4}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": "2"}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": true}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 1.5}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": null}, "enemies": [], "items": [], "status": "playing"}',
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": []}, "enemies": [], "items": [], "status": "playing"}',
        # R4.3 round 5 checks on version 5 saves (enemy attack)
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": 0}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": -2}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": "3"}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": true}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": 2.5}], "items": [], "status": "playing"}',
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], "player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, "enemies": [{"row": 0, "col": 2, "hp": 3, "attack": null}], "items": [], "status": "playing"}',
    ],
)
def test_r4_malformed_file_raises_save_error(tmp_path, content):
    """R4.3: corrupt or invalid save data raises SaveError (including round 2, 3 and 4 fields)."""
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


def test_r4_valid_version_4_save_loads(tmp_path):
    """R4.2/R4.5/R10.8: the base version 4 save used by the malformed cases above is itself valid."""
    content = (
        '{"version": 4, "level": 1, "map": ["...X"], "next_levels": [], '
        '"player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 3}, '
        '"enemies": [], "items": [], "status": "playing"}'
    )
    path = tmp_path / "good.json"
    path.write_text(content, encoding="utf-8")
    assert load_game(path).poison == 3


def test_r4_valid_version_5_save_loads(tmp_path):
    """R4.2/R4.5/R11.3: the base version 5 save used by the malformed cases above is itself valid."""
    content = (
        '{"version": 5, "level": 1, "map": ["...X"], "next_levels": [], '
        '"player": {"row": 0, "col": 0, "hp": 5, "potions": 0, "weapons": [], "poison": 0}, '
        '"enemies": [{"row": 0, "col": 2, "hp": 3, "attack": 3}], "items": [], "status": "playing"}'
    )
    path = tmp_path / "good.json"
    path.write_text(content, encoding="utf-8")
    assert [(e.pos, e.hp, e.attack) for e in load_game(path).enemies] == [((0, 2), 3, 3)]


def test_r4_roundtrip_keeps_level_3_enemy_stats(tmp_path):
    """R4.2/R11.3: level 3 enemies' HP and attack survive a round trip of the default game."""
    game = Game.from_levels(LEVELS)
    for _ in range(2):
        game.enemies = []
        game.player = (9, 8)  # next to the exit at (9, 9) on levels 1 and 2
        game.tiles[9] = game.tiles[9][:8] + ".X" + game.tiles[9][10:]
        game.move("right")
    assert game.level == 3
    game.enemies[0].hp = 9
    path = tmp_path / "save.json"
    save_game(game, path)
    loaded = load_game(path)
    assert loaded == game
    assert {(e.hp, e.attack) for e in loaded.enemies[1:]} == {(20, 4)}
    assert (loaded.enemies[0].hp, loaded.enemies[0].attack) == (9, 4)


def _v4_save(level, poison=2):
    return {
        "version": 4,
        "level": level,
        "map": ["#####", "#...#", "####X"],
        "next_levels": [["@E.X"]] if level < 3 else [],
        "player": {"row": 1, "col": 1, "hp": 15, "potions": 1, "weapons": ["sword"], "poison": poison},
        "enemies": [{"row": 1, "col": 2, "hp": 12}],
        "items": [{"row": 1, "col": 3, "kind": "potion"}],
        "status": "playing",
    }


@pytest.mark.parametrize(("level", "attack"), [(1, 3), (2, 3), (3, 4), (4, 4)])
def test_r4_version_4_save_is_upgraded(tmp_path, level, attack):
    """R4.5/R11.1: a round 4 save loads with each enemy given the attack for the saved level.
    Everything else is kept, including the saved 12 HP (not the new level HP), and it is
    written back as version 5."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps(_v4_save(level)), encoding="utf-8")
    game = load_game(path)
    assert [(e.pos, e.hp, e.attack) for e in game.enemies] == [((1, 2), 12, attack)]
    assert (game.level, game.player, game.player_hp, game.poison) == (level, (1, 1), 15, 2)
    assert (game.potions, game.weapons) == (1, ["sword"])
    assert [(i.pos, i.kind) for i in game.items] == [((1, 3), "potion")]
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 5
    assert data["enemies"] == [{"row": 1, "col": 2, "hp": 12, "attack": attack}]


def test_r4_upgraded_version_4_save_gets_round_5_stats_on_the_next_level(tmp_path):
    """R4.5/R11.1: a round 4 save on level 2 leads to a level 3 with 20 HP, 4 attack enemies."""
    path = tmp_path / "old.json"
    open_exit = dict(_v4_save(2, poison=0), map=["#####", "#...X", "#####"], enemies=[], items=[])
    path.write_text(json.dumps(open_exit), encoding="utf-8")
    game = load_game(path)
    for _ in range(3):
        game.move("right")
    assert game.level == 3
    assert [(e.hp, e.attack) for e in game.enemies] == [(20, 4)]


def test_r4_version_3_save_goes_through_version_4_to_5(tmp_path):
    """R4.5: a round 3 save on level 2 is upgraded 3 -> 4 -> 5. It is not poisoned, and its
    8 HP enemy keeps its HP and gets level 2's attack of 3."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps(V3_SAVE), encoding="utf-8")
    game = load_game(path)
    assert game.poison == 0
    assert [(e.hp, e.attack) for e in game.enemies] == [(8, 3)]
    assert game.to_dict()["version"] == 5


V3_SAVE = {
    "version": 3,
    "level": 2,
    "map": ["#####", "#...#", "####X"],
    "next_levels": [["@E.X"]],
    "player": {"row": 1, "col": 1, "hp": 12, "potions": 1, "weapons": ["dagger"]},
    "enemies": [{"row": 1, "col": 2, "hp": 8}],
    "items": [{"row": 1, "col": 3, "kind": "potion"}],
    "status": "playing",
}


def test_r4_version_3_save_is_upgraded(tmp_path):
    """R4.5/R9.3/R10.8: a round 3 save loads unpoisoned, its enemies keep their saved HP,
    and it is written back as version 5 (changed in round 5: was version 4)."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps(V3_SAVE), encoding="utf-8")
    game = load_game(path)
    assert game.poison == 0
    assert (game.level, game.total_levels, game.status) == (2, 3, "playing")
    assert (game.player, game.player_hp, game.potions, game.weapons) == ((1, 1), 12, 1, ["dagger"])
    assert [(e.pos, e.hp) for e in game.enemies] == [((1, 2), 8)]
    assert [(i.pos, i.kind) for i in game.items] == [((1, 3), "potion")]
    assert game.next_levels == [["@E.X"]]
    save_game(game, path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["version"] == 5
    assert data["player"]["poison"] == 0


def test_r4_upgraded_version_3_save_gets_round_5_stats_on_the_next_level(tmp_path):
    """R4.5/R11.1: enemies on the levels still to come in a round 3 save get the stats for
    their level. Changed in round 5: the saved level 2 leads to level 3, so 20 HP and 4 attack
    (was 12 HP on every level)."""
    path = tmp_path / "old.json"
    open_exit = dict(V3_SAVE, map=["#####", "#...X", "#####"], enemies=[], items=[])
    path.write_text(json.dumps(open_exit), encoding="utf-8")
    game = load_game(path)
    for _ in range(3):
        game.move("right")
    assert game.level == 3
    assert [(e.hp, e.attack) for e in game.enemies] == [(20, 4)]


def test_r4_version_2_save_goes_through_version_3_to_4(tmp_path):
    """R4.5: a round 2 save is upgraded step by step (2 -> 3 -> 4 -> 5), is not poisoned and
    its level 1 enemy gets attack 3. Changed in round 5: ends at version 5."""
    path = tmp_path / "old.json"
    path.write_text(json.dumps(V2_SAVE), encoding="utf-8")
    game = load_game(path)
    assert game.poison == 0
    assert [e.attack for e in game.enemies] == [3]
    assert game.to_dict()["version"] == 5
