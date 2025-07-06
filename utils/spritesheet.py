#!/usr/bin/env python3
"""
Skybound Spritesheet Management System

This module provides functionality for loading and managing spritesheets
with accompanying JSON metadata files. It enables efficient sprite animation
and asset management for the Skybound game.

The system uses texture atlases (spritesheets) combined with JSON metadata
to define sprite locations, sizes, and frame information. This approach
provides several benefits:
- Reduced memory usage through texture atlasing
- Faster loading times with fewer image files
- Easy sprite management and animation sequences
- Metadata-driven sprite definitions

Supported Features:
- PNG spritesheet loading with alpha channel support
- JSON metadata parsing for sprite definitions
- Individual sprite extraction from atlases
- Named sprite lookup for easy access

Author: [Your Name]
Date: July 2025
"""

import pygame as pg
import json
import os


class Spritesheet:
    """
    Spritesheet manager for loading and extracting sprites from texture atlases.
    
    This class handles the loading of spritesheet images and their accompanying
    JSON metadata files, providing methods to extract individual sprites by
    name or coordinates.
    
    The JSON metadata file should contain sprite definitions in the format:
    {
        "sprites": {
            "sprite_name": {
                "x": 0,
                "y": 0,
                "width": 32,
                "height": 32
            }
        }
    }
    
    Attributes:
        img_folder_path (str): Path to the images folder
        filename (str): Full path to the spritesheet image file
        sprite_sheet (pygame.Surface): Loaded spritesheet surface
        meta_data (str): Path to the JSON metadata file
        data (dict): Parsed JSON metadata containing sprite definitions
    """
    
    def __init__(self, filename):
        """
        Initialize the spritesheet with the specified filename.
        
        Args:
            filename (str): Name of the spritesheet file (PNG format)
            
        The constructor automatically loads both the image file and its
        corresponding JSON metadata file (same name with .json extension).
        """
        # Set up path to images folder
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Load the spritesheet image
        self.filename = os.path.join(self.img_folder_path, filename)
        self.sprite_sheet = pg.image.load(self.filename).convert_alpha()
        
        # Load the corresponding JSON metadata file
        self.meta_data = self.filename.replace("png", "json")
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, width, height):
        """
        Extract a sprite from the spritesheet at specified coordinates.
        
        Args:
            x (int): X coordinate of the sprite's top-left corner
            y (int): Y coordinate of the sprite's top-left corner
            width (int): Width of the sprite in pixels
            height (int): Height of the sprite in pixels
            
        Returns:
            pygame.Surface: The extracted sprite surface with alpha channel
            
        This method creates a new surface and blits the specified region
        from the spritesheet, preserving transparency.
        """
        # Create a new surface with alpha channel support
        sprite = pg.Surface((width, height), pg.SRCALPHA)
        
        # Blit the specified region from the spritesheet
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        
        return sprite

    def parse_sprite(self, name):
        """
        Extract a sprite by name using metadata definitions.
        
        Args:
            name (str): Name of the sprite as defined in the JSON metadata
            
        Returns:
            pygame.Surface: The extracted sprite surface
            
        This method looks up the sprite definition in the loaded metadata
        and extracts the corresponding sprite from the spritesheet.
        """
        # Get sprite definition from metadata
        sprite = self.data["sprites"][name]
        
        # Extract coordinates and dimensions
        x, y, w, h = sprite["x"], sprite["y"], sprite["width"], sprite["height"]
        
        # Extract and return the sprite
        image = self.get_sprite(x, y, w, h)
        return image
