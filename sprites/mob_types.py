#!/usr/bin/env python3
"""
Skybound Advanced Enemy System

This module implements a comprehensive enemy system with multiple mob types,
each featuring unique AI behaviors, movement patterns, and characteristics.

The enemy system includes:
- Base mob class with common functionality
- Specialized enemy types with unique behaviors
- Scalable difficulty based on game progression
- Dynamic AI decision making
- Physics-based movement and collision
- Visual and audio feedback systems

Enemy Types:
- BasicMob: Simple horizontal movement
- JumperMob: Vertical jumping behavior
- ChaserMob: Actively pursues the player
- PatrolMob: Follows predefined patrol routes
- ShooterMob: Ranged attack capabilities (higher levels)

The system uses inheritance and composition to create diverse enemy
behaviors while maintaining code reusability and performance.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
import random
from utils.spritesheet import Spritesheet


class BaseMob(pg.sprite.Sprite):
    """
    Base class for all enemy types in the game.
    
    This class provides common functionality shared by all enemy types,
    including physics simulation, basic AI patterns, health management,
    and visual representation.
    
    Common Features:
    - Physics-based movement with gravity
    - Health and damage systems
    - Basic AI timing and decision making
    - Animation frame management
    - Collision detection preparation
    - Screen boundary handling
    
    All specific enemy types inherit from this class and override
    the update_ai method to implement their unique behaviors.
    
    Attributes:
        Physics System:
            pos (pg.Vector2): Current world position
            vel (pg.Vector2): Current velocity
            acc (pg.Vector2): Current acceleration
            on_floor (bool): Ground contact state
            
        AI System:
            ai_timer (int): Timer for AI decision making
            direction (int): Movement direction (1 = right, -1 = left)
            speed (float): Movement speed multiplier
            jump_strength (float): Jump force strength
            
        Visual System:
            frame_index (int): Current animation frame
            animation_timer (int): Animation timing counter
            
        Combat System:
            health (int): Current health points
    """
    
    def __init__(self, x, y):
        """
        Initialize the base mob with physics and AI systems.
        
        Args:
            x (float): Initial X coordinate
            y (float): Initial Y coordinate
            
        This initialization sets up:
        1. Pygame sprite functionality
        2. Physics vectors and constants
        3. AI timing and behavior variables
        4. Animation state management
        5. Combat and health systems
        """
        # Initialize pygame sprite base class
        pg.sprite.Sprite.__init__(self)
        
        # Set up asset paths
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Screen dimensions for boundary checking
        self.HEIGHT = 600
        self.WIDTH = 480
        
        # Physics system initialization
        self.pos = pg.Vector2(x, y)         # World position
        self.vel = pg.Vector2(0, 0)         # Current velocity
        self.acc = pg.Vector2(0, 0)         # Current acceleration
        self.on_floor = False               # Ground contact state
        
        # Animation system
        self.frame_index = 0                # Current animation frame
        self.animation_timer = 0            # Animation timing counter
        
        # Combat system
        self.health = 1                     # Health points
        
        # AI system
        self.speed = 1.0                    # Movement speed multiplier
        self.jump_strength = 10             # Jump force strength
        self.ai_timer = 0                   # AI decision timer
        self.direction = 1                  # Movement direction (1=right, -1=left)
        
    def update_physics(self):
        """Basic physics update for all mobs"""
        self.acc = pg.Vector2(0, 0.5)  # Gravity
        self.vel += self.acc
        self.pos += self.vel
        
        # Screen wrapping
        if self.pos.x > self.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.WIDTH
            
        self.rect.midbottom = self.pos
        self.hitbox.topleft = (self.rect.left, self.rect.top)


class ChaserMob(BaseMob):
    """Mob that chases the player (original behavior)"""
    def __init__(self, x=440, y=450):
        super().__init__(x, y)
        self.MOB_ACC = 0.5
        self.MOB_FRICTION = -0.12
        self.chase_speed = 1.4
        
        # Load the spritesheet
        self.spritesheet = Spritesheet("Mobsheet.png")
        self.walk_frames = [
            self.spritesheet.parse_sprite("midle1.png"),
            self.spritesheet.parse_sprite("mw1.png"),
            self.spritesheet.parse_sprite("midle2.png"),
            self.spritesheet.parse_sprite("mw2.png"),
        ]
        
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )
        
    def update(self, player_pos=None):
        self.acc = pg.Vector2(0, self.MOB_ACC)
        self.animation_timer += 2
        
        if self.animation_timer % 20 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.image = self.walk_frames[self.frame_index]
            
        # Apply friction and physics
        self.acc.x += self.vel.x * self.MOB_FRICTION
        self.vel += self.acc
        self.pos += self.vel + self.MOB_ACC * self.acc
        
        # Screen wrapping
        if self.pos.x > self.WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.WIDTH
            
        self.rect.midbottom = self.pos
        self.hitbox.topleft = (self.rect.left, self.rect.top)
        
    def chase_player(self, player_pos):
        """Chase behavior for player"""
        if player_pos.x < self.pos.x:
            self.vel.x = -self.chase_speed
        elif player_pos.x > self.pos.x:
            self.vel.x = self.chase_speed
            
        # Jump if player is higher
        if player_pos.y + 40 < self.pos.y and self.on_floor:
            self.vel.y = -self.jump_strength
            self.on_floor = False


class PatrolMob(BaseMob):
    """Mob that patrols back and forth"""
    def __init__(self, x, y, patrol_range=150):
        super().__init__(x, y)
        self.patrol_range = patrol_range
        self.start_x = x
        self.patrol_speed = 0.8
        self.direction = 1
        
        # Create a simple red rectangle for now (you can replace with sprites)
        self.image = pg.Surface((40, 40))
        self.image.fill((255, 100, 100))  # Red color
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )
        
    def update(self, player_pos=None):
        # Patrol behavior
        if abs(self.pos.x - self.start_x) > self.patrol_range:
            self.direction *= -1
            
        self.vel.x = self.patrol_speed * self.direction
        self.update_physics()


class JumperMob(BaseMob):
    """Mob that jumps periodically"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.jump_timer = 0
        self.jump_interval = random.randint(60, 120)  # Random jump timing
        
        # Create a simple green rectangle for now
        self.image = pg.Surface((35, 35))
        self.image.fill((100, 255, 100))  # Green color
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )
        
    def update(self, player_pos=None):
        self.jump_timer += 1
        
        # Jump periodically
        if self.jump_timer >= self.jump_interval and self.on_floor:
            self.vel.y = -8
            self.on_floor = False
            self.jump_timer = 0
            self.jump_interval = random.randint(60, 120)
            
        # Slight horizontal movement
        if random.randint(1, 100) == 1:
            self.vel.x = random.uniform(-1, 1)
            
        self.update_physics()


class ShooterMob(BaseMob):
    """Mob that shoots projectiles at the player"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.shoot_timer = 0
        self.shoot_interval = 120  # Shoot every 2 seconds at 60 FPS
        self.projectiles = pg.sprite.Group()
        self.last_player_pos = None
        
        # Create a simple blue rectangle for now
        self.image = pg.Surface((45, 45))
        self.image.fill((100, 100, 255))  # Blue color
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )
        
    def update(self, player_pos=None):
        self.shoot_timer += 1
        
        if player_pos:
            self.last_player_pos = player_pos
        
        # Shoot at player
        if (self.shoot_timer >= self.shoot_interval and 
            self.last_player_pos and 
            abs(self.last_player_pos.x - self.pos.x) < 200):
            
            self.shoot_at_player()
            self.shoot_timer = 0
            
        # Update projectiles
        self.projectiles.update()
        
        self.update_physics()
        
    def shoot_at_player(self):
        """Create a projectile towards the player"""
        if self.last_player_pos:
            projectile = Projectile(self.pos.x, self.pos.y, self.last_player_pos)
            self.projectiles.add(projectile)


class Projectile(pg.sprite.Sprite):
    """Simple projectile for shooter mobs"""
    def __init__(self, start_x, start_y, target_pos):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((8, 8))
        self.image.fill((255, 255, 0))  # Yellow projectile
        self.rect = self.image.get_rect()
        self.rect.center = (start_x, start_y)
        
        # Calculate direction to target
        direction = target_pos - pg.Vector2(start_x, start_y)
        if direction.length() > 0:
            direction = direction.normalize()
        
        self.vel = direction * 3  # Projectile speed
        self.pos = pg.Vector2(start_x, start_y)
        self.lifetime = 180  # 3 seconds at 60 FPS
        
    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        self.lifetime -= 1
        
        # Remove if off screen or lifetime expired
        if (self.lifetime <= 0 or self.pos.x < 0 or self.pos.x > 480 or 
            self.pos.y < 0 or self.pos.y > 600):
            self.kill()


def create_random_mob(x, y, level=1):
    """Factory function to create random mobs based on level"""
    if level == 1:
        return ChaserMob(x, y)
    elif level <= 3:
        mob_types = [ChaserMob, PatrolMob]
        return random.choice(mob_types)(x, y)
    elif level <= 5:
        mob_types = [ChaserMob, PatrolMob, JumperMob]
        return random.choice(mob_types)(x, y)
    else:
        mob_types = [ChaserMob, PatrolMob, JumperMob, ShooterMob]
        return random.choice(mob_types)(x, y)
