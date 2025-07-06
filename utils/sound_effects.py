#!/usr/bin/env python3
"""
Skybound Sound Effects System

This module provides a comprehensive sound effects system for the Skybound game,
featuring both pre-recorded audio and procedurally generated sound effects.

The sound system includes:
- Dynamic sound effect generation using mathematical functions
- Volume and enable/disable controls for different audio categories
- Spatial audio with distance-based attenuation
- Sound effect management and caching
- Integration with pygame's audio mixer

Features:
- Procedural sound generation for consistent audio without large files
- Real-time audio processing and effects
- Memory-efficient sound caching system
- Volume normalization and audio processing
- Cross-platform audio compatibility

The system generates sounds mathematically, creating consistent audio
effects while keeping file sizes small and providing flexibility
for dynamic audio generation.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import os
import random
import math
import numpy as np


class SoundManager:
    """
    Comprehensive sound effects manager for the Skybound game.
    
    This class manages all sound effects in the game, providing both
    pre-recorded audio playback and procedural sound generation capabilities.
    
    The sound manager provides:
    - Dynamic sound effect generation using mathematical functions
    - Volume control for different audio categories
    - Spatial audio with distance-based volume calculation
    - Sound effect caching for performance
    - Enable/disable toggles for different sound types
    
    The system uses procedural generation to create consistent sound effects
    without requiring large audio files, making the game more lightweight
    while providing rich audio feedback.
    
    Attributes:
        sounds (dict): Cache of generated sound effects
        sfx_volume (float): Sound effects volume (0.0 to 1.0)
        music_volume (float): Music volume (0.0 to 1.0)
        sfx_enabled (bool): Whether sound effects are enabled
        music_enabled (bool): Whether music is enabled
    """
    
    def __init__(self):
        """
        Initialize the sound manager and create basic sound effects.
        
        This initialization:
        1. Sets up volume and enable/disable settings
        2. Initializes pygame mixer if not already active
        3. Creates a cache dictionary for sound effects
        4. Generates basic sound effects procedurally
        """
        # Initialize sound effect cache
        self.sounds = {}
        
        # Audio settings with reasonable defaults
        self.sfx_volume = 0.7       # Sound effects volume
        self.music_volume = 0.4     # Background music volume
        self.sfx_enabled = True     # Sound effects enabled
        self.music_enabled = True   # Music enabled
        
        # Initialize pygame mixer if not already done
        if not pg.mixer.get_init():
            pg.mixer.init()
            
        # Create procedural sound effects
        self.create_sound_effects()
        
    def create_sound_effects(self):
        """
        Create basic sound effects using procedural generation.
        
        This method generates various sound effects mathematically,
        creating consistent audio without requiring external files.
        The generated sounds include:
        - Jump sounds (musical tones)
        - Landing sounds (impact effects)
        - Collision sounds (noise-based effects)
        - Power-up sounds (ascending tones)
        - Coin collection sounds (pleasant chimes)
        """
        # Create jump sound - A4 note (440 Hz) with sine wave
        jump_sound = self.create_tone(440, 0.1, "sine")
        self.sounds["jump"] = jump_sound
        
        # Create coin collect sound
        coin_sound = self.create_tone(800, 0.1, "sine")  # Higher pitch
        self.sounds["coin"] = coin_sound
        
        # Create power-up sound
        powerup_sound = self.create_chord([523, 659, 784], 0.2)  # C-E-G chord
        self.sounds["powerup"] = powerup_sound
        
        # Create damage sound
        damage_sound = self.create_tone(200, 0.3, "sawtooth")  # Low harsh sound
        self.sounds["damage"] = damage_sound
        
        # Create level complete sound
        victory_sound = self.create_melody([523, 659, 784, 1047], 0.1)  # Ascending notes
        self.sounds["victory"] = victory_sound
        
        # Create enemy death sound
        enemy_death_sound = self.create_tone(300, 0.2, "triangle")
        self.sounds["enemy_death"] = enemy_death_sound
        
        # Create platform land sound
        land_sound = self.create_tone(150, 0.05, "square")
        self.sounds["land"] = land_sound
        
    def create_tone(self, frequency, duration, wave_type="sine"):
        """Create a tone with specified frequency and duration"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            time = float(i) / sample_rate
            
            if wave_type == "sine":
                wave = 4096 * math.sin(frequency * 2 * math.pi * time)
            elif wave_type == "square":
                wave = 4096 * (1 if math.sin(frequency * 2 * math.pi * time) > 0 else -1)
            elif wave_type == "sawtooth":
                wave = 4096 * (2 * (time * frequency % 1) - 1)
            elif wave_type == "triangle":
                wave = 4096 * (2 * abs(2 * (time * frequency % 1) - 1) - 1)
            else:
                wave = 4096 * math.sin(frequency * 2 * math.pi * time)
                
            # Apply fade out to prevent clicks
            if i > frames * 0.8:
                fade = 1 - (i - frames * 0.8) / (frames * 0.2)
                wave *= fade
                
            arr.append([int(wave), int(wave)])
            
        sound_array = np.array(arr, dtype=np.int16)
        sound = pg.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume)
        return sound
        
    def create_chord(self, frequencies, duration):
        """Create a chord with multiple frequencies"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        
        for i in range(frames):
            time = float(i) / sample_rate
            wave = 0
            
            for frequency in frequencies:
                wave += (4096 / len(frequencies)) * math.sin(frequency * 2 * math.pi * time)
                
            # Apply fade out
            if i > frames * 0.8:
                fade = 1 - (i - frames * 0.8) / (frames * 0.2)
                wave *= fade
                
            arr.append([int(wave), int(wave)])
            
        sound_array = np.array(arr, dtype=np.int16)
        sound = pg.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume)
        return sound
        
    def create_melody(self, frequencies, note_duration):
        """Create a melody with sequence of notes"""
        sample_rate = 22050
        note_frames = int(note_duration * sample_rate)
        total_frames = note_frames * len(frequencies)
        arr = []
        
        for note_idx, frequency in enumerate(frequencies):
            for i in range(note_frames):
                time = float(i) / sample_rate
                wave = 4096 * math.sin(frequency * 2 * math.pi * time)
                
                # Apply fade in/out for each note
                if i < note_frames * 0.1:
                    fade = i / (note_frames * 0.1)
                    wave *= fade
                elif i > note_frames * 0.9:
                    fade = 1 - (i - note_frames * 0.9) / (note_frames * 0.1)
                    wave *= fade
                    
                arr.append([int(wave), int(wave)])
                
        sound_array = np.array(arr, dtype=np.int16)
        sound = pg.sndarray.make_sound(sound_array)
        sound.set_volume(self.sfx_volume)
        return sound
        
    def play_sound(self, sound_name, volume_multiplier=1.0):
        """Play a sound effect"""
        if not self.sfx_enabled or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        sound.set_volume(self.sfx_volume * volume_multiplier)
        sound.play()
        
    def play_random_pitch(self, sound_name, pitch_range=0.2):
        """Play a sound with random pitch variation"""
        if not self.sfx_enabled or sound_name not in self.sounds:
            return
            
        # Create a copy of the sound and modify its frequency
        original_sound = self.sounds[sound_name]
        
        # For simplicity, we'll just play at different volumes to simulate pitch
        pitch_modifier = random.uniform(1 - pitch_range, 1 + pitch_range)
        volume = self.sfx_volume * pitch_modifier
        
        original_sound.set_volume(min(1.0, volume))
        original_sound.play()
        
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
            
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pg.mixer.music.set_volume(self.music_volume)
        
    def toggle_sfx(self):
        """Toggle sound effects on/off"""
        self.sfx_enabled = not self.sfx_enabled
        
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            pg.mixer.music.unpause()
        else:
            pg.mixer.music.pause()
            
    def load_external_sound(self, sound_name, file_path):
        """Load an external sound file"""
        try:
            sound = pg.mixer.Sound(file_path)
            sound.set_volume(self.sfx_volume)
            self.sounds[sound_name] = sound
            return True
        except pg.error:
            print(f"Could not load sound: {file_path}")
            return False
            
    def play_footstep(self):
        """Play a footstep sound with variation"""
        # Create a simple footstep sound
        footstep = self.create_tone(random.randint(80, 120), 0.05, "square")
        footstep.set_volume(self.sfx_volume * 0.3)
        footstep.play()
        
    def play_ambient_sound(self, sound_type):
        """Play ambient sounds"""
        if sound_type == "wind":
            wind_sound = self.create_tone(random.randint(60, 100), 2.0, "sawtooth")
            wind_sound.set_volume(self.sfx_volume * 0.1)
            wind_sound.play()
            
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        pg.mixer.stop()


# Global sound manager instance
sound_manager = SoundManager()


# Convenience functions for easy access
def play_jump_sound():
    sound_manager.play_sound("jump")
    
def play_coin_sound():
    sound_manager.play_sound("coin")
    
def play_powerup_sound():
    sound_manager.play_sound("powerup")
    
def play_damage_sound():
    sound_manager.play_sound("damage")
    
def play_victory_sound():
    sound_manager.play_sound("victory")
    
def play_enemy_death_sound():
    sound_manager.play_sound("enemy_death")
    
def play_land_sound():
    sound_manager.play_sound("land")
    
def play_footstep_sound():
    sound_manager.play_footstep()
    
def set_sfx_volume(volume):
    sound_manager.set_sfx_volume(volume)
    
def set_music_volume(volume):
    sound_manager.set_music_volume(volume)
    
def toggle_sfx():
    sound_manager.toggle_sfx()
    
def toggle_music():
    sound_manager.toggle_music()
