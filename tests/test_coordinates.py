from game.config import screen

def test_scratch_screen_conversion():
    assert screen(0, 0) == (240, 180)
    assert screen(-240, 180) == (0, 0)
