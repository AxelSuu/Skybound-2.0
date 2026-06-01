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
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color[:3]  # store RGB only; alpha computed at draw time
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = 0.1
        # Pre-allocated surface reused every frame to avoid per-frame allocation.
        _d = size * 2 + 2
        self._surf = pg.Surface((_d, _d), pg.SRCALPHA)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += self.gravity
        self.lifetime -= 1

    def draw(self, screen):
        if self.lifetime > 0:
            ratio = self.lifetime / self.max_lifetime
            current_size = max(1, int(self.size * ratio))
            alpha = int(255 * ratio)
            self._surf.fill((0, 0, 0, 0))
            pg.draw.circle(self._surf, (*self.color, alpha),
                           (self.size + 1, self.size + 1), current_size)
            screen.blit(self._surf, (int(self.x) - self.size - 1, int(self.y) - self.size - 1))

    def is_alive(self):
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


class EffectsManager:
    """Centralized effects management"""
    def __init__(self):
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.floating_text = FloatingTextManager()
        self.hit_stop = 0  # Frames of gameplay freeze remaining (juice)

    def start_hit_stop(self, frames):
        """Freeze the gameplay simulation for a few frames for impact.

        Effects (shake, particles) keep animating during the freeze; the game
        loop is responsible for skipping its simulation while is_hit_stopped().
        """
        self.hit_stop = max(self.hit_stop, frames)

    def is_hit_stopped(self):
        """True while a hit-stop freeze is in effect."""
        return self.hit_stop > 0

    def update(self):
        if self.hit_stop > 0:
            self.hit_stop -= 1
        self.particle_system.update()
        self.screen_shake.update()
        self.floating_text.update()

    def draw(self, screen, font):
        self.particle_system.draw(screen)
        self.floating_text.draw(screen, font)

    def create_explosion(self, x, y, color=(255, 100, 0)):
        self.particle_system.create_explosion(x, y, color)
        self.screen_shake.start_shake(5, 10)

    def create_collectible_effect(self, x, y, color=(255, 255, 0)):
        self.particle_system.create_collectible_effect(x, y, color)

    def create_landing_dust(self, x, y, direction=0):
        self.particle_system.create_landing_dust(x, y, direction)

    def add_floating_text(self, x, y, text, color=(255, 255, 255)):
        self.floating_text.add_text(x, y, text, color)

    def get_shake_offset(self):
        return self.screen_shake.get_offset()
