#!/usr/bin/env python3
"""
Skybound Visual Effects System

This module provides a comprehensive visual effects system for enhancing
the gameplay experience with particle effects, screen shake, floating text,
and various visual feedback elements.

Effect Types:
- Particle Systems: Explosions, trails, ambient effects
- Screen Shake: Impact feedback and dramatic moments
- Floating Text: Damage numbers, coin collection, achievements
- Power-up Indicators: Visual feedback for temporary effects

The effects system is designed to be performant and visually appealing,
providing immediate feedback to player actions and game events.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import random
import math


class Particle:
    """
    Base particle class for all particle effects.
    
    Particles are small visual elements that create various effects like
    explosions, trails, sparks, and ambient atmosphere. Each particle
    has its own physics simulation including gravity, velocity, and lifetime.
    
    Attributes:
        x, y (float): Current position coordinates
        vel_x, vel_y (float): Velocity components
        color (tuple): RGB color values
        size (int): Particle size in pixels
        lifetime (int): Remaining frames before particle disappears
        max_lifetime (int): Original lifetime for fade calculations
        gravity (float): Downward acceleration per frame
    """
    
    def __init__(self, x, y, vel_x=0, vel_y=0, color=(255, 255, 255), size=3, lifetime=60):
        """
        Initialize a particle with specified properties.
        
        Args:
            x, y (float): Starting position
            vel_x, vel_y (float): Initial velocity components
            color (tuple): RGB color tuple
            size (int): Particle size in pixels
            lifetime (int): Duration in frames (60 = 1 second at 60fps)
        """
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1  # Subtle gravity effect
        
    def update(self):
        """
        Update particle position and physics.
        
        This method:
        1. Updates position based on velocity
        2. Applies gravity to vertical velocity
        3. Decreases lifetime counter
        4. Handles particle physics simulation
        """
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Apply gravity
        self.vel_y += self.gravity
        self.lifetime -= 1
        
        # Fade out over time
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        if len(self.color) == 3:
            self.color = (*self.color, alpha)
        else:
            self.color = (*self.color[:3], alpha)
            
    def draw(self, screen):
        """Draw the particle"""
        if self.lifetime > 0:
            current_size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            # Create a surface with per-pixel alpha
            surf = pg.Surface((current_size * 2, current_size * 2), pg.SRCALPHA)
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color_with_alpha = (*self.color[:3], alpha)
            pg.draw.circle(surf, color_with_alpha, (current_size, current_size), current_size)
            screen.blit(surf, (self.x - current_size, self.y - current_size))
            
    def is_alive(self):
        """Check if particle is still alive"""
        return self.lifetime > 0


class ParticleSystem:
    """Manages multiple particles"""
    def __init__(self):
        self.particles = []
        
    def add_particle(self, particle):
        """Add a particle to the system"""
        self.particles.append(particle)
        
    def update(self):
        """Update all particles and remove dead ones"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
            
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)
            
    def create_explosion(self, x, y, color=(255, 100, 0), count=10):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            size = random.randint(2, 5)
            lifetime = random.randint(30, 60)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime)
            self.add_particle(particle)
            
    def create_collectible_effect(self, x, y, color=(255, 255, 0)):
        """Create effect when collecting items"""
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed - 2  # Slight upward bias
            size = random.randint(1, 3)
            lifetime = random.randint(20, 40)
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime)
            self.add_particle(particle)
            
    def create_landing_dust(self, x, y, direction=0):
        """Create enhanced dust effect when player lands"""
        # More particles for better visibility
        for _ in range(8):
            vel_x = random.uniform(-3, 3) + direction
            vel_y = random.uniform(-2, 0.5)
            size = random.randint(2, 4)  # Larger particles
            lifetime = random.randint(25, 40)  # Longer lasting
            # More visible colors - light brown/tan dust
            color = random.choice([
                (222, 184, 135),  # Burlywood
                (210, 180, 140),  # Tan
                (245, 245, 220),  # Beige
                (255, 228, 196),  # Bisque
            ])
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime)
            self.add_particle(particle)
        
        # Add some sparkle particles for extra visibility
        for _ in range(3):
            vel_x = random.uniform(-1, 1)
            vel_y = random.uniform(-3, -1)
            size = random.randint(1, 2)
            lifetime = random.randint(20, 30)
            color = (255, 255, 255)  # White sparkles
            
            particle = Particle(x, y, vel_x, vel_y, color, size, lifetime)
            self.add_particle(particle)


class ScreenShake:
    """Screen shake effect for impact"""
    def __init__(self):
        self.shake_intensity = 0
        self.shake_duration = 0
        self.offset_x = 0
        self.offset_y = 0
        
    def start_shake(self, intensity, duration):
        """Start screen shake effect"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        
    def update(self):
        """Update shake effect"""
        if self.shake_duration > 0:
            self.shake_duration -= 1
            # Generate random offset based on intensity
            self.offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            
            # Reduce intensity over time
            self.shake_intensity = max(0, self.shake_intensity - 1)
        else:
            self.offset_x = 0
            self.offset_y = 0
            
    def get_offset(self):
        """Get current shake offset"""
        return (self.offset_x, self.offset_y)


class FloatingText:
    """Floating text for score/damage indicators"""
    def __init__(self, x, y, text, color=(255, 255, 255), size=20):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.lifetime = 120  # 2 seconds
        self.max_lifetime = 120
        self.vel_y = -1  # Float upward
        
    def update(self):
        """Update floating text"""
        self.y += self.vel_y
        self.lifetime -= 1
        
    def draw(self, screen, font):
        """Draw floating text"""
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            # Create text surface
            text_surface = font.render(self.text, True, self.color)
            # Apply alpha
            text_surface.set_alpha(alpha)
            screen.blit(text_surface, (self.x, self.y))
            
    def is_alive(self):
        """Check if text is still alive"""
        return self.lifetime > 0


class FloatingTextManager:
    """Manages floating text effects"""
    def __init__(self):
        self.texts = []
        
    def add_text(self, x, y, text, color=(255, 255, 255), size=20):
        """Add floating text"""
        floating_text = FloatingText(x, y, text, color, size)
        self.texts.append(floating_text)
        
    def update(self):
        """Update all floating texts"""
        self.texts = [t for t in self.texts if t.is_alive()]
        for text in self.texts:
            text.update()
            
    def draw(self, screen, font):
        """Draw all floating texts"""
        for text in self.texts:
            text.draw(screen, font)


class PowerUpIndicator:
    """Visual indicator for active power-ups"""
    def __init__(self, x, y, effect_name, duration, color):
        self.x = x
        self.y = y
        self.effect_name = effect_name
        self.duration = duration
        self.max_duration = duration
        self.color = color
        self.pulse_timer = 0
        
    def update(self):
        """Update indicator"""
        self.duration -= 1
        self.pulse_timer += 1
        
    def draw(self, screen, font):
        """Draw power-up indicator"""
        if self.duration > 0:
            # Create pulsing effect
            pulse = 1 + 0.2 * math.sin(self.pulse_timer * 0.2)
            
            # Draw background
            bg_color = (*self.color, 100)
            bg_surface = pg.Surface((80, 20), pg.SRCALPHA)
            pg.draw.rect(bg_surface, bg_color, (0, 0, 80, 20), border_radius=5)
            screen.blit(bg_surface, (self.x, self.y))
            
            # Draw progress bar
            progress = self.duration / self.max_duration
            bar_width = int(76 * progress)
            pg.draw.rect(screen, self.color, (self.x + 2, self.y + 2, bar_width, 16))
            
            # Draw text
            text_surface = font.render(self.effect_name, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.x + 40, self.y + 10))
            screen.blit(text_surface, text_rect)
            
    def is_alive(self):
        """Check if indicator is still alive"""
        return self.duration > 0


class EffectsManager:
    """Centralized effects management"""
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.floating_text = FloatingTextManager()
        self.power_up_indicators = []
        
    def update(self):
        """Update all effects"""
        self.particle_system.update()
        self.screen_shake.update()
        self.floating_text.update()
        self.power_up_indicators = [i for i in self.power_up_indicators if i.is_alive()]
        for indicator in self.power_up_indicators:
            indicator.update()
            
    def draw(self, screen, font):
        """Draw all effects"""
        self.particle_system.draw(screen)
        self.floating_text.draw(screen, font)
        for indicator in self.power_up_indicators:
            indicator.draw(screen, font)
            
    def create_explosion(self, x, y, color=(255, 100, 0)):
        """Create explosion effect"""
        self.particle_system.create_explosion(x, y, color)
        self.screen_shake.start_shake(5, 10)
        
    def create_collectible_effect(self, x, y, color=(255, 255, 0)):
        """Create collectible effect"""
        self.particle_system.create_collectible_effect(x, y, color)
        
    def create_landing_dust(self, x, y, direction=0):
        """Create landing dust effect"""
        self.particle_system.create_landing_dust(x, y, direction)
        
    def add_floating_text(self, x, y, text, color=(255, 255, 255)):
        """Add floating text"""
        self.floating_text.add_text(x, y, text, color)
        
    def add_power_up_indicator(self, x, y, effect_name, duration, color):
        """Add power-up indicator"""
        indicator = PowerUpIndicator(x, y, effect_name, duration, color)
        self.power_up_indicators.append(indicator)
        
    def get_shake_offset(self):
        """Get screen shake offset"""
        return self.screen_shake.get_offset()
