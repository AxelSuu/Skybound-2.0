#!/usr/bin/env python3
"""
Skybound Game Loop Module

This module contains the main game loop class that handles:
- Level creation and management
- Player movement and collision detection
- Enemy AI and collision
- Power-up system management
- Visual effects and particle systems
- Achievement tracking
- Game state updates and rendering

The Loop class is the core of the gameplay experience, managing all
real-time interactions and updates during active gameplay.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
from levels.level1 import LevelClass
from utils.database_logic import *
from utils.effects import EffectsManager
from utils.sound_effects import *
from utils.achievements import check_level_achievement, check_coin_achievement, check_no_damage_achievement
from sprites.powerups import PowerUpManager
from windows.paus import Pause

# Game Configuration Constants
WIDTH : int = 480              # Screen width in pixels
HEIGHT : int = 600             # Screen height in pixels  
FPS : int = 100                # Target frames per second (high for smooth gameplay)
TITLE : str = "Skybound"       # Window title
WHITE : tuple = (255, 255, 255) # RGB color tuple for white
IMG_FOLDER_PATH : str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "imgs"))

class Loop():
    """
    Main game loop class that handles active gameplay.
    
    This class manages the core game loop during active gameplay, including:
    - Real-time game state updates
    - Player input handling and movement
    - Enemy AI and behavior
    - Collision detection and response
    - Power-up spawning and effects
    - Visual effects and particle systems
    - Achievement checking and notifications
    - Level progression and transitions
    - Game over conditions
    
    The loop runs at a high frame rate (100 FPS) to ensure smooth gameplay
    and responsive controls.
    
    Attributes:
        main: Reference to the main game instance
        screen: Pygame display surface
        clock: Pygame clock for frame rate control
        bg_scroll: Background scrolling offset
        running: Main loop control flag
        level: Current level instance
        background/background2: Background images for parallax scrolling
        mouse: Mouse position tuple
        click: Mouse click state
        effects_manager: Manages particle effects and visual feedback
        powerup_manager: Handles power-up spawning and management
        font: Font for UI text rendering
        player_was_on_floor: Tracks player ground state for landing effects
        level_start_time: Timestamp when level started (for achievements)
        player_took_damage_this_level: Tracks damage for no-damage achievements
    """
    def __init__(self, main):
        """
        Initialize the game loop and set up the game environment.
        
        Args:
            main: Reference to the main game instance for state management
            
        This initialization:
        1. Sets up pygame display and clock
        2. Creates the level and loads initial game state
        3. Initializes managers for effects and power-ups
        4. Prepares fonts and UI elements
        5. Starts the main game loop
        """
        self.main = main
        
        # Core pygame components
        self.screen = None
        self.clock = None
        
        # Visual and game state
        self.bg_scroll = 0                      # Background scrolling offset
        self.running = True                     # Main loop control flag
        self.level = None                       # Current level instance
        self.background = None                  # Primary background image
        self.background2 = None                 # Secondary background for parallax
        
        # Input handling
        self.mouse = None                       # Mouse position
        self.click = None                       # Mouse click state
        
        # Game systems
        self.effects_manager = EffectsManager()   # Particle effects and visual feedback
        self.powerup_manager = PowerUpManager()   # Power-up spawning and management
        self.font = None                         # Font for UI text
        
        # Player state tracking
        self.player_was_on_floor = False         # For landing effect detection
        self.level_start_time = 0               # Track level duration for achievements
        self.player_took_damage_this_level = False # Track damage for no-damage runs
        
        # Initialize pygame and start the game
        self.init_pygame()
        self.startgame()
        self.total_coins_collected = 0
        self.init_pygame()
        self.startgame()

    def init_pygame(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        icon = pg.image.load(os.path.join(IMG_FOLDER_PATH, 'icon.png'))
        pg.display.set_icon(icon)
        self.clock = pg.time.Clock()
        
        # Load font for UI
        try:
            font_path = os.path.join(os.path.dirname(__file__), "..", "font", "Outfit-Regular.ttf")
            self.font = pg.font.Font(font_path, 16)
        except:
            self.font = pg.font.Font(None, 16)

    def startgame(self):
        self.level = LevelClass(self)
        self.load_level()
        self.run()

    def load_level(self):
        if GetLevel() == 1:
            self.level.level1()
        elif GetLevel() > 1:
            self.level.level2()
        self.background = self.level.sky
        self.background2 = pg.transform.flip(self.background, True, False).convert()
        self.level_start_time = pg.time.get_ticks()
        self.player_took_damage_this_level = False

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                SetGamestate("EXIT")

    def update(self):
        self.all_sprites.update()
        self.powerup_manager.update(self.platforms)
        self.effects_manager.update()
        self.handle_collisions()
        
        # Update mob AI with player position
        for mob in self.mobs:
            if hasattr(mob, 'update'):
                mob.update(self.player.pos)
            if hasattr(mob, 'chase_player'):
                mob.chase_player(self.player.pos)
                
        # Check for landing effects
        if not self.player_was_on_floor and self.player.on_floor:
            self.effects_manager.create_landing_dust(
                self.player.pos.x, self.player.pos.y, 
                self.player.vel.x * 0.5
            )
            play_land_sound()
            
        self.player_was_on_floor = self.player.on_floor

    def handle_collisions(self):
        # Player platform collision
        hits = pg.sprite.spritecollide(self.player, self.platforms, False)
        if hits and self.player.vel.y >= 0:
            self.player.pos.y = hits[0].rect.top - 1
            self.player.vel.y = 0
            self.player.on_floor = True

        # Mob platform collision
        for mob in self.mobs:
            hits2 = pg.sprite.spritecollide(mob, self.platforms, False)
            if hits2 and  mob.vel.y >= 0:
                mob.pos.y = hits2[0].rect.top -1
                mob.vel.y = 0
                mob.on_floor = True

        # Player goal collision
        win = pg.sprite.spritecollide(self.player, self.goals, False)
        if win:
            # Check achievements
            level_completed = GetScore()
            level_achievements = check_level_achievement(level_completed)
            
            # Check speed run achievement
            level_time = (pg.time.get_ticks() - self.level_start_time) / 1000
            if level_time < 30:
                from utils.achievements import check_speed_run_achievement
                speed_achievement = check_speed_run_achievement()
                if speed_achievement:
                    level_achievements.append(speed_achievement)
                    
            # Check no damage achievement
            if not self.player_took_damage_this_level:
                no_damage_achievement = check_no_damage_achievement()
                if no_damage_achievement:
                    level_achievements.append(no_damage_achievement)
            
            # Display achievement notifications
            for achievement in level_achievements:
                if achievement:
                    self.effects_manager.add_floating_text(
                        WIDTH / 2, 100, 
                        f"Achievement: {achievement.name}!", 
                        (255, 215, 0)
                    )
            
            SetHighScore(GetScore())
            SetScore(GetScore() + 1)
            self.running = False
            play_victory_sound()
            self.effects_manager.create_explosion(
                self.player.pos.x, self.player.pos.y, (0, 255, 0)
            )
            if GetScore() > GetHighScore() and GetScore() > 2:
                SetGamestate("NEW_HIGHSCORE")
            else:
                SetGamestate("GAME_OVER")

        # Player mob collision
        end2 = pg.sprite.spritecollide(self.player, self.mobs, False)
        if end2:
            if self.player.take_damage():
                self.player_took_damage_this_level = True
                play_damage_sound()
                self.effects_manager.create_explosion(
                    self.player.pos.x, self.player.pos.y, (255, 0, 0)
                )
                self.effects_manager.add_floating_text(
                    self.player.pos.x, self.player.pos.y - 20, 
                    "OUCH!", (255, 0, 0)
                )
                
            if self.player.is_dead():
                self.running = False
                SetScore(1)
                SetGamestate("GAME_OVER")

        # Power-up collisions
        self.powerup_manager.check_collisions(self.player)
        
        # Check for power-up collection effects
        for powerup in self.powerup_manager.power_ups:
            if powerup.collected:
                self.effects_manager.create_collectible_effect(
                    powerup.pos.x, powerup.pos.y, powerup.image.get_at((0, 0))[:3]
                )
                play_coin_sound()
                
                # Add floating text based on power-up type
                if hasattr(powerup, 'value'):  # Coin
                    self.total_coins_collected += powerup.value
                    coin_achievements = check_coin_achievement(self.total_coins_collected)
                    for achievement in coin_achievements:
                        if achievement:
                            self.effects_manager.add_floating_text(
                                WIDTH / 2, 120, 
                                f"Achievement: {achievement.name}!", 
                                (255, 215, 0)
                            )
                    
                    self.effects_manager.add_floating_text(
                        powerup.pos.x, powerup.pos.y - 20, 
                        f"+{powerup.value}", (255, 215, 0)
                    )
                else:  # Other power-ups
                    self.effects_manager.add_floating_text(
                        powerup.pos.x, powerup.pos.y - 20, 
                        powerup.__class__.__name__.replace('Boost', '').replace('Potion', '').upper(), 
                        (255, 255, 255)
                    )

        # Handle projectile collisions (for shooter mobs)
        for mob in self.mobs:
            if hasattr(mob, 'projectiles'):
                projectile_hits = pg.sprite.spritecollide(self.player, mob.projectiles, True)
                if projectile_hits:
                    if self.player.take_damage():
                        self.player_took_damage_this_level = True
                        play_damage_sound()
                        self.effects_manager.create_explosion(
                            self.player.pos.x, self.player.pos.y, (255, 100, 0)
                        )
                        
                    if self.player.is_dead():
                        self.running = False
                        SetScore(1)
                        SetGamestate("GAME_OVER")

        # Mouse pause button collision
        self.mouse = pg.mouse.get_pos()
        self.click = pg.mouse.get_pressed()
        if (self.closebutton.rect.x + 50 > self.mouse[0] > self.closebutton.rect.x and
                self.closebutton.rect.y + 50 > self.mouse[1] > self.closebutton.rect.y):
            if self.click[0] == 1:
                Pause(self, self.main)

    def draw(self):
        self.screen.fill(WHITE)
        
        # Apply screen shake
        shake_offset = self.effects_manager.get_shake_offset()
        
        # Draw background with shake offset
        self.bg_scroll += 1.5
        if self.bg_scroll >= self.background.get_width():
            self.bg_scroll = 0
            self.background = pg.transform.flip(self.background, True, False).convert()
            self.background2 = pg.transform.flip(self.background2, True, False).convert()
            
        bg_x = WIDTH - self.background.get_width() + self.bg_scroll + shake_offset[0]
        bg_y = 0 + shake_offset[1]
        self.screen.blit(self.background, (bg_x, bg_y))
        
        if self.bg_scroll > self.background.get_width() - WIDTH:
            bg2_x = WIDTH - self.background.get_width() * 2 + self.bg_scroll + shake_offset[0]
            bg2_y = 0 + shake_offset[1]
            self.screen.blit(self.background2, (bg2_x, bg2_y))
            
        # Draw sprites with shake offset
        for sprite in self.all_sprites:
            sprite_rect = sprite.rect.copy()
            sprite_rect.x += shake_offset[0]
            sprite_rect.y += shake_offset[1]
            
            # Handle player invincibility flashing
            if sprite == self.player and self.player.should_flash():
                # Skip drawing the player when flashing
                continue
            
            self.screen.blit(sprite.image, sprite_rect)
            
        # Draw power-ups
        self.powerup_manager.draw(self.screen)
        
        # Draw projectiles from mobs
        for mob in self.mobs:
            if hasattr(mob, 'projectiles'):
                for projectile in mob.projectiles:
                    proj_rect = projectile.rect.copy()
                    proj_rect.x += shake_offset[0]
                    proj_rect.y += shake_offset[1]
                    self.screen.blit(projectile.image, proj_rect)
        
        # Draw UI
        self.draw_ui()
        
        # Draw effects last (no shake offset for UI elements)
        self.effects_manager.draw(self.screen, self.font)
        
        pg.display.flip()

    def draw_ui(self):
        """Draw the game UI including health, coins, and power-up indicators"""
        # Draw player health
        health_text = f"Health: {self.player.health}/{self.player.max_health}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (10, HEIGHT - 80))
        
        # Draw health hearts
        for i in range(self.player.max_health):
            heart_color = (255, 0, 0) if i < self.player.health else (100, 100, 100)
            heart_rect = pg.Rect(10 + i * 20, HEIGHT - 60, 16, 16)
            pg.draw.rect(self.screen, heart_color, heart_rect)
            
        # Draw coins
        coin_text = f"Coins: {self.player.coins}"
        coin_surface = self.font.render(coin_text, True, (255, 215, 0))
        self.screen.blit(coin_surface, (10, HEIGHT - 40))
        
        # Draw level
        level_text = f"Level: {GetScore()}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        self.screen.blit(level_surface, (10, HEIGHT - 20))
        
        # Draw active power-up effects
        active_effects = self.player.get_active_effects()
        for i, (effect_name, duration) in enumerate(active_effects):
            effect_y = 70 + i * 25
            effect_color = {
                "Speed": (255, 255, 0),
                "Jump": (0, 255, 0),
                "Shield": (0, 191, 255),
                "Double Jump": (255, 0, 255)
            }.get(effect_name, (255, 255, 255))
            
            # Draw effect background
            effect_rect = pg.Rect(WIDTH - 90, effect_y, 80, 20)
            pg.draw.rect(self.screen, (*effect_color, 50), effect_rect)
            
            # Draw effect progress bar
            progress = min(1.0, duration / 300.0)  # Assuming 300 is max duration
            bar_width = int(76 * progress)
            bar_rect = pg.Rect(WIDTH - 88, effect_y + 2, bar_width, 16)
            pg.draw.rect(self.screen, effect_color, bar_rect)
            
            # Draw effect name
            effect_text = self.font.render(effect_name, True, (255, 255, 255))
            text_rect = effect_text.get_rect(center=(WIDTH - 50, effect_y + 10))
            self.screen.blit(effect_text, text_rect)
            
        # Draw shield indicator
        if self.player.shield_active:
            shield_surface = pg.Surface((self.player.rect.width + 10, self.player.rect.height + 10), pg.SRCALPHA)
            pg.draw.circle(shield_surface, (0, 191, 255, 100), 
                          (shield_surface.get_width()//2, shield_surface.get_height()//2), 
                          shield_surface.get_width()//2, 3)
            self.screen.blit(shield_surface, (self.player.rect.x - 5, self.player.rect.y - 5))
