#!/usr/bin/env python3
"""
Skybound Level Generation System

This module handles the creation and management of game levels, including:
- Static level design for Level 1 (tutorial/introduction)
- Procedural level generation for subsequent levels
- Dynamic difficulty scaling based on player progression
- Enemy placement and spawn logic
- Platform layout optimization for gameplay flow

The level system uses a hybrid approach:
- Level 1 is hand-crafted for consistent player introduction
- Level 2+ are procedurally generated with increasing complexity
- All levels ensure playability through reachability algorithms

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
import random
import math

# Import game sprites and components
from sprites.player import Player
from sprites.platform import Platform2
from sprites.goal import Goal
from sprites.mob import Mob
from sprites.mob_types import create_random_mob
from sprites.pausebutton import Closebutton
from constants import MAX_REACH_V, MAX_REACH_H
from levels.themes import theme_for_level, apply_tint


def build_reachable_platforms(num_platforms, current_level, width, height, rng=random):
    """Generate a platform layout that is guaranteed climbable.

    Platforms are built upward from the floor, each placed within a single
    jump (MAX_REACH_V vertically, MAX_REACH_H horizontally) of the one below,
    so the level is always completable by construction. This replaces the old
    "scatter randomly, then nudge" approach which could leave gaps larger than
    the player's ~132px jump height.

    Args:
        num_platforms: how many platforms to attempt (above the floor).
        current_level: difficulty driver (bigger gaps / narrower platforms).
        width, height: screen dimensions.
        rng: random source (injectable for deterministic tests).

    Returns:
        list[pygame.Rect] sorted top-to-bottom (index 0 = highest, where the
        goal goes), excluding the floor platform.
    """
    floor_top = height - 40
    # Difficulty: gaps trend larger and platforms narrower as levels climb,
    # but always stay within the reachable budget.
    min_gap = min(70 + current_level * 3, MAX_REACH_V - 10)
    max_w = max(50, 120 - current_level * 3)
    min_w = max(36, 80 - current_level * 3)

    plats = []
    prev_cx = width // 2
    prev_y = floor_top
    for _ in range(num_platforms):
        gap = rng.randint(min_gap, MAX_REACH_V)
        y = prev_y - gap
        if y < 60:  # reached the top of the play area
            break
        w = rng.randint(min(min_w, max_w), max(min_w, max_w))
        h = 20
        # Horizontal offset within reach, kept fully on screen.
        cx = prev_cx + rng.randint(-MAX_REACH_H, MAX_REACH_H)
        cx = max(w // 2, min(width - w // 2, cx))
        plats.append(pg.Rect(cx - w // 2, y, w, h))
        prev_cx, prev_y = cx, y

    plats.sort(key=lambda r: r.y)  # highest first
    return plats


class LevelClass:
    """
    Level creation and management system for Skybound.
    
    This class handles both static and procedural level generation:
    
    Static Level (Level 1):
    - Hand-crafted introductory level
    - Consistent platform placement for learning
    - Single enemy for basic combat introduction
    
    Procedural Levels (Level 2+):
    - Algorithm-generated platform layouts
    - Dynamic difficulty scaling based on level number
    - Multiple enemy types with strategic placement
    - Reachability verification to ensure completability
    
    The procedural generation uses several algorithms:
    - Platform spacing optimization for jump distances
    - Enemy placement with safety zones around player/goal
    - Difficulty ramping through enemy count and platform complexity
    
    Attributes:
        game: Reference to the main game loop instance
        img_folder_path: Path to game image assets
        WIDTH/HEIGHT: Screen dimensions for level boundaries
        skys: List of background images for visual variety
        sky: Currently selected background image
    """
    def __init__(self, game):
        """
        Initialize the level creation system.
        
        Args:
            game: Reference to the main game loop instance
            
        This initialization:
        1. Sets up paths to game assets (images, backgrounds)
        2. Defines screen dimensions for level boundaries
        3. Loads multiple background images for visual variety
        4. Stores reference to game instance for sprite management
        """
        # Store reference to main game instance
        self.game = game
        
        # Set up asset paths
        self.img_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "imgs")
        )
        
        # Define screen dimensions for level creation
        self.WIDTH = 480
        self.HEIGHT = 600
        
        # Load background images for visual variety across levels
        self.skys = [
            pg.image.load(
                os.path.join(self.img_folder_path, "sky2.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky5.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky2.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky3.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky4.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky14.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky15.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky7.png")
            ).convert_alpha(),
            pg.image.load(
                os.path.join(self.img_folder_path, "Freesky8.png")
            ).convert_alpha(),
        ]
        
        # Set default background
        self.sky = self.skys[0]
        self.theme = None
        self._sky_cache = {}

    def _load_sky(self, filename):
        """Load (and cache) a themed background image by filename."""
        if filename not in self._sky_cache:
            self._sky_cache[filename] = pg.image.load(
                os.path.join(self.img_folder_path, filename)
            ).convert_alpha()
        return self._sky_cache[filename]

    def level1(self):
        # Create level 1 (static)
        self.game.all_sprites = pg.sprite.Group()
        self.game.platforms = pg.sprite.Group()
        self.game.goals = pg.sprite.Group()
        
        # Preserve existing player or create new one
        if not hasattr(self.game, 'player') or self.game.player is None:
            self.game.player = Player()
        else:
            # Reset player position for new level
            self.game.player.pos = pg.Vector2(30, self.HEIGHT * 3 / 4)
            self.game.player.rect.center = self.game.player.pos
            self.game.player.vel = pg.Vector2(0, 0)
            self.game.player.on_floor = False
            
        self.game.all_sprites.add(self.game.player)
        self.game.closebutton = Closebutton(10, 10, 50, 50)
        self.game.all_sprites.add(self.game.closebutton)
        self.game.mobs = pg.sprite.Group()
        
        # Create mob at a safe distance from player and goal
        # Player is at (30, HEIGHT * 3 / 4), goal will be at (WIDTH / 2 - 100, 60)
        # Place mob on the right side of the screen to avoid conflicts
        mob_x = self.WIDTH - 80  # Right side of screen
        mob_y = self.HEIGHT * 3 / 4 + 10
        self.game.mob = create_random_mob(mob_x, mob_y, 1)  # Level 1 mob
        self.game.all_sprites.add(self.game.mob)
        self.game.mobs.add(self.game.mob)

        p1 = Platform2(0, self.HEIGHT - 40, self.WIDTH, 40)
        self.game.all_sprites.add(p1)
        self.game.platforms.add(p1)
        p2 = Platform2(self.WIDTH / 2 - 50, self.HEIGHT * 3 / 4, 100, 20)
        self.game.all_sprites.add(p2)
        self.game.platforms.add(p2)
        p3 = Platform2(self.WIDTH / 2 - 150, self.HEIGHT * 3 / 6, 100, 20)
        self.game.all_sprites.add(p3)
        self.game.platforms.add(p3)
        p4 = Platform2(self.WIDTH / 2 + 100, self.HEIGHT * 3 / 9, 100, 20)
        self.game.all_sprites.add(p4)
        self.game.platforms.add(p4)
        p5 = Platform2(self.WIDTH / 2 - 100, 100, 100, 20)
        self.game.all_sprites.add(p5)
        self.game.platforms.add(p5)
        goal = Goal(self.WIDTH / 2 - 100, 60, 20, 20)
        self.game.all_sprites.add(goal)
        self.game.goals.add(goal)

    def level2(self):
        # Create level 2 (randomly generated with enhanced difficulty scaling)
        from utils.database_logic import GetScore
        
        current_level = GetScore()
        # Pick the biome for this level and bake its tint onto the background.
        self.theme = theme_for_level(current_level)
        self.sky = apply_tint(self._load_sky(self.theme["sky"]), self.theme["tint"])
        self.game.all_sprites = pg.sprite.Group()
        self.game.platforms = pg.sprite.Group()
        self.game.goals = pg.sprite.Group()
        
        # Preserve existing player stats but reset position and physics
        if not hasattr(self.game, 'player') or self.game.player is None:
            self.game.player = Player()
        else:
            # Reset player position and physics for new level
            self.game.player.pos = pg.Vector2(30, self.HEIGHT * 3 / 4)
            self.game.player.rect.center = self.game.player.pos
            self.game.player.vel = pg.Vector2(0, 0)
            self.game.player.on_floor = False
            # Keep health, coins, and other progress
            
        self.game.all_sprites.add(self.game.player)
        self.game.closebutton = Closebutton(10, 10, 50, 50)
        self.game.all_sprites.add(self.game.closebutton)
        self.game.mobs = pg.sprite.Group()

        # Create floor Platform
        p1 = Platform2(0, self.HEIGHT - 40, self.WIDTH, 40)
        self.game.all_sprites.add(p1)
        self.game.platforms.add(p1)

        # Build a reachable platform layout (guaranteed climbable by construction)
        base_platforms = 4
        extra_platforms = min(current_level // 3, 4)  # +1 every 3 levels, max +4
        num_platforms = base_platforms + extra_platforms

        platform_rects = build_reachable_platforms(
            num_platforms, current_level, self.WIDTH, self.HEIGHT
        )
        platforms = []
        for r in platform_rects:
            platform = Platform2(r.x, r.y, r.width, r.height)
            platforms.append(platform)
            self.game.all_sprites.add(platform)
            self.game.platforms.add(platform)

        # Create multiple mobs based on level
        num_mobs = min(1 + current_level // 4, 3)  # 1 mob initially, +1 every 4 levels, max 3
        
        # Player spawn position
        player_spawn_x = 30
        player_spawn_y = self.HEIGHT * 3 / 4
        
        # Place the goal on the highest platform first
        goal_platform = platforms[0]  # Already sorted by y-coordinate
        goal_x = goal_platform.rect.centerx - 10
        goal_y = goal_platform.rect.top - 20

        # Ensure the goal is within screen boundaries
        goal_x = max(0, min(self.WIDTH - 20, goal_x))
        goal_y = max(0, min(self.HEIGHT - 60, goal_y))

        goal = Goal(goal_x, goal_y, 20, 20)
        self.game.all_sprites.add(goal)
        self.game.goals.add(goal)
        
        def is_safe_spawn_position(x, y, min_distance=100):
            """Check if a spawn position is safe (not too close to player or goal)"""
            # Check distance from player
            player_distance = math.sqrt((x - player_spawn_x)**2 + (y - player_spawn_y)**2)
            if player_distance < min_distance:
                return False
            
            # Check distance from goal
            goal_distance = math.sqrt((x - goal_x)**2 + (y - goal_y)**2)
            if goal_distance < min_distance:
                return False
            
            return True
        
        for i in range(num_mobs):
            max_attempts = 20  # Prevent infinite loops
            attempts = 0
            mob_spawned = False
            
            while attempts < max_attempts and not mob_spawned:
                if i == 0:
                    # First mob - try default position first, then find alternative
                    if attempts == 0:
                        mob_x = 440
                        mob_y = self.HEIGHT * 3 / 4 + 10
                    else:
                        # Find alternative position on a random platform
                        if platforms:
                            spawn_platform = random.choice(platforms)
                            mob_x = spawn_platform.rect.centerx
                            mob_y = spawn_platform.rect.top - 50
                        else:
                            mob_x = random.randint(50, self.WIDTH - 50)
                            mob_y = self.HEIGHT // 2
                else:
                    # Additional mobs spawn on random platforms
                    if platforms:
                        spawn_platform = random.choice(platforms)
                        mob_x = spawn_platform.rect.centerx + random.randint(-30, 30)
                        mob_y = spawn_platform.rect.top - 50
                        
                        # Keep mob within platform bounds
                        mob_x = max(spawn_platform.rect.left + 20, 
                                   min(spawn_platform.rect.right - 20, mob_x))
                    else:
                        mob_x = random.randint(50, self.WIDTH - 50)
                        mob_y = self.HEIGHT // 2
                
                # Check if the position is safe
                if is_safe_spawn_position(mob_x, mob_y):
                    mob = create_random_mob(mob_x, mob_y, current_level)
                    self.game.all_sprites.add(mob)
                    self.game.mobs.add(mob)
                    mob_spawned = True
                
                attempts += 1
            
            # If we couldn't find a safe position, spawn at a fallback location
            if not mob_spawned:
                # Use the rightmost side of the screen as fallback
                fallback_x = self.WIDTH - 60
                fallback_y = self.HEIGHT - 100
                mob = create_random_mob(fallback_x, fallback_y, current_level)
                self.game.all_sprites.add(mob)
                self.game.mobs.add(mob)
        
        # Add some variety to higher levels
        if current_level > 5:
            # Add moving platforms (we'll implement this as a subclass)
            self.add_special_platforms(current_level)
            
    def add_special_platforms(self, level):
        """Add special platform types for higher levels"""
        # For now, we'll just add some randomly positioned smaller platforms
        # In a full implementation, you could add moving platforms, disappearing platforms, etc.
        
        if level > 8:
            # Add some smaller, harder to reach platforms
            for _ in range(2):
                width = random.randint(30, 50)
                height = 20
                x = random.randint(0, self.WIDTH - width)
                y = random.randint(60, self.HEIGHT - 200)
                
                platform = Platform2(x, y, width, height)
                self.game.all_sprites.add(platform)
                self.game.platforms.add(platform)
