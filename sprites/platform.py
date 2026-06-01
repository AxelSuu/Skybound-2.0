#!/usr/bin/env python3
"""
Skybound Platform Sprite Module

This module defines the Platform2 sprite class, which represents the scalable
platform objects that players can stand on and jump between in the game.

Platforms are fundamental elements of the level design, providing:
- Solid surfaces for player movement and jumping
- Collision detection for physics interactions
- Scalable dimensions for varied level layouts
- Visual consistency across all levels

The platform system supports dynamic sizing, allowing the level generation
system to create platforms of various widths and heights to create interesting
and challenging level layouts.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
from levels.themes import apply_tint


class Platform2(pg.sprite.Sprite):
    """
    Scalable platform sprite for level construction.
    
    This sprite represents solid platforms that players can stand on, jump
    from, and use for navigation through the level. The platform supports
    arbitrary dimensions through scaling, making it suitable for procedural
    level generation.
    
    Features:
    - Scalable to any width and height
    - Solid collision detection
    - Consistent visual appearance
    - Optimized for level generation algorithms
    
    The platform uses a base image that is scaled to the requested dimensions,
    ensuring visual consistency while providing flexibility for level design.
    
    Attributes:
        image (pygame.Surface): The scaled platform image
        rect (pygame.Rect): Rectangle for positioning and collision detection
        img_folder_path (str): Path to the images folder
    """
    
    def __init__(self, x, y, w, h, tint=None):
        """
        Initialize a platform sprite with specified position, dimensions and
        an optional biome tint.

        Args:
            x (int): X coordinate for the platform's left edge
            y (int): Y coordinate for the platform's top edge
            w (int): Width of the platform in pixels
            h (int): Height of the platform in pixels
            tint (tuple | None): Optional RGBA tint applied after scaling.
                Pass the theme tint from ``levels.themes.theme_for_level()``
                to colour-match the platform to the current biome.
        """
        pg.sprite.Sprite.__init__(self)

        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )

        self.image = self._load_platform(w, h, tint)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def _load_platform(self, w, h, tint):
        """Load, scale, and optionally tint the platform image."""
        image = pg.image.load(
            os.path.join(self.img_folder_path, "plat3.png")
        ).convert_alpha()
        image = pg.transform.scale(image, (w, h))
        return apply_tint(image, tint)

    # Keep old name as an alias so any external callers don't break.
    def load_platform2(self, w, h):
        return self._load_platform(w, h, None)
