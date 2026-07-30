from unittest.mock import Mock

from game.app import Game


def make_game(level):
    game = Game.__new__(Game)
    game.loaded_levels = set()
    game.levels = [level]
    game.p = Mock()
    game.a = Mock()
    game.a.stage_surface.return_value = Mock()
    game.begin_dialogue = Mock()
    return game


def test_level_intro_only_plays_on_first_load(monkeypatch):
    monkeypatch.setattr("game.app.pygame.mask.from_surface", Mock())
    level = {
        "spawn": {"x": 0, "y": 0, "facing": "right"},
        "ground": "1",
        "spikes": "costume1",
        "invisible": "costume1",
        "disappearing": "costume1",
        "assistant": {"sequence": 1},
    }
    game = make_game(level)

    game.load_level(1)
    game.load_level(1)

    game.begin_dialogue.assert_called_once_with(1)
    assert game.state == "playing"
