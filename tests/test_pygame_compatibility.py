from pathlib import Path


def test_surface_dimensions_use_pygame_accessors():
    """pygame.Surface does not consistently expose width/height attributes."""
    game_dir = Path(__file__).parents[1] / "game"

    for source_path in game_dir.glob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        assert ".width" not in source
        assert ".height" not in source
