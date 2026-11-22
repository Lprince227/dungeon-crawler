"""Tests for R11: enemies get harder level by level (more HP on level 2, more HP and attack on 3)."""
import pytest

from dungeon.game import DIRECTIONS, EXIT, FLOOR, LEVELS, POISON_TURNS, Game, enemy_stats

LEVEL_STATS = {1: (12, 3), 2: (16, 3), 3: (20, 4)}


def _default_game_on_level(n):
    """The default game, taken to level n by clearing each earlier level and stepping onto its exit."""
    game = Game.from_levels(LEVELS)
    while game.level < n:
        r, c = next((r, c) for r, row in enumerate(game.tiles) for c, ch in enumerate(row) if ch == EXIT)
        game.enemies, game.items = [], []
        direction, (dr, dc) = next(
            (d, v) for d, v in DIRECTIONS.items() if game.tile_at((r - v[0], c - v[1])) == FLOOR
        )
        game.player = (r - dr, c - dc)
        game.move(direction)
    assert game.level == n
    return game


def _stand_next_to(game, enemy):
    """Put the player on a floor tile next to enemy with only that enemy left; return the direction."""
    game.enemies, game.items = [enemy], []
    r, c = enemy.pos
    direction, (dr, dc) = next(
        (d, v) for d, v in DIRECTIONS.items() if game.tile_at((r - v[0], c - v[1])) == FLOOR
    )
    game.player = (r - dr, c - dc)
    return direction


@pytest.mark.parametrize("level", [1, 2, 3])
def test_r11_enemy_stats_on_each_level_of_the_default_game(level):
    """R11.1: every enemy on level 1 / 2 / 3 of the default game has 12/3, 16/3 and 20/4 HP/attack."""
    game = _default_game_on_level(level)
    assert game.enemies
    assert {(e.hp, e.attack) for e in game.enemies} == {LEVEL_STATS[level]}


def test_r11_stats_table():
    """R11.1: the stats table, and levels past 3 use the level 3 stats."""
    assert [enemy_stats(n) for n in (1, 2, 3, 4, 10)] == [(12, 3), (16, 3), (20, 4), (20, 4), (20, 4)]


def test_r11_each_level_is_harder_than_the_last():
    """R11: enemy HP rises every level, and attack never drops and rises on level 3."""
    stats = [enemy_stats(n) for n in (1, 2, 3)]
    hps, attacks = [hp for hp, _ in stats], [atk for _, atk in stats]
    assert hps[0] < hps[1] < hps[2]
    assert attacks[0] == attacks[1] < attacks[2]


def test_r11_level_past_3_in_a_custom_game_uses_level_3_stats():
    """R11.1: the fourth map of a custom game gets 20 HP, 4 attack enemies."""
    game = Game.from_levels([["@X"], ["@X"], ["@X"], ["@E.X"]])
    for _ in range(3):
        game.move("right")
    assert game.level == 4
    assert [(e.hp, e.attack) for e in game.enemies] == [(20, 4)]


def test_r11_stats_go_by_level_number_not_by_map():
    """R11.2: the level 3 map played on its own is level 1 (12/3); any second map is level 2 (16/3)."""
    alone = Game.from_map(LEVELS[2])
    assert {(e.hp, e.attack) for e in alone.enemies} == {(12, 3)}
    game = Game.from_levels([["@X"], ["@E.X"]])
    assert [(e.hp, e.attack) for e in game.enemies] == []
    game.move("right")
    assert [(e.hp, e.attack) for e in game.enemies] == [(16, 3)]


def test_r11_level_2_enemy_takes_four_base_hits():
    """R11.3/R11.6: a level 2 enemy keeps its own HP: 16 -> 11 -> 6 -> 1 -> dead at Atk 5."""
    game = _default_game_on_level(2)
    enemy = game.enemies[0]
    direction = _stand_next_to(game, enemy)
    seen = []
    for _ in range(3):
        game.player_hp, game.poison = 20, 0
        game.move(direction)
        seen.append(enemy.hp)
    assert seen == [11, 6, 1]
    message = game.move(direction)
    assert game.enemies == []
    assert "defeat" in message.lower()


@pytest.mark.parametrize(("level", "damage"), [(1, 3), (2, 3), (3, 4)])
def test_r11_hit_back_uses_the_enemy_attack_for_its_level(level, damage):
    """R11.1/R2.3: an enemy's hit-back costs 3 HP on levels 1 and 2 and 4 HP on level 3,
    and poisons for 3 turns on every level (R11.4)."""
    game = _default_game_on_level(level)
    game.player_hp, game.poison = 20, 0
    enemy = game.enemies[0]
    message = game.move(_stand_next_to(game, enemy))
    assert game.player_hp == 20 - damage
    assert game.poison == POISON_TURNS
    assert f"hits back for {damage}" in message


def test_r11_poison_is_the_same_on_level_3():
    """R11.4: after a level 3 hit-back, poison still deals 1 damage per turn for 3 turns."""
    game = Game.from_levels([["@X"], ["@X"], ["@E", ".X"]])
    game.move("right")
    game.move("right")
    assert game.level == 3
    game.move("right")  # attack: 20 - 4 = 16, poisoned
    assert (game.player_hp, game.poison) == (16, 3)
    game.move("down")
    game.move("up")
    game.move("down")
    assert (game.player_hp, game.poison) == (13, 0)


def test_r11_level_3_hit_back_can_kill():
    """R11.1/R3.2: at 4 HP, one level 3 hit-back takes the player to 0 and the game is lost."""
    game = _default_game_on_level(3)
    game.player_hp, game.poison = 4, 0
    game.move(_stand_next_to(game, game.enemies[0]))
    assert game.player_hp == 0
    assert game.status == "lost"


@pytest.mark.parametrize(("level", "hp"), [(2, 16), (3, 20)])
def test_r11_reaching_a_level_says_how_strong_its_enemies_are(level, hp):
    """R11.5: the message on reaching level 2 or 3 gives that level's enemy HP and attack."""
    game = _default_game_on_level(level - 1)
    r, c = next((r, c) for r, row in enumerate(game.tiles) for c, ch in enumerate(row) if ch == EXIT)
    game.enemies, game.items = [], []
    direction, (dr, dc) = next(
        (d, v) for d, v in DIRECTIONS.items() if game.tile_at((r - v[0], c - v[1])) == FLOOR
    )
    game.player = (r - dr, c - dc)
    message = game.move(direction)
    assert game.level == level
    assert f"Enemies here have {hp} HP and hit for {LEVEL_STATS[level][1]}." in message


@pytest.mark.parametrize(
    ("level", "weapons", "hits"),
    [
        (2, [], 4),
        (2, ["dagger"], 3),
        (2, ["dagger", "dagger"], 3),
        (2, ["sword"], 2),
        (2, ["sword", "axe"], 2),
        (2, ["dagger", "dagger", "sword", "axe"], 2),
        (2, ["sword", "axe", "axe"], 1),
        (3, [], 4),
        (3, ["dagger"], 4),
        (3, ["dagger", "dagger"], 3),
        (3, ["sword"], 3),
        (3, ["axe"], 2),
        (3, ["dagger", "dagger", "sword", "axe"], 2),
        (3, ["axe", "axe", "axe"], 1),
    ],
)
def test_r11_hits_needed_by_attack(level, weapons, hits):
    """R11.6: hits to kill an unhurt level 2 (16 HP) or level 3 (20 HP) enemy, by attack.
    Changed in round 6: level 3 hit-backs paralyse (R12), so the counts assume no paralysis
    and it is cleared between hits, like HP and poison."""
    game = Game.from_levels([["@X"]] * (level - 1) + [["@E.X"]])
    for _ in range(level - 1):
        game.move("right")
    assert game.level == level
    game.weapons = list(weapons)
    count = 0
    while game.enemies:
        game.player_hp, game.poison, game.paralysis = 20, 0, 0
        game.move("right")
        count += 1
    assert count == hits
