"""Tests for deterministic biome theme rotation and platform tinting."""

import pygame as pg
from levels.themes import THEMES, LEVELS_PER_THEME, theme_for_level


def test_theme_is_stable_within_a_biome_band():
    # All levels in the first band map to the first theme.
    for level in range(1, LEVELS_PER_THEME + 1):
        assert theme_for_level(level) is THEMES[0]


def test_theme_advances_each_band():
    assert theme_for_level(1) is THEMES[0]
    assert theme_for_level(1 + LEVELS_PER_THEME) is THEMES[1]
    assert theme_for_level(1 + 2 * LEVELS_PER_THEME) is THEMES[2]


def test_theme_rotation_wraps_around():
    band = LEVELS_PER_THEME * len(THEMES)
    # One full cycle later returns to the starting theme.
    assert theme_for_level(1) is theme_for_level(1 + band)


def test_low_levels_are_clamped_safely():
    # Defensive: level 0 / negatives should not crash and map to the first band.
    assert theme_for_level(0) is THEMES[0]
    assert theme_for_level(-5) is THEMES[0]


# ---------------------------------------------------------------------------
# Platform biome tinting
# ---------------------------------------------------------------------------

def test_platform_with_no_tint_constructs_cleanly():
    """Platform2 with tint=None must produce a valid surface (Day biome)."""
    from sprites.platform import Platform2
    p = Platform2(0, 0, 100, 20, tint=None)
    assert isinstance(p.image, pg.Surface)
    assert p.rect.width == 100
    assert p.rect.height == 20


def test_platform_with_tint_constructs_cleanly():
    """Platform2 with an RGBA tint must still produce a valid surface."""
    from sprites.platform import Platform2
    dusk_tint = (255, 140, 60, 27)  # half-strength Dusk tint
    p = Platform2(10, 20, 80, 20, tint=dusk_tint)
    assert isinstance(p.image, pg.Surface)
    assert p.image.get_size() == (80, 20)


def test_platform_tint_alters_pixel_color():
    """A tinted platform must differ from an untinted one of the same size."""
    from sprites.platform import Platform2
    untinted = Platform2(0, 0, 60, 20, tint=None)
    tinted = Platform2(0, 0, 60, 20, tint=(0, 0, 200, 120))  # strong blue tint
    # Sample the centre pixel — colours must differ.
    cx, cy = 30, 10
    assert untinted.image.get_at((cx, cy)) != tinted.image.get_at((cx, cy))
