#!/usr/bin/env python3
"""
Skybound shared constants.

Single source of truth for values that were previously duplicated as magic
numbers across the game loop and sprite classes (screen size, frame rate,
physics tuning, gameplay timers, colours). Importing from here keeps Player,
Mob and the loop in agreement and makes tuning a one-line change.
"""

# --- Display ---------------------------------------------------------------
WIDTH: int = 480               # Screen width in pixels
HEIGHT: int = 600              # Screen height in pixels
FPS: int = 100                 # Target frames per second
TITLE: str = "Skybound"        # Window title

# --- Physics (shared by Player and Mob) ------------------------------------
PLAYER_ACC: float = 0.5        # Gravity / acceleration magnitude
FRICTION: float = -0.12        # Horizontal friction coefficient
MOB_ACC: float = 0.5           # Mob gravity / acceleration magnitude
MOB_FRICTION: float = -0.12    # Mob horizontal friction coefficient

# --- Jumping ---------------------------------------------------------------
JUMP_VELOCITY: int = -14       # Upward velocity of a normal jump
JUMP_BOOST_VELOCITY: int = -18 # Upward velocity while jump-boost is active
# Game-feel grace windows (frames @ 100 FPS).
COYOTE_FRAMES: int = 6         # Grace to still jump just after leaving a ledge
JUMP_BUFFER_FRAMES: int = 8    # Grace to register a jump pressed just before landing

# Reachability budget for procedural level generation. A base jump
# (v=JUMP_VELOCITY, g=PLAYER_ACC) peaks at ~132px; these stay safely under that
# so every generated platform is reachable from the one below it.
MAX_REACH_V: int = 110         # Max jumpable vertical gap between platform tops
MAX_REACH_H: int = 140         # Max horizontal gap reachable within a jump's airtime

# --- Player gameplay -------------------------------------------------------
START_HEALTH: int = 3          # Health the player spawns with
MAX_HEALTH: int = 5            # Hard cap on health
INVINCIBILITY_FRAMES: int = 120  # I-frames after taking damage (~2s @ 60fps)
POWERUP_DURATION: int = 300    # Default power-up duration in frames

# --- Colours ---------------------------------------------------------------
WHITE: tuple = (255, 255, 255)
BLACK: tuple = (0, 0, 0)
RED: tuple = (255, 0, 0)
GREEN: tuple = (0, 255, 0)
GOLD: tuple = (255, 215, 0)
