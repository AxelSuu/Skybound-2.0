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

Author: [Your Name]
Date: July 2025
"""

import pygame as pg
import os


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
    
    def __init__(self, x, y, w, h):
        """
        Initialize a platform sprite with specified position and dimensions.
        
        Args:
            x (int): X coordinate for the platform's left edge
            y (int): Y coordinate for the platform's top edge
            w (int): Width of the platform in pixels
            h (int): Height of the platform in pixels
            
        The platform is created by loading a base image and scaling it to
        the specified dimensions, then positioning it at the given coordinates.
        """
        # Initialize pygame sprite base class
        pg.sprite.Sprite.__init__(self)
        
        # Set up path to images folder
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Load and scale the platform image to requested dimensions
        self.image = self.load_platform2(w, h)
        
        # Set up collision rectangle and position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_platform2(self, w, h):
        """
        Load and scale the platform image to the specified dimensions.
        
        Args:
            w (int): Desired width in pixels
            h (int): Desired height in pixels
            
        Returns:
            pygame.Surface: The scaled platform image
            
        This method loads the base platform image and scales it to the
        requested dimensions. The scaling maintains the visual appearance
        while allowing for platforms of any size.
        """
        # Load the base platform image
        image1 = pg.image.load(
            os.path.join(self.img_folder_path, "plat3.png")
        ).convert_alpha()
        
        # Scale the image to the requested dimensions
        return pg.transform.scale(image1, (w, h))
