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
    SetScore,
    SetLevel,
    manualSetHighScore,
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
        """Cosmetics selection screen — choose skin and hat from owned items.

        Items are displayed as a compact grid:
          - Skins section: one button per owned skin (unowned greyed out).
          - Hats section:  one button per owned hat  (unowned greyed out).

        Only owned items can be equipped; unowned ones show "Buy in Shop" to
        guide the player toward the shop.
        """
        from utils.cosmetics import (
            SKINS, HATS, owned_skins, owned_hats,
            get_skin, set_skin, get_hat, set_hat,
        )

        GOLD = (255, 215, 0)
        GREY = (160, 160, 160)
        GREEN = (60, 180, 75)

        # Buttons are rebuilt each frame so clicks always see fresh positions.
        skin_buttons = []
        hat_buttons = []

        active = True
        while active:
            self.screen.fill(self.LIGHTBLUE)
            draw_text(self.screen, "Character Selection", 36, self.WIDTH / 2, 28)
            draw_text(self.screen, "Press ESC to return", 16, self.WIDTH / 2, self.HEIGHT - 18)

            owned_s = owned_skins()
            owned_h = owned_hats()
            current_skin = get_skin()
            current_hat = get_hat()

            skin_buttons = []
            hat_buttons = []

            # ---- Skins ----
            draw_text(self.screen, "Skins", 22, self.WIDTH / 2, 60)
            btn_w, btn_h = 80, 28
            skin_ids = list(SKINS.keys())
            total_w = len(skin_ids) * (btn_w + 8) - 8
            sx = self.WIDTH / 2 - total_w / 2
            sy = 80
            for idx in skin_ids:
                spec = SKINS[idx]
                is_owned = idx in owned_s
                is_equipped = idx == current_skin
                btn = pg.Rect(sx, sy, btn_w, btn_h)
                if is_equipped:
                    pg.draw.rect(self.screen, GOLD, btn)
                elif is_owned:
                    pg.draw.rect(self.screen, GREEN, btn)
                else:
                    pg.draw.rect(self.screen, GREY, btn)
                pg.draw.rect(self.screen, self.BLACK, btn, 2)
                draw_text(self.screen, spec["name"], 13, btn.centerx, btn.centery)
                skin_buttons.append((btn, idx, is_owned))
                sx += btn_w + 8

            # ---- Hats ----
            draw_text(self.screen, "Hats", 22, self.WIDTH / 2, 130)
            hat_ids = list(HATS.keys())
            total_w_h = len(hat_ids) * (btn_w + 8) - 8
            hx = self.WIDTH / 2 - total_w_h / 2
            hy = 150
            for hat_id in hat_ids:
                spec = HATS[hat_id]
                is_owned = hat_id in owned_h
                is_equipped = hat_id == current_hat
                btn = pg.Rect(hx, hy, btn_w, btn_h)
                if is_equipped:
                    pg.draw.rect(self.screen, GOLD, btn)
                elif is_owned:
                    pg.draw.rect(self.screen, GREEN, btn)
                else:
                    pg.draw.rect(self.screen, GREY, btn)
                pg.draw.rect(self.screen, self.BLACK, btn, 2)
                draw_text(self.screen, spec["name"], 13, btn.centerx, btn.centery)
                hat_buttons.append((btn, hat_id, is_owned))
                hx += btn_w + 8

            # ---- Legend ----
            legend_y = 200
            draw_text(self.screen, "Gold = Equipped", 14, self.WIDTH / 2, legend_y,
                      color=GOLD)
            draw_text(self.screen, "Green = Owned  /  Grey = Buy in Shop", 14,
                      self.WIDTH / 2, legend_y + 18)

            # ---- Event handling ----
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    active = False
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    active = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    for btn, idx, is_owned in skin_buttons:
                        if btn.collidepoint(mouse_pos) and is_owned:
                            set_skin(idx)
                    for btn, hat_id, is_owned in hat_buttons:
                        if btn.collidepoint(mouse_pos) and is_owned:
                            set_hat(hat_id)

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
