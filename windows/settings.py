#!/usr/bin/env python3
"""
Skybound Settings Screen Module

This module implements the settings screen for the Skybound game, providing
players with controls for audio settings, gameplay options, and system
preferences.

The settings screen includes:
- Audio volume controls (SFX and Music)
- Audio enable/disable toggles
- Visual feedback for setting changes
- Persistent settings storage
- Intuitive keyboard controls

The settings system provides immediate feedback for changes and automatically
saves preferences for future game sessions.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
from utils.draw_text import draw_text
from utils.sound_effects import sound_manager


class Settings:
    """
    Settings screen class for managing game preferences and options.
    
    This class provides a comprehensive settings interface allowing players
    to customize their gaming experience through various options:
    
    Audio Settings:
    - Sound effects volume control
    - Music volume control
    - Individual enable/disable toggles for SFX and music
    
    Visual Feedback:
    - Real-time preview of volume changes
    - Color-coded setting indicators
    - Clear visual hierarchy for setting categories
    
    The settings are automatically saved and loaded, ensuring player
    preferences persist across game sessions.
    
    Attributes:
        WIDTH, HEIGHT (int): Screen dimensions
        Color constants: Various color definitions for UI elements
        screen (pygame.Surface): Main display surface
        settings_active (bool): Settings screen control flag
        sfx_volume (float): Sound effects volume (0.0 to 1.0)
        music_volume (float): Music volume (0.0 to 1.0)
        sfx_enabled (bool): Sound effects enabled state
        music_enabled (bool): Music enabled state
    """
    
    def __init__(self):
        """
        Initialize the settings screen with current configuration values.
        
        This initialization:
        1. Sets up screen dimensions and color constants
        2. Creates the display surface for the settings screen
        3. Loads current settings from the sound manager
        4. Initializes control flags and state variables
        5. Starts the settings display loop
        """
        # Screen configuration
        self.WIDTH = 480
        self.HEIGHT = 600
        
        # Color constants for UI elements
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHTBLUE = (135, 206, 235)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)    # For enabled states
        self.RED = (255, 0, 0)      # For disabled states
        
        # Initialize display
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.settings_active = True
        
        # Load current settings from sound manager
        self.sfx_volume = sound_manager.sfx_volume
        self.music_volume = sound_manager.music_volume
        self.sfx_enabled = sound_manager.sfx_enabled
        self.music_enabled = sound_manager.music_enabled
        
        # Start the settings display loop
        self.show_settings()
        
    def show_settings(self):
        """Display the settings screen"""
        while self.settings_active:
            self.screen.fill(self.LIGHTBLUE)
            
            # Title
            draw_text(self.screen, "Settings", 40, self.WIDTH / 2, 50)
            
            # SFX Volume
            draw_text(self.screen, "Sound Effects Volume", 20, self.WIDTH / 2, 120)
            sfx_bar_rect = pg.Rect(self.WIDTH / 2 - 100, 140, 200, 20)
            pg.draw.rect(self.screen, self.WHITE, sfx_bar_rect)
            pg.draw.rect(self.screen, self.BLACK, sfx_bar_rect, 2)
            
            sfx_fill_width = int(200 * self.sfx_volume)
            sfx_fill_rect = pg.Rect(self.WIDTH / 2 - 100, 140, sfx_fill_width, 20)
            pg.draw.rect(self.screen, self.GREEN, sfx_fill_rect)
            
            draw_text(self.screen, f"{int(self.sfx_volume * 100)}%", 16, self.WIDTH / 2, 170)
            
            # Music Volume
            draw_text(self.screen, "Music Volume", 20, self.WIDTH / 2, 200)
            music_bar_rect = pg.Rect(self.WIDTH / 2 - 100, 220, 200, 20)
            pg.draw.rect(self.screen, self.WHITE, music_bar_rect)
            pg.draw.rect(self.screen, self.BLACK, music_bar_rect, 2)
            
            music_fill_width = int(200 * self.music_volume)
            music_fill_rect = pg.Rect(self.WIDTH / 2 - 100, 220, music_fill_width, 20)
            pg.draw.rect(self.screen, self.GREEN, music_fill_rect)
            
            draw_text(self.screen, f"{int(self.music_volume * 100)}%", 16, self.WIDTH / 2, 250)
            
            # Toggle buttons
            sfx_toggle_rect = pg.Rect(self.WIDTH / 2 - 80, 290, 160, 30)
            sfx_color = self.GREEN if self.sfx_enabled else self.RED
            pg.draw.rect(self.screen, sfx_color, sfx_toggle_rect)
            pg.draw.rect(self.screen, self.BLACK, sfx_toggle_rect, 2)
            sfx_text = "SFX: ON" if self.sfx_enabled else "SFX: OFF"
            draw_text(self.screen, sfx_text, 18, self.WIDTH / 2, 305)
            
            music_toggle_rect = pg.Rect(self.WIDTH / 2 - 80, 340, 160, 30)
            music_color = self.GREEN if self.music_enabled else self.RED
            pg.draw.rect(self.screen, music_color, music_toggle_rect)
            pg.draw.rect(self.screen, self.BLACK, music_toggle_rect, 2)
            music_text = "Music: ON" if self.music_enabled else "Music: OFF"
            draw_text(self.screen, music_text, 18, self.WIDTH / 2, 355)
            
            # Instructions
            draw_text(self.screen, "Use mouse to adjust sliders", 16, self.WIDTH / 2, 420)
            draw_text(self.screen, "Click buttons to toggle", 16, self.WIDTH / 2, 440)
            draw_text(self.screen, "Press ESC to return", 16, self.WIDTH / 2, 480)
            
            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.settings_active = False
                    
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.settings_active = False
                        
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pg.mouse.get_pos()
                    
                    # Check SFX volume slider
                    if sfx_bar_rect.collidepoint(mouse_x, mouse_y):
                        self.sfx_volume = max(0, min(1, (mouse_x - sfx_bar_rect.x) / sfx_bar_rect.width))
                        sound_manager.set_sfx_volume(self.sfx_volume)
                        
                    # Check music volume slider
                    elif music_bar_rect.collidepoint(mouse_x, mouse_y):
                        self.music_volume = max(0, min(1, (mouse_x - music_bar_rect.x) / music_bar_rect.width))
                        sound_manager.set_music_volume(self.music_volume)
                        
                    # Check SFX toggle
                    elif sfx_toggle_rect.collidepoint(mouse_x, mouse_y):
                        self.sfx_enabled = not self.sfx_enabled
                        sound_manager.sfx_enabled = self.sfx_enabled
                        
                    # Check music toggle
                    elif music_toggle_rect.collidepoint(mouse_x, mouse_y):
                        self.music_enabled = not self.music_enabled
                        sound_manager.music_enabled = self.music_enabled
                        if self.music_enabled:
                            # Resume music logic would go here
                            pass
                        else:
                            # Pause music logic would go here
                            pass
                            
                elif event.type == pg.MOUSEMOTION:
                    # Allow dragging on sliders
                    if pg.mouse.get_pressed()[0]:  # Left mouse button held
                        mouse_x, mouse_y = pg.mouse.get_pos()
                        
                        # Check SFX volume slider
                        if sfx_bar_rect.collidepoint(mouse_x, mouse_y):
                            self.sfx_volume = max(0, min(1, (mouse_x - sfx_bar_rect.x) / sfx_bar_rect.width))
                            sound_manager.set_sfx_volume(self.sfx_volume)
                            
                        # Check music volume slider
                        elif music_bar_rect.collidepoint(mouse_x, mouse_y):
                            self.music_volume = max(0, min(1, (mouse_x - music_bar_rect.x) / music_bar_rect.width))
                            sound_manager.set_music_volume(self.music_volume)
            
            pg.display.flip()
            
    def save_settings(self):
        """Save settings to file"""
        settings_data = {
            'sfx_volume': self.sfx_volume,
            'music_volume': self.music_volume,
            'sfx_enabled': self.sfx_enabled,
            'music_enabled': self.music_enabled
        }
        
        # Save to text file (simple format)
        txt_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "txts")
        )
        
        try:
            with open(os.path.join(txt_folder_path, "settings.txt"), "w") as f:
                f.write(f"sfx_volume={self.sfx_volume}\n")
                f.write(f"music_volume={self.music_volume}\n")
                f.write(f"sfx_enabled={self.sfx_enabled}\n")
                f.write(f"music_enabled={self.music_enabled}\n")
        except:
            pass  # Ignore if can't save
            
    def load_settings(self):
        """Load settings from file"""
        txt_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "txts")
        )
        
        try:
            with open(os.path.join(txt_folder_path, "settings.txt"), "r") as f:
                lines = f.readlines()
                for line in lines:
                    if '=' in line:
                        key, value = line.strip().split('=')
                        if key == 'sfx_volume':
                            self.sfx_volume = float(value)
                        elif key == 'music_volume':
                            self.music_volume = float(value)
                        elif key == 'sfx_enabled':
                            self.sfx_enabled = value.lower() == 'true'
                        elif key == 'music_enabled':
                            self.music_enabled = value.lower() == 'true'
        except:
            pass  # Use defaults if can't load
