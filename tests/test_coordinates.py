from game.config import screen, wrap_coordinate

def test_scratch_screen_conversion():
    assert screen(0, 0) == (240, 180)
    assert screen(-240, 180) == (0, 0)

def test_wrapping_lands_inside_opposite_edge():
    assert wrap_coordinate(241.5,240) == -238.5
    assert wrap_coordinate(-241.5,240) == 238.5
    assert wrap_coordinate(183,182) == -181
    assert wrap_coordinate(-183,182) == 181
