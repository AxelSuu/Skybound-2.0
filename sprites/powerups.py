#!/usr/bin/env python3
"""
Skybound Power-up System

This module implements a comprehensive power-up system with various collectible
items that provide temporary or permanent enhancements to the player.

Power-up Types:
- SpeedBoost: Increases player movement speed
- JumpBoost: Enhances jumping ability
- Shield: Provides temporary damage protection
- DoubleJump: Grants double jump ability
- HealthPotion: Restores player health
- CoinMagnet: Attracts nearby coins automatically

The power-up system includes:
- Animated floating effects for visual appeal
- Collision detection with the player
- Timed effects that expire naturally
- Visual feedback through particle effects
- Sound effects for collection feedback

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
import random
import math


class BasePowerUp(pg.sprite.Sprite):
    """
    Base class for all power-up items in the game.
    
    This class provides common functionality for all power-ups including:
    - Floating animation effects
    - Basic collision detection
    - Position management
    - Collection state tracking
    
    All specific power-up types inherit from this class and implement
    their own apply_effect method to define their unique functionality.
    
    Attributes:
        pos (pg.Vector2): Current world position
        collected (bool): Whether this power-up has been collected
        bounce_timer (int): Timer for floating animation
        original_y (float): Original Y position for bounce calculation
    """
    
    def __init__(self, x, y):
        """
        Initialize a power-up at the specified location.
        
        Args:
            x (float): X coordinate for spawn position
            y (float): Y coordinate for spawn position
        """
        pg.sprite.Sprite.__init__(self)
        self.pos = pg.Vector2(x, y)
        self.collected = False
        self.bounce_timer = 0
        self.original_y = y
        
    def update(self):
        """
        Update the power-up's animation and position.
        
        Creates a smooth floating effect using sine wave mathematics
        to make the power-up gently bob up and down, making it more
        visually appealing and easier to notice.
        """
        self.bounce_timer += 1
        # Create a floating effect using sine wave
        bounce_offset = 3 * math.sin(self.bounce_timer * 0.1)
        self.pos.y = self.original_y + bounce_offset
        self.rect.center = self.pos
        
    def collect(self, player):
        """Called when player collects this power-up"""
        self.collected = True
        self.kill()


class SpeedBoost(BasePowerUp):
    """Increases player speed temporarily"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 255, 0))  # Yellow
        # Draw a lightning bolt symbol
        pg.draw.polygon(self.image, (255, 255, 255), 
                       [(10, 2), (6, 8), (12, 8), (8, 18), (14, 12), (8, 12)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.effect_duration = 300  # 5 seconds at 60 FPS
        
    def collect(self, player):
        player.add_speed_boost(self.effect_duration)
        super().collect(player)


class JumpBoost(BasePowerUp):
    """Increases player jump height temporarily"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((20, 20))
        self.image.fill((0, 255, 0))  # Green
        # Draw an up arrow
        pg.draw.polygon(self.image, (255, 255, 255), 
                       [(10, 2), (6, 8), (14, 8)])
        pg.draw.rect(self.image, (255, 255, 255), (8, 8, 4, 10))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.effect_duration = 300
        
    def collect(self, player):
        player.add_jump_boost(self.effect_duration)
        super().collect(player)


class HealthPotion(BasePowerUp):
    """Restores player health or gives extra life"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 0, 0))  # Red
        # Draw a cross
        pg.draw.rect(self.image, (255, 255, 255), (8, 4, 4, 12))
        pg.draw.rect(self.image, (255, 255, 255), (4, 8, 12, 4))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def collect(self, player):
        player.add_health()
        super().collect(player)


class Coin(BasePowerUp):
    """Collectible coin for currency"""
    def __init__(self, x, y, value=1):
        super().__init__(x, y)
        self.value = value
        size = 12 + (value * 2)  # Bigger coins for higher values
        self.image = pg.Surface((size, size))
        color = (255, 215, 0) if value == 1 else (192, 192, 192) if value == 2 else (205, 127, 50)
        self.image.fill(color)
        # Draw a circle
        pg.draw.circle(self.image, (255, 255, 255), (size//2, size//2), size//2-2, 2)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def collect(self, player):
        player.add_coins(self.value)
        super().collect(player)


class Shield(BasePowerUp):
    """Temporary invincibility"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((20, 20))
        self.image.fill((0, 191, 255))  # Light blue
        # Draw a shield shape
        pg.draw.polygon(self.image, (255, 255, 255), 
                       [(10, 2), (4, 6), (4, 12), (10, 18), (16, 12), (16, 6)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.effect_duration = 1800  # 30 seconds
        
    def collect(self, player):
        player.add_shield(self.effect_duration)
        super().collect(player)


class DoubleJump(BasePowerUp):
    """Enables double jump temporarily"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 0, 255))  # Magenta
        # Draw two up arrows
        pg.draw.polygon(self.image, (255, 255, 255), 
                       [(7, 2), (4, 6), (10, 6)])
        pg.draw.polygon(self.image, (255, 255, 255), 
                       [(13, 8), (10, 12), (16, 12)])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.effect_duration = 240  # 4 seconds
        
    def collect(self, player):
        player.add_double_jump(self.effect_duration)
        super().collect(player)


class PowerUpManager:
    """Manages power-up spawning and collection"""
    def __init__(self):
        self.power_ups = pg.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 120  # 2 seconds at 60 FPS
        
    def update(self, platforms):
        """Update all power-ups and spawn new ones"""
        self.spawn_timer += 1
        self.power_ups.update()
        
        # Spawn new power-ups periodically
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_random_powerup(platforms)
            self.spawn_timer = 0
            
    def spawn_random_powerup(self, platforms):
        """Spawn a random power-up on a random platform"""
        if not platforms:
            return
            
        # Choose a random platform
        platform = random.choice(platforms.sprites())
        
        # Calculate x position, handling narrow platforms
        min_x = platform.rect.left + 20
        max_x = platform.rect.right - 20
        if min_x >= max_x:
            # Platform too narrow, use center instead
            x = platform.rect.centerx
        else:
            x = random.randint(min_x, max_x)
        
        y = platform.rect.top - 25
        
        # Choose random power-up type
        power_up_types = [SpeedBoost, JumpBoost, HealthPotion, Coin, Shield, DoubleJump]
        weights = [15, 15, 10, 30, 8, 12]  # Coins are most common
        
        power_up_class = random.choices(power_up_types, weights=weights)[0]
        
        # Special case for coins - sometimes spawn multiple
        if power_up_class == Coin:
            if random.randint(1, 5) == 1:  # 20% chance for silver coin
                power_up = Coin(x, y, 2)
            elif random.randint(1, 20) == 1:  # 5% chance for gold coin
                power_up = Coin(x, y, 3)
            else:
                power_up = Coin(x, y, 1)
        else:
            power_up = power_up_class(x, y)
            
        self.power_ups.add(power_up)
        
    def check_collisions(self, player):
        """Check for power-up collisions with player"""
        collected = pg.sprite.spritecollide(player, self.power_ups, False)
        for power_up in collected:
            power_up.collect(player)
            
    def draw(self, screen):
        """Draw all power-ups"""
        self.power_ups.draw(screen)
        
    def spawn_specific_powerup(self, power_up_type, x, y):
        """Spawn a specific power-up at given location"""
        power_up = power_up_type(x, y)
        self.power_ups.add(power_up)
        return power_up
