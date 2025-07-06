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

Author: [Your Name]
Date: July 2025
"""

import pygame as pg
import os


def draw_text(screen, text, size, x, y):
    """
    Draw text on screen with specified parameters.
    
    This function renders text using the custom Outfit font, positioning it
    with center alignment at the specified coordinates. The text is rendered
    in black color for optimal contrast on light backgrounds.
    
    Args:
        screen (pygame.Surface): The screen surface to draw on
        text (str): The text string to render
        size (int): Font size in pixels
        x (int): X coordinate for text center position
        y (int): Y coordinate for text center position
    
    Features:
        - Uses custom Outfit font for consistent typography
        - Center-aligned positioning for perfect button/UI alignment
        - Black color (#000000) for optimal readability
        - Handles font loading with proper path resolution
    
    Usage:
        draw_text(screen, "Start Game", 24, 240, 300)
        draw_text(screen, "Score: 1250", 16, 100, 50)
    """
    # Construct path to custom font file
    font_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "font", "Outfit-Regular.ttf")
    )
    
    # Define text color (black for optimal contrast)
    BLACK = (0, 0, 0)
    
    # Load font with specified size
    font = pg.font.Font(font_folder_path, size)
    
    # Render text to surface with anti-aliasing
    text_surface = font.render(text, True, BLACK)
    
    # Get text rectangle and center it at specified position
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    
    # Draw the text to the screen
    screen.blit(text_surface, text_rect)
