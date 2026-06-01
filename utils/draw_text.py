#!/usr/bin/env python3
"""
Skybound Text Rendering Utilities

This module provides text rendering utilities for the Skybound game,
including font loading, text positioning, and styling functions.

The module uses the custom "Outfit" font for consistent typography
throughout the game interface, providing a clean and modern appearance.

Features:
- Custom font loading with fallback to system fonts
- Center-aligned text positioning
- Consistent color scheme (black text on light backgrounds)
- Optimized rendering for game UI elements

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os

_FONT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "font", "Outfit-Regular.ttf")
)
_BLACK = (0, 0, 0)
_font_cache: dict = {}


def draw_text(screen, text, size, x, y):
    """Draw center-aligned black text at (x, y) using the Outfit font."""
    if size not in _font_cache:
        _font_cache[size] = pg.font.Font(_FONT_PATH, size)
    font = _font_cache[size]
    text_surface = font.render(text, True, _BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)
