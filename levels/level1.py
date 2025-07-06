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
        self.sky = random.choice(self.skys)
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

        # Enhanced difficulty scaling
        base_platforms = 4
        extra_platforms = min(current_level // 3, 4)  # Add platforms every 3 levels, max 4 extra
        num_platforms = base_platforms + extra_platforms
        
        # Adjust platform spacing based on difficulty
        min_spacing = max(120, 180 - (current_level * 5))  # Closer platforms on higher levels
        max_spacing = min(220, 160 + (current_level * 5))  # But not too close
        
        platforms = []
        for plat in range(num_platforms):
            width = random.randint(max(40, 80 - current_level), min(120, 80 + current_level))
            height = 20
            x = random.randint(0, self.WIDTH - width)
            y = random.randint(40, self.HEIGHT - height - 300)
            platform = Platform2(x, y, width, height)
            platforms.append(platform)

        # Sort platforms by y-coordinate
        platforms.sort(key=lambda p: p.rect.y)

        # Adjust y-coordinates to ensure proper spacing
        for i in range(1, len(platforms)):
            min_gap = min_spacing
            max_gap = max_spacing
            
            if platforms[i].rect.y - platforms[i - 1].rect.y > max_gap:
                platforms[i].rect.y = platforms[i - 1].rect.y + max_gap
            elif platforms[i].rect.y - platforms[i - 1].rect.y < min_gap:
                platforms[i].rect.y = platforms[i - 1].rect.y + min_gap

        # Adjust x-coordinates to ensure reachability
        for i in range(1, len(platforms)):
            max_horizontal_distance = 150  # Maximum jump distance
            if abs(platforms[i].rect.centerx - platforms[i - 1].rect.centerx) > max_horizontal_distance:
                # Move platform closer to previous one
                if platforms[i].rect.centerx < platforms[i - 1].rect.centerx:
                    platforms[i].rect.x = max(0, platforms[i - 1].rect.centerx - max_horizontal_distance - platforms[i].rect.width // 2)
                else:
                    platforms[i].rect.x = min(self.WIDTH - platforms[i].rect.width, 
                                            platforms[i - 1].rect.centerx + max_horizontal_distance - platforms[i].rect.width // 2)

        # Final boundary checks
        for platform in platforms:
            if platform.rect.y > self.HEIGHT - 160:
                platform.rect.y = self.HEIGHT - 160
            if platform.rect.x > self.WIDTH - 80:
                platform.rect.x = self.WIDTH - 80
            if platform.rect.x < 0:
                platform.rect.x = 0

        # Add platforms to the game
        for platform in platforms:
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
