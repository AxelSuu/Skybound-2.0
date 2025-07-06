#!/usr/bin/env python3
"""
Skybound Player Module

This module contains the Player class which handles all player-related functionality
including movement, animations, power-ups, health system, and collision detection.

The Player class is the core interactive element of the game, supporting:
- Smooth movement with acceleration and friction
- Multiple animation states (idle, moving, jumping, falling)
- Power-up system with various temporary abilities
- Health and coin collection systems
- Customizable character appearances (hats)
- Persistent statistics across game sessions

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
from utils.spritesheet import Spritesheet
from utils.database_logic import Hat
from utils.player_stats import player_stats


class Player(pg.sprite.Sprite):
    """
    Player character class with comprehensive movement, animation, and power-up systems.
    
    This class manages the player character's state, including:
    - Physics-based movement with acceleration and friction
    - Animated sprite states (idle, moving, jumping, falling)
    - Power-up effects (speed boost, jump boost, shield, double jump)
    - Health and damage system with invincibility frames
    - Coin collection and persistent statistics
    - Customizable character appearance (hat selection)
    - Collision detection with optimized hitbox
    
    The player uses a Vector2-based physics system for smooth movement and
    supports various power-ups that temporarily enhance abilities.
    
    Attributes:
        Physics System:
            pos (pg.Vector2): Current world position
            vel (pg.Vector2): Current velocity
            acc (pg.Vector2): Current acceleration
            rect (pg.Rect): Sprite rectangle for rendering
            hitbox (pg.Rect): Collision detection rectangle
            
        Animation System:
            frame_index (int): Current animation frame
            animation_timer (int): Animation timing counter
            playerleft (bool): Player facing direction
            state (str): Current animation state
            
        Power-up System:
            speed_boost_timer (int): Remaining speed boost duration
            jump_boost_timer (int): Remaining jump enhancement duration
            shield_timer (int): Remaining shield protection duration
            double_jump_timer (int): Remaining double jump ability duration
            
        Health and Stats:
            health (int): Current health points
            max_health (int): Maximum health capacity
            coins (int): Collected coins
            invincible_timer (int): Invincibility frames after damage
    """

    def __init__(self):
        """
        Initialize the player with default settings and load animation frames.
        
        This initialization process:
        1. Sets up the sprite base class
        2. Loads character images and animations based on hat selection
        3. Initializes physics constants and vectors
        4. Sets up the power-up system with timers
        5. Loads persistent player statistics from previous sessions
        6. Creates collision hitbox for accurate collision detection
        
        The player starts with default health and no active power-ups,
        but statistics like coins and certain upgrades may be restored
        from previous gameplay sessions.
        """
        # Initialize pygame sprite base class
        pg.sprite.Sprite.__init__(self)
        
        # Set up file paths for game assets
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Load character customization (hat selection)
        self.hat = Hat()
        self.hat_image1 = pg.image.load(
            os.path.join(self.img_folder_path, "hat1.png")
        ).convert_alpha()
        self.hat_image2 = pg.image.load(
            os.path.join(self.img_folder_path, "hat2.png")
        ).convert_alpha()
        
        # Load default character frame
        self.startframe = pg.image.load(
            os.path.join(self.img_folder_path, "IdleL2.png")
        ).convert_alpha()
        
        # Animation state variables
        self.jumping, self.falling = False, False
        self.frame_index = 0              # Current frame in animation sequence
        self.animation_timer = 0          # Timer for animation frame switching
        self.playerleft = True            # Player facing direction (True = left)
        self.state = "idle"              # Current animation state
        
        # Movement and physics state
        self.on_floor = False            # Ground contact detection
        self.jump_pressed = False        # Jump input state (prevents double-jumping)
        
        # Screen dimensions for boundary checking
        self.WIDTH = 480
        self.HEIGHT = 600
        
        # Physics constants
        self.PLAYER_ACC = 0.5            # Player acceleration rate
        self.PLAYER_FRICTION = -0.12     # Friction/deceleration rate
        
        # Load animation spritesheet
        self.spritesheet = Spritesheet("Playersheet.png")
        
        # Load appropriate character animations based on hat selection
        if self.hat == "0":
            self.load_character()
        elif self.hat == "hat":
            self.load_hat_character()

        self.image = self.startframe  # Start with the first frame

        self.rect = (
            self.image.get_rect()
        )  # Set the rect attribute for collision detection
        self.rect.center = (30, self.HEIGHT * 3 / 4)  # Create center rect object
        self.pos = pg.Vector2(self.rect.center)  # Set the position vector for movement
        self.vel = pg.Vector2(0, 0)  # Set the velocity vector for movement
        self.acc = pg.Vector2(0, 0)  # Set the acceleration vector for movement

        # Create hitbox for collision detection
        self.hitbox = pg.Rect(
            self.rect.left + 10,
            self.rect.top + 7,
            self.rect.width - 26,
            self.rect.height - 7,
        )
        
        # Power-up system - load from persistent stats
        self.speed_boost_timer = 0
        self.jump_boost_timer = 0
        self.shield_timer = 0
        self.double_jump_timer = 0
        self.health = 3
        self.max_health = 5
        self.coins = 0
        self.has_double_jump = False
        self.double_jump_used = False
        self.shield_active = False
        self.power_up_effects = []
        
        # Load persistent stats
        player_stats.apply_stats_to_player(self)
        
        # Invincibility frames
        self.invincible_timer = 0
        self.invincible_duration = 120  # 2 seconds at 60 FPS (120 frames)

    def update(self):
        """Update the player's position, state, and animations."""

        self.acc = pg.Vector2(0, self.PLAYER_ACC)
        self.animation_timer += 1
        
        # Update power-up timers
        self.update_power_ups()

        keys = pg.key.get_pressed()

        if not keys[pg.K_LEFT] and not keys[pg.K_RIGHT] and self.on_floor:
            self.state = "idle"

        # Apply speed boost if active
        speed_multiplier = 1.5 if self.speed_boost_timer > 0 else 1.0
        base_acc = self.PLAYER_ACC * speed_multiplier

        if keys[pg.K_LEFT]:
            self.acc.x = -base_acc
            self.state = "moving"
            self.playerleft = True

        if keys[pg.K_RIGHT]:
            self.acc.x = base_acc
            self.state = "moving"
            self.playerleft = False

        # Enhanced jumping with double jump support
        if keys[pg.K_SPACE] and not self.jump_pressed:
            if self.on_floor and self.vel.y == 0:
                # Regular jump
                jump_strength = -12
                if self.jump_boost_timer > 0:
                    jump_strength = -16  # Enhanced jump
                self.vel.y = jump_strength
                self.on_floor = False
                self.jump_pressed = True
                self.double_jump_used = False
            elif (self.has_double_jump and not self.double_jump_used and 
                  not self.on_floor and self.vel.y > -8):
                # Double jump
                jump_strength = -12
                if self.jump_boost_timer > 0:
                    jump_strength = -16
                self.vel.y = jump_strength
                self.double_jump_used = True
                self.jump_pressed = True

        if not keys[pg.K_SPACE]:
            self.jump_pressed = False

        if self.vel.y < 0:
            self.state = "jumping"

        if self.vel.y > 0.5:
            self.state = "falling"

        self.animate()

        # apply friction
        self.acc.x += self.vel.x * self.PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        self.pos += self.vel + self.PLAYER_ACC * self.acc
        # wrap around the sides of the screen
        if self.pos.x > self.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.WIDTH

        self.rect.midbottom = self.pos

        # Update hitbox position
        self.hitbox.topleft = (self.rect.left + 10, self.rect.top + 7)

    def animate(self):
        """Handle player animations based on the current state."""

        if self.state == "idle":
            if self.animation_timer % 20 == 0:
                if self.playerleft:
                    self.frame_index = (self.frame_index + 1) % len(
                        self.idle_left_frames
                    )
                    self.image = self.idle_left_frames[self.frame_index]
                    self.animation_timer = 0
                else:
                    self.frame_index = (self.frame_index + 1) % len(
                        self.idle_right_frames
                    )
                    self.image = self.idle_right_frames[self.frame_index]
                    self.animation_timer = 0

        if self.state == "moving" and not self.playerleft:
            if self.animation_timer % 6 == 0:  # Change frame every 0.1 seconds
                self.frame_index = (self.frame_index + 1) % len(self.walk_right_frames)
                self.image = self.walk_right_frames[self.frame_index]
                self.animation_timer = 0

        if self.state == "moving" and self.playerleft:
            if self.animation_timer % 6 == 0:  # Change frame every 0.1 seconds
                self.frame_index = (self.frame_index + 1) % len(self.walk_left_frames)
                self.image = self.walk_left_frames[self.frame_index]
                self.animation_timer = 0

        if self.state == "jumping":
            if self.playerleft:
                self.image = self.jumping_left_frames[0]
            else:
                self.image = self.jumping_right_frames[0]

        if self.state == "falling":
            if self.playerleft:
                self.image = self.falling_left_frames[0]
            else:
                self.image = self.falling_right_frames[0]

    def load_character(self):
        """Load the character frames for the player without a hat."""

        self.idle_left_frames = [
            self.spritesheet.parse_sprite("idlel1.png"),
            self.spritesheet.parse_sprite("idlel2.png"),
        ]
        self.idle_right_frames = [
            self.spritesheet.parse_sprite("idler1.png"),
            self.spritesheet.parse_sprite("idler2.png"),
        ]
        self.walk_left_frames = [
            self.spritesheet.parse_sprite("wl1.png"),
            self.spritesheet.parse_sprite("wl2.png"),
            self.spritesheet.parse_sprite("wl3.png"),
            self.spritesheet.parse_sprite("wl4.png"),
        ]
        self.walk_right_frames = [
            self.spritesheet.parse_sprite("wr1.png"),
            self.spritesheet.parse_sprite("wr2.png"),
            self.spritesheet.parse_sprite("wr3.png"),
            self.spritesheet.parse_sprite("wr4.png"),
        ]
        self.jumping_left_frames = [self.spritesheet.parse_sprite("jumpingl.png")]
        self.jumping_right_frames = [self.spritesheet.parse_sprite("jumpingr.png")]
        self.falling_left_frames = [self.spritesheet.parse_sprite("fallingl.png")]
        self.falling_right_frames = [self.spritesheet.parse_sprite("fallingr.png")]

    def load_hat_character(self):
        """Load the character frames for the player with a hat."""

        self.idle_left_frames = [
            self.spritesheet.parse_sprite("idlel1.png"),
            self.spritesheet.parse_sprite("idlel2.png"),
        ]
        self.idle_right_frames = [
            self.spritesheet.parse_sprite("idler1.png"),
            self.spritesheet.parse_sprite("idler2.png"),
        ]
        self.walk_left_frames = [
            self.spritesheet.parse_sprite("wl1.png"),
            self.spritesheet.parse_sprite("wl2.png"),
            self.spritesheet.parse_sprite("wl3.png"),
            self.spritesheet.parse_sprite("wl4.png"),
        ]
        self.walk_right_frames = [
            self.spritesheet.parse_sprite("wr1.png"),
            self.spritesheet.parse_sprite("wr2.png"),
            self.spritesheet.parse_sprite("wr3.png"),
            self.spritesheet.parse_sprite("wr4.png"),
        ]
        self.jumping_left_frames = [self.spritesheet.parse_sprite("jumpingl.png")]
        self.jumping_right_frames = [self.spritesheet.parse_sprite("jumpingr.png")]
        self.falling_left_frames = [self.spritesheet.parse_sprite("fallingl.png")]
        self.falling_right_frames = [self.spritesheet.parse_sprite("fallingr.png")]

        for frame in self.idle_left_frames:
            frame.blit(self.hat_image1, (0, -8))

        for frame in self.idle_right_frames:
            frame.blit(self.hat_image1, (10, -8))

        for frame in self.walk_left_frames:
            frame.blit(self.hat_image1, (0, -8))

        for frame in self.walk_right_frames:
            frame.blit(self.hat_image1, (10, -8))

        for frame in self.jumping_left_frames:
            frame.blit(self.hat_image1, (0, -8))

        for frame in self.jumping_right_frames:
            frame.blit(self.hat_image1, (10, -8))

        for frame in self.falling_left_frames:
            frame.blit(self.hat_image1, (0, -8))

        for frame in self.falling_right_frames:
            frame.blit(self.hat_image1, (10, -8))

    def update_power_ups(self):
        """Update all active power-up timers"""
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            
        if self.jump_boost_timer > 0:
            self.jump_boost_timer -= 1
            
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.shield_active = False
                
        if self.double_jump_timer > 0:
            self.double_jump_timer -= 1
            if self.double_jump_timer == 0:
                self.has_double_jump = False
                
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
                
    def add_speed_boost(self, duration):
        """Add speed boost power-up"""
        self.speed_boost_timer = max(self.speed_boost_timer, duration)
        
    def add_jump_boost(self, duration):
        """Add jump boost power-up"""
        self.jump_boost_timer = max(self.jump_boost_timer, duration)
        
    def add_shield(self, duration):
        """Add shield power-up"""
        self.shield_timer = max(self.shield_timer, duration)
        self.shield_active = True
        
    def add_double_jump(self, duration):
        """Add double jump power-up"""
        self.double_jump_timer = max(self.double_jump_timer, duration)
        self.has_double_jump = True
        
    def add_health(self):
        """Add health/extra life"""
        self.health = min(self.health + 1, self.max_health)
        
    def add_coins(self, amount):
        """Add coins to player"""
        self.coins += amount
        
    def take_damage(self):
        """Take damage if not shielded and not invincible"""
        if not self.shield_active and self.invincible_timer <= 0:
            self.health -= 1
            self.invincible_timer = self.invincible_duration
            return True
        return False
        
    def is_dead(self):
        """Check if player is dead"""
        return self.health <= 0
        
    def get_active_effects(self):
        """Get list of active power-up effects for UI display"""
        effects = []
        if self.speed_boost_timer > 0:
            effects.append(("Speed", self.speed_boost_timer))
        if self.jump_boost_timer > 0:
            effects.append(("Jump", self.jump_boost_timer))
        if self.shield_timer > 0:
            effects.append(("Shield", self.shield_timer))
        if self.double_jump_timer > 0:
            effects.append(("Double Jump", self.double_jump_timer))
        return effects
    
    def is_invincible(self):
        """Check if player is currently invincible"""
        return self.invincible_timer > 0
        
    def should_flash(self):
        """Check if player should flash during invincibility"""
        return self.invincible_timer > 0 and (self.invincible_timer // 5) % 2 == 0
    
    def apply_knockback(self, direction_x):
        """Apply knockback when taking damage"""
        knockback_force = 8
        self.vel.x = direction_x * knockback_force
        self.vel.y = -3  # Small upward knockback
