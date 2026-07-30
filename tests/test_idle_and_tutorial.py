from unittest.mock import Mock

import pygame

from game.app import Game, IDLE_SECONDS, IDLE_WARNING_SECONDS


def bare_game():
    game = Game.__new__(Game)
    game.state = "playing"
    game.idle_elapsed = 0
    game.idle_warning = None
    game.tutorial_pending = True
    game.tutorial = False
    game.tutorial_clicks = 0
    game.tutorial_hold = 0
    game.tutorial_pointer_down = False
    return game


def test_click_regions_cover_five_actions():
    assert Game.click_zone(10, 10) == "jump_left"
    assert Game.click_zone(240, 10) == "jump_up"
    assert Game.click_zone(470, 10) == "jump_right"
    assert Game.click_zone(10, 300) == "move_left"
    assert Game.click_zone(470, 300) == "move_right"


def test_input_opens_tutorial_and_second_click_closes_it():
    game = bare_game()
    click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    game.note_input(click)
    assert game.tutorial and game.tutorial_clicks == 1

    game.note_input(click)
    assert not game.tutorial


def test_first_input_replaces_touch_prompt_with_tutorial():
    game = bare_game()
    assert game.tutorial_pending and not game.tutorial

    game.note_input(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))

    assert not game.tutorial_pending
    assert game.tutorial


def test_input_dismisses_idle_warning_without_opening_tutorial():
    game = bare_game()
    game.idle_elapsed = IDLE_SECONDS
    game.idle_warning = IDLE_WARNING_SECONDS
    game.note_input(pygame.event.Event(pygame.FINGERDOWN, finger_id=0, x=.5, y=.5))
    assert game.idle_warning is None
    assert game.idle_elapsed == 0
    assert game.tutorial_pending


def test_idle_warning_pauses_normal_update(monkeypatch):
    game = bare_game()
    game.idle_warning = 3
    game.angle = game.saw_time = 0
    game.restart_game = Mock()
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (False, False, False))
    game.update(1)
    assert game.idle_warning == 2
    game.restart_game.assert_not_called()
