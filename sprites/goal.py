#!/usr/bin/env python3
"""
Skybound Goal Sprite Module

This module defines the Goal sprite class, which represents the level completion
target that players must reach to advance to the next level.

The Goal sprite serves as the primary objective for each level, providing
a clear visual target for players to reach. When the player collides with
the goal, it triggers level completion logic and progression to the next level.

Features:
- Visual representation of the level objective
- Collision detection with the player
- Strategic placement on the highest or most challenging platforms
- Clear visual design to stand out in the level environment

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os


class Goal(pg.sprite.Sprite):
    """
    Goal sprite representing the level completion target.
    
    This sprite defines the objective that players must reach to complete
    a level. It's typically placed on the highest or most challenging
    platform in each level, requiring players to navigate through all
    obstacles and enemies to reach it.
    
    The goal sprite uses a distinctive visual design to make it easily
    identifiable as the level objective, helping players understand
    where they need to go.
    
    Attributes:
        image (pygame.Surface): The goal sprite image
        rect (pygame.Rect): Rectangle for positioning and collision detection
        img_folder_path (str): Path to the images folder
    """
    
    def __init__(self, x, y, w, h):
        """
        Initialize the goal sprite at the specified position.
        
        Args:
            x (int): X coordinate for the goal position
            y (int): Y coordinate for the goal position
            w (int): Width parameter (currently unused but kept for compatibility)
            h (int): Height parameter (currently unused but kept for compatibility)
            
        The goal sprite is positioned exactly at the specified coordinates,
        typically on the highest platform or at the end of the level path.
        """
        # Initialize pygame sprite base class
        pg.sprite.Sprite.__init__(self)
        
        # Set up path to images folder
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Load the goal sprite image
        self.image = pg.image.load(
            os.path.join(self.img_folder_path, "goal2.png")
        ).convert_alpha()
        
        # Set up collision rectangle and position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
