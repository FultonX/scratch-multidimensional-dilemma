WIDTH, HEIGHT = 480, 360
FPS, UPDATE_HZ = 60, 30
TITLE = "The Multidirectional Dilemma"

def screen(x, y): return 240 + x, 180 - y

def wrap_coordinate(value, limit):
    """Wrap a coordinate while keeping it inside the opposite boundary."""
    span = limit * 2
    while value > limit:
        value -= span
    while value < -limit:
        value += span
    return value
