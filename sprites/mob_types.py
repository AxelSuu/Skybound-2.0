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
from sprites.base import PhysicsSprite


def _crop(surf):
    """Crop a Surface to its non-transparent bounding box.

    The new enemy sprite cells are 4× padded — the visible character sits
    centred inside a larger transparent canvas.  Cropping makes the logical
    rect match the visible art so collision hitboxes stay tight.
    """
    bb = surf.get_bounding_rect()
    if bb.width == 0 or bb.height == 0:
        return surf  # fully transparent — return as-is to avoid zero-size subsurface
    return surf.subsurface(bb).copy()


class BaseMob(PhysicsSprite):
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
        # Initialize the shared physics base (pos/vel/acc, ACC, FRICTION,
        # WIDTH, HEIGHT, on_floor). Enemies use the same tuning as the player.
        super().__init__(acc=0.5, friction=-0.12)

        # Set up asset paths
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )

        # Anchor world position at the requested spawn point
        self.pos = pg.Vector2(x, y)

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
        """Basic gravity update (no friction) shared by the simpler mobs."""
        self.apply_gravity()


class ChaserMob(BaseMob):
    """Mob that chases the player (original behavior)"""
    def __init__(self, x=440, y=450):
        super().__init__(x, y)
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
        self.acc = pg.Vector2(0, self.ACC)
        self.animation_timer += 2

        if self.animation_timer % 20 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.image = self.walk_frames[self.frame_index]

        # Friction-based motion + screen wrap + rect/hitbox sync (shared base)
        self.apply_physics()

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

        # Load animated spritesheet; crop cells to tight visible art.
        self.spritesheet = Spritesheet("Patrolsheet.png")
        self.walk_frames = [
            _crop(self.spritesheet.parse_sprite("patrol1.png")),
            _crop(self.spritesheet.parse_sprite("patrol2.png")),
        ]
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(
            self.rect.left, self.rect.top, self.rect.width, self.rect.height
        )

    def update(self, player_pos=None):
        # Animate walk cycle
        self.animation_timer += 1
        if self.animation_timer % 12 == 0:
            self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.image = self.walk_frames[self.frame_index]

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

        # Load animated spritesheet; crop cells to tight visible art.
        # Frame 0 = squashed (grounded), frame 1 = stretched (airborne).
        self.spritesheet = Spritesheet("Jumpersheet.png")
        self.walk_frames = [
            _crop(self.spritesheet.parse_sprite("jumper1.png")),
            _crop(self.spritesheet.parse_sprite("jumper2.png")),
        ]
        self.image = self.walk_frames[0]
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

        # Frame 0 = grounded/squashed, frame 1 = airborne/stretched
        self.image = self.walk_frames[0 if self.on_floor else 1]

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
        self.fire_pose_timer = 0  # frames remaining to show the firing pose

        # Load animated spritesheet; crop cells to tight visible art.
        # Frame 0 = idle, frame 1 = firing pose (shown briefly after a shot).
        self.spritesheet = Spritesheet("Shootersheet.png")
        self.walk_frames = [
            _crop(self.spritesheet.parse_sprite("shooter1.png")),
            _crop(self.spritesheet.parse_sprite("shooter2.png")),
        ]
        self.image = self.walk_frames[0]
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
            self.fire_pose_timer = 10  # show firing frame for 10 ticks

        # Show firing frame briefly after a shot, then revert to idle.
        if self.fire_pose_timer > 0:
            self.fire_pose_timer -= 1
            self.image = self.walk_frames[1]
        else:
            self.image = self.walk_frames[0]

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


class DiveBomberMob(BaseMob):
    """Hovers at altitude and periodically dive-bombs toward the player."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hover_y = y
        self.target_x = None
        self.state = "hover"
        self.dive_interval = random.randint(90, 150)
        self.dive_duration = 35

        self.image = pg.Surface((34, 26), pg.SRCALPHA)
        pg.draw.polygon(self.image, (255, 140, 0), [(0, 0), (34, 0), (17, 26)])  # arrow/dart
        pg.draw.polygon(self.image, (120, 50, 0), [(0, 0), (34, 0), (17, 26)], 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)

    def update(self, player_pos=None):
        self.ai_timer += 1
        if player_pos is not None:
            self.target_x = player_pos.x

        if self.state == "hover":
            # Ease back toward hover altitude and drift slowly toward the player.
            self.vel.y += (self.hover_y - self.pos.y) * 0.02
            self.vel.y *= 0.85
            if self.target_x is not None:
                self.vel.x = max(-1.2, min(1.2, (self.target_x - self.pos.x) * 0.03))
            # Commit to a dive once the timer is up and the player is below.
            if self.ai_timer >= self.dive_interval and (
                player_pos is None or player_pos.y > self.pos.y
            ):
                self.state = "dive"
                self.ai_timer = 0
                self.vel.y = 9.0
                if self.target_x is not None:
                    self.vel.x = max(-3.0, min(3.0, (self.target_x - self.pos.x) * 0.1))
        else:  # diving
            self.vel.y += 0.5  # accelerate downward
            if self.ai_timer >= self.dive_duration or self.on_floor:
                self.state = "hover"
                self.ai_timer = 0

        self.pos += self.vel
        self._wrap_and_sync()


class BossMob(BaseMob):
    """A large boss that hovers near the top firing telegraphed spread shots.

    The player cannot attack it (the game is dodge-and-climb); the boss is an
    obstacle to survive on the way to the goal. It winds up visibly (telegraph)
    before each volley so attacks can be read and dodged.
    """
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 5  # conceptual; reserved for a future stomp/attack mechanic
        self.hover_y = y
        self.move_speed = 1.6
        self.last_player_pos = None
        self.projectiles = pg.sprite.Group()
        self.shoot_timer = 0
        self.shoot_interval = 140
        self.telegraph_frames = 35
        self.charging = False

        # Load boss spritesheet; crop to visible art for a tight collision rect.
        spritesheet = Spritesheet("Bosssheet.png")
        self._base_image = _crop(spritesheet.parse_sprite("boss_idle.png"))
        self._charge_image = _crop(spritesheet.parse_sprite("boss_charge.png"))
        self.image = self._base_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hitbox = pg.Rect(self.rect.left, self.rect.top, self.rect.width, self.rect.height)

    def update(self, player_pos=None):
        if player_pos is not None:
            self.last_player_pos = player_pos

        # Slow horizontal tracking and gentle hover.
        if self.last_player_pos is not None:
            self.vel.x = max(
                -self.move_speed,
                min(self.move_speed, (self.last_player_pos.x - self.pos.x) * 0.01),
            )
        self.vel.y += (self.hover_y - self.pos.y) * 0.01
        self.vel.y *= 0.9

        # Attack cycle with a visible telegraph before each volley.
        self.shoot_timer += 1
        self.charging = self.shoot_timer >= (self.shoot_interval - self.telegraph_frames)
        if self.shoot_timer >= self.shoot_interval:
            self._shoot_spread()
            self.shoot_timer = 0
            self.charging = False

        self.image = self._charge_image if self.charging else self._base_image
        self.projectiles.update()

        self.pos += self.vel
        self._wrap_and_sync()

    def _shoot_spread(self):
        """Fire a fan of projectiles aimed around the player's position."""
        if self.last_player_pos is None:
            return
        for dx in (-70, -25, 25, 70):
            target = pg.Vector2(self.last_player_pos.x + dx, self.last_player_pos.y)
            self.projectiles.add(Projectile(self.pos.x, self.pos.y, target))


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
        mob_types = [ChaserMob, PatrolMob, JumperMob, ShooterMob, DiveBomberMob]
        return random.choice(mob_types)(x, y)
