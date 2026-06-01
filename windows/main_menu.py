#!/usr/bin/env python3
"""
Skybound Main Menu System

This module implements the main menu screen for the Skybound game, providing
the primary interface for players to navigate between different game modes
and options.

The main menu includes:
- Game start functionality
- Character selection and customization
- Achievement viewing
- Settings configuration
- High score display
- Shop system for unlockables

The menu uses a clean, modern design with smooth transitions and responsive
button interactions. It serves as the central hub for all game functionality
and provides easy access to all game features.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
import time
from utils.draw_text import draw_text
from constants import WIDTH, HEIGHT, FPS
from utils.database_logic import (
    GetHighScore,
    SetGamestate,
    SetHat,
    SetChar,
    SetScore,
    SetLevel,
    manualSetHighScore,
    SelectedChar,
    Hat,
    ResetProgress,
)
from utils.daily import set_active as set_daily_active, get_daily_best
from utils.achievements import reset_all_achievements
from utils.player_stats import player_stats


class Main_menu:
    """
    Main menu screen class providing the central navigation interface.
    
    This class manages the main menu screen, which serves as the primary
    interface for players to access different game modes and options.
    
    The menu provides access to:
    - Starting new games
    - Character selection and customization
    - Achievement viewing and tracking
    - Settings and configuration
    - High score viewing
    - Shop system for unlockables
    
    The interface uses a button-based layout with clear visual feedback
    for user interactions, providing an intuitive and user-friendly
    navigation experience.
    
    Attributes:
        WIDTH, HEIGHT (int): Screen dimensions
        Color constants: Various color definitions for UI elements
        TITLE (str): Game title text
        img_folder_path (str): Path to image assets
        screen (pygame.Surface): Main display surface
        clock (pygame.Clock): Frame rate control
        running (bool): Menu loop control flag
        buttons (list): List of interactive button elements
        selected_button (int): Currently highlighted button index
    """
    
    def __init__(self):
        """
        Initialize the main menu with screen setup and button layout.
        
        This initialization:
        1. Sets up screen dimensions and color constants
        2. Loads background images and UI elements
        3. Configures button layout and interactions
        4. Initializes pygame display and clock
        5. Starts the main menu loop
        """
        # Screen configuration
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        # Color constants for UI elements
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHTBLUE = (135, 206, 235)
        self.BLUE = (0, 0, 255)
        
        # Game branding
        self.TITLE = "Skybound"
        
        # Asset paths
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )

        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        pg.display.set_caption(self.TITLE)
        icon = pg.image.load(os.path.join(self.img_folder_path, "icon.png"))
        self.bg_scroll = 0
        self.background = pg.image.load(
            os.path.join(self.img_folder_path, "sky2.png")
        ).convert()
        self.background2 = pg.transform.flip(self.background, True, False).convert()
        pg.display.set_icon(icon)
        self.clock = pg.time.Clock()
        # Unified button width to match character selection buttons
        self.BUTTON_WIDTH = 200
        self.main_menu()

    def main_menu(self):
        main_menu = True
        while main_menu:
            self.clock.tick(FPS)
            # Background animation block
            self.screen.fill(self.WHITE)
            self.bg_scroll += 0.5
            if self.bg_scroll >= self.background.get_width():
                self.bg_scroll = 0
                self.background = pg.transform.flip(
                    self.background, True, False
                ).convert()
                self.background2 = pg.transform.flip(
                    self.background2, True, False
                ).convert()
            self.screen.blit(
                self.background, (480 - self.background.get_width() + self.bg_scroll, 0)
            )
            if self.bg_scroll > self.background.get_width() - 480:
                self.screen.blit(
                    self.background2,
                    (480 - self.background.get_width() * 2 + self.bg_scroll, 0),
                )

            # Text block
            draw_text(self.screen, "Skybound", 50, self.WIDTH / 2, self.HEIGHT / 4)
            draw_text(
                self.screen, "Press Space to play", 22, self.WIDTH / 2, self.HEIGHT / 2
            )
            draw_text(self.screen, "Shop", 22, self.WIDTH / 2, 440)
            draw_text(
                self.screen,
                "Character Selection",
                22,
                self.WIDTH / 2,
                475,
            )
            draw_text(
                self.screen,
                f"Highscore: {GetHighScore()}",
                22,
                self.WIDTH / 2,
                self.HEIGHT * 3 / 4 + 60,
            )
            draw_text(self.screen, "Settings", 22, self.WIDTH / 2, 540)
            draw_text(self.screen, "Achievements", 22, self.WIDTH / 2, 580)
            draw_text(self.screen, "Restart", 22, self.WIDTH / 2, 40)

            # Event handler
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    main_menu = False
                    SetGamestate("EXIT")
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if self.shop_button.collidepoint(mouse_pos):
                        self.show_shop()
                    if self.character_button.collidepoint(mouse_pos):
                        self.show_character_selection()
                    if self.settings_button.collidepoint(mouse_pos):
                        self.show_settings()
                    if self.achievements_button.collidepoint(mouse_pos):
                        self.show_achievements()
                    if self.restart_button.collidepoint(mouse_pos):
                        ResetProgress()            # coins, score, level, highscore, hat, char, upgrades
                        reset_all_achievements()
                        player_stats.reset_stats()  # clear in-memory run state
            keys = pg.key.get_pressed()
            if keys[pg.K_SPACE]:
                main_menu = False
                SetGamestate("START_SCREEN")

            # Draw buttons block
            # Text positions: Shop (440), Character (475), Settings (540), Achievements (570), Restart (40)
            # Button rects should be centered on text (text_y - 15 for 30px height buttons)
            bw = self.BUTTON_WIDTH
            hw = bw / 2
            self.shop_button = pg.Rect(self.WIDTH / 2 - hw, 425, bw, 30)
            self.character_button = pg.Rect(self.WIDTH / 2 - hw, 460, bw, 30)
            self.settings_button = pg.Rect(self.WIDTH / 2 - hw, 525, bw, 30)
            self.achievements_button = pg.Rect(self.WIDTH / 2 - hw, 565, bw, 30)
            self.restart_button = pg.Rect(self.WIDTH / 2 - hw, 25, bw, 30)
            pg.draw.rect(self.screen, self.BLACK, self.shop_button, 2)
            pg.draw.rect(self.screen, self.BLACK, self.character_button, 2)
            pg.draw.rect(self.screen, self.BLACK, self.settings_button, 2)
            pg.draw.rect(self.screen, self.BLACK, self.achievements_button, 2)
            pg.draw.rect(self.screen, self.BLACK, self.restart_button, 2)

            pg.display.flip()

    def show_character_selection(self):
        # Create character selection screen, talks with txt files

        hat_image = pg.image.load(
            os.path.join(self.img_folder_path, "hat1.png")
        ).convert_alpha()
        normal_image = pg.image.load(
            os.path.join(self.img_folder_path, "IdleL2.png")
        ).convert_alpha()
        hat_character = normal_image.copy()
        hat_character.blit(hat_image, (0, -8))

        character_screen = True
        while character_screen:
            self.screen.fill(self.LIGHTBLUE)
            draw_text(
                self.screen, "Character Selection", 50, self.WIDTH / 2, self.HEIGHT / 4
            )
            draw_text(
                self.screen,
                "Press ESC to return",
                22,
                self.WIDTH / 2,
                self.HEIGHT * 0.8,
            )

            # Draw untouched buttons
            bw = getattr(self, 'BUTTON_WIDTH', 100)
            hw = bw / 2
            self.hat_button = pg.Rect(self.WIDTH / 2 - hw, self.HEIGHT / 2 - 10, bw, 30)
            self.normal_button = pg.Rect(self.WIDTH / 2 - hw, self.HEIGHT / 2 + 40, bw, 30)

            # Logic for drawing touched buttons
            selected_char = SelectedChar()
            if selected_char == 0:
                pg.draw.rect(self.screen, self.BLUE, self.normal_button)
                pg.draw.rect(self.screen, self.BLACK, self.hat_button, 2)
                draw_text(
                    self.screen, "Normal", 22, self.WIDTH / 2, self.HEIGHT / 2 + 53
                )
                draw_text(self.screen, "Hat", 22, self.WIDTH / 2, self.HEIGHT / 2 + 3)
                self.screen.blit(
                    normal_image, (self.WIDTH / 2 + 100, self.HEIGHT / 2 - 50)
                )

            elif selected_char == 1:
                pg.draw.rect(self.screen, self.BLUE, self.hat_button)
                pg.draw.rect(self.screen, self.BLACK, self.normal_button, 2)
                draw_text(
                    self.screen, "Normal", 22, self.WIDTH / 2, self.HEIGHT / 2 + 53
                )
                draw_text(self.screen, "Hat", 22, self.WIDTH / 2, self.HEIGHT / 2 + 3)
                self.screen.blit(
                    hat_character, (self.WIDTH / 2 + 100, self.HEIGHT / 2 - 50)
                )

            else:
                pg.draw.rect(self.screen, self.BLACK, self.hat_button, 2)
                pg.draw.rect(self.screen, self.BLACK, self.normal_button, 2)
                draw_text(
                    self.screen, "Normal", 22, self.WIDTH / 2, self.HEIGHT / 2 + 53
                )
                draw_text(self.screen, "Hat", 22, self.WIDTH / 2, self.HEIGHT / 2 + 3)

            # event handler
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    character_screen = False
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    character_screen = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if self.hat_button.collidepoint(mouse_pos) and Hat() == "hat":
                        SetChar("1")
                    if self.normal_button.collidepoint(mouse_pos):
                        SetChar("0")

            pg.display.flip()

    def show_shop(self):
        """Show the upgrade shop (spend coins on permanent upgrades + cosmetics)."""
        from windows.shop import Shop

        Shop()

    def show_settings(self):
        """Show settings screen"""
        from windows.settings import Settings

        settings = Settings()

    def show_achievements(self):
        """Show achievements screen"""
        from windows.achievements import AchievementScreen

        achievements = AchievementScreen()
