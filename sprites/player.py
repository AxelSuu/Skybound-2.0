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
from utils.database_logic import WearsHat, GetCoins, AddCoins
from utils.player_stats import player_stats
from utils.upgrades import apply_upgrades
from sprites.base import PhysicsSprite
from constants import (
    PLAYER_ACC,
    FRICTION,
    JUMP_VELOCITY,
    JUMP_BOOST_VELOCITY,
    START_HEALTH,
    MAX_HEALTH,
    INVINCIBILITY_FRAMES,
    COYOTE_FRAMES,
    JUMP_BUFFER_FRAMES,
)


class Player(PhysicsSprite):
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
        # Initialize the shared physics base (sets pos/vel/acc, ACC, FRICTION,
        # WIDTH, HEIGHT, on_floor).
        super().__init__(acc=PLAYER_ACC, friction=FRICTION)

        # Set up file paths for game assets
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Load character customization. The player wears the hat only when it
        # is both owned and equipped (see WearsHat) — owning it but selecting
        # "Normal" must show no hat.
        self.wears_hat = WearsHat()
        self.hat_image = pg.image.load(
            os.path.join(self.img_folder_path, "hat1.png")
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
        
        # Movement and physics state (pos/vel/acc, WIDTH, HEIGHT, ACC, FRICTION
        # are provided by PhysicsSprite).
        self.jump_pressed = False        # Jump key state last frame (edge detection)
        self.coyote_timer = 0            # Frames of grace to jump after leaving ground
        self.jump_buffer_timer = 0       # Frames a pending jump press stays buffered
        # Squash & stretch (purely visual): >0 squashes (land), <0 stretches (jump).
        self.squash = 0.0

        # Load animation spritesheet
        self.spritesheet = Spritesheet("Playersheet.png")
        
        # Load character animations, blitting the hat on if it's equipped.
        self.load_character(wear_hat=self.wears_hat)

        self.image = self.startframe  # Start with the first frame

        self.rect = (
            self.image.get_rect()
        )  # Set the rect attribute for collision detection
        self.rect.center = (30, self.HEIGHT * 3 / 4)  # Create center rect object
        self.seed_body(self.rect.center)  # Anchor pos/vel/acc at the spawn point

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
        self.magnet_timer = 0
        self.health = START_HEALTH
        self.max_health = MAX_HEALTH
        self.has_double_jump = False
        self.double_jump_used = False
        self.shield_active = False
        self.power_up_effects = []
        self.run_accel_mult = 1.0  # boosted by the move-speed shop upgrade

        # Load persistent stats, then layer permanent shop upgrades on top.
        player_stats.apply_stats_to_player(self)
        apply_upgrades(self)
        
        # Invincibility frames
        self.invincible_timer = 0
        self.invincible_duration = INVINCIBILITY_FRAMES  # ~2 seconds at 60 FPS

    def update(self):
        """Update the player's position, state, and animations."""

        self.acc = pg.Vector2(0, self.ACC)
        self.animation_timer += 1
        
        # Update power-up timers
        self.update_power_ups()

        keys = pg.key.get_pressed()

        if not keys[pg.K_LEFT] and not keys[pg.K_RIGHT] and self.on_floor:
            self.state = "idle"

        # Apply speed boost (temporary power-up) and the permanent move-speed upgrade
        speed_multiplier = 1.5 if self.speed_boost_timer > 0 else 1.0
        base_acc = self.ACC * speed_multiplier * self.run_accel_mult

        if keys[pg.K_LEFT]:
            self.acc.x = -base_acc
            self.state = "moving"
            self.playerleft = True

        if keys[pg.K_RIGHT]:
            self.acc.x = base_acc
            self.state = "moving"
            self.playerleft = False

        # Jumping with coyote time, jump buffering and double-jump support
        self._update_jump(keys[pg.K_SPACE])

        if self.vel.y < 0:
            self.state = "jumping"

        if self.vel.y > 0.5:
            self.state = "falling"

        self.animate()
        self._apply_squash()

        # Friction-based motion + screen wrap + rect/hitbox sync (shared base).
        # The hitbox is inset (+10, +7) from the sprite rect.
        self.apply_physics(hitbox_dx=10, hitbox_dy=7)

    def land(self):
        """Trigger the landing squash (called by the loop on ground contact)."""
        self.squash = 1.0

    def _apply_squash(self):
        """Apply and decay the squash/stretch deformation to the current frame.

        Purely visual: ``self.rect`` (the collision shape) is left untouched, so
        the scaled image is anchored by its midbottom at draw time to keep the
        feet planted. Uses pygame-ce ``transform.scale_by``.
        """
        if abs(self.squash) < 0.02:
            self.squash = 0.0
            return
        k = 0.3  # max deformation = 30%
        scale_x = 1.0 + k * self.squash
        scale_y = 1.0 - k * self.squash
        self.image = pg.transform.scale_by(self.image, (scale_x, scale_y))
        self.squash *= 0.75  # ease back to neutral

    def _update_jump(self, space_held):
        """Resolve jumping with coyote time and jump buffering.

        Args:
            space_held (bool): whether the jump key is down this frame.

        Coyote time lets the player jump for a few frames after walking off a
        ledge; jump buffering remembers a press made just before landing so it
        fires the instant the ground is touched. Both are classic platformer
        "game feel" affordances. Double-jump (a power-up) is unchanged.
        """
        # Refresh the coyote window while genuinely resting on the ground.
        if self.on_floor and self.vel.y == 0:
            self.coyote_timer = COYOTE_FRAMES
        elif self.coyote_timer > 0:
            self.coyote_timer -= 1

        # Buffer the jump press on the key-down edge, then let it decay.
        space_pressed_edge = space_held and not self.jump_pressed
        if space_pressed_edge:
            self.jump_buffer_timer = JUMP_BUFFER_FRAMES
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        jump_strength = JUMP_BOOST_VELOCITY if self.jump_boost_timer > 0 else JUMP_VELOCITY

        if self.jump_buffer_timer > 0 and self.coyote_timer > 0:
            # Ground (or coyote-grace) jump.
            self.vel.y = jump_strength
            self.on_floor = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            self.double_jump_used = False
            self.squash = -1.0  # stretch on take-off
        elif (
            space_pressed_edge
            and self.has_double_jump
            and not self.double_jump_used
            and not self.on_floor
            and self.vel.y > -8
        ):
            # Mid-air double jump (power-up). Requires a fresh press.
            self.vel.y = jump_strength
            self.double_jump_used = True

        # Remember the key state for next-frame edge detection.
        self.jump_pressed = space_held

    def animate(self):
        """Handle player animations based on the current state.

        Always reassigns ``self.image`` to a clean (unscaled) frame so that the
        squash/stretch pass downstream never compounds on an already-deformed
        surface. Frame advancement is still gated per state.
        """
        # Pick the active frame list for the current state and facing, plus how
        # often to advance the frame (None = single-frame poses).
        if self.state == "moving":
            frames = self.walk_left_frames if self.playerleft else self.walk_right_frames
            gate = 6
        elif self.state == "jumping":
            frames = self.jumping_left_frames if self.playerleft else self.jumping_right_frames
            gate = None
        elif self.state == "falling":
            frames = self.falling_left_frames if self.playerleft else self.falling_right_frames
            gate = None
        else:  # idle (and any fallback)
            frames = self.idle_left_frames if self.playerleft else self.idle_right_frames
            gate = 20

        if gate is not None and self.animation_timer % gate == 0:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.animation_timer = 0

        # Clamp the shared frame index in case we just switched frame lists.
        self.image = frames[self.frame_index % len(frames)]

    def load_character(self, wear_hat=False):
        """Load the player's animation frames from the spritesheet.

        When ``wear_hat`` is True the hat is blitted onto every frame; otherwise
        the bare character is used.
        """
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

        if wear_hat:
            self._apply_hat()

    def _apply_hat(self):
        """Blit the hat onto every animation frame.

        Left-facing frames anchor the hat at x=0, right-facing at x=10, so it
        tracks the character's head in both directions.
        """
        left_groups = (
            self.idle_left_frames,
            self.walk_left_frames,
            self.jumping_left_frames,
            self.falling_left_frames,
        )
        right_groups = (
            self.idle_right_frames,
            self.walk_right_frames,
            self.jumping_right_frames,
            self.falling_right_frames,
        )
        for group in left_groups:
            for frame in group:
                frame.blit(self.hat_image, (0, -8))
        for group in right_groups:
            for frame in group:
                frame.blit(self.hat_image, (10, -8))

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

        if self.magnet_timer > 0:
            self.magnet_timer -= 1

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

    def add_max_health(self):
        """Permanently raise the max health by one and heal into it (Extra Life)."""
        self.max_health += 1
        self.health += 1

    def add_magnet(self, duration):
        """Activate the coin magnet for a number of frames."""
        self.magnet_timer = max(self.magnet_timer, duration)
        
    @property
    def coins(self):
        """The single coin wallet (shared with the shop, persisted in save.json)."""
        return GetCoins()

    def add_coins(self, amount):
        """Add coins to the wallet."""
        AddCoins(amount)
        
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
        if self.magnet_timer > 0:
            effects.append(("Magnet", self.magnet_timer))
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
