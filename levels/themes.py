#!/usr/bin/env python3
"""
Skybound biome themes.

The game ships several parallax sky backgrounds but previously picked one at
random each level. This rotates through distinct biomes deterministically as
the player climbs (Day -> Dusk -> Night -> Storm -> ...), each pairing a
background image with an optional colour tint for atmosphere.
"""

import pygame as pg

# How many levels a single biome lasts before rotating to the next.
LEVELS_PER_THEME = 3

# Each theme: a background image filename (must exist in imgs/) and an optional
# RGBA tint baked over it (None = untinted).
THEMES = [
    {"name": "Day",   "sky": "Freesky5.png", "tint": None},
    {"name": "Dusk",  "sky": "Freesky2.png", "tint": (255, 140, 60, 55)},
    {"name": "Night", "sky": "Freesky7.png", "tint": (20, 20, 80, 95)},
    {"name": "Storm", "sky": "Freesky8.png", "tint": (90, 95, 115, 80)},
]


def theme_for_level(level):
    """Return the theme dict for a given level number (1-based)."""
    index = ((max(1, level) - 1) // LEVELS_PER_THEME) % len(THEMES)
    return THEMES[index]


def apply_tint(surface, tint):
    """Return a copy of ``surface`` with an RGBA ``tint`` blended over it.

    ``tint`` of None returns the surface unchanged (no copy needed).
    """
    if not tint:
        return surface
    tinted = surface.copy()
    overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
    overlay.fill(tint)
    tinted.blit(overlay, (0, 0))
    return tinted
