#!/usr/bin/env python3
"""
Skybound - A 2D Platformer Game

This is the main entry point for the Skybound game. It manages the game state system,
handles window transitions, and controls background music for different game states.

The game uses a state-based architecture with the following states:
- MAIN_MENU: Main menu screen with options to start, view achievements, settings, etc.
- START_SCREEN: Character selection screen
- GAME: Active gameplay loop
- PAUSED: Game paused state
- GAME_OVER: Game over screen after completing a level or dying
- NEW_HIGHSCORE: Special screen shown when a new high score is achieved
- EXIT: Terminates the game

State management is handled through a simple text file database system located
in the utils/database_logic.py module. Player progress, settings, and statistics
are persisted between game sessions.

Author: Axel Suu
Date: July 2025
"""

import pygame as pg
import numpy as np
import os

# Import database utilities for state management
from utils.database_logic import *

# Import all game window classes
from windows.main_menu import *
from windows.start import *
from windows.gameover import *
from windows.paus import *
from gameloop.loop import *
from windows.new_highscore_screen import *


class Main_Loop:
    """
    Main loop class to manage game states and transitions.
    
    This class is responsible for:
    - Initializing pygame and audio systems
    - Managing game state transitions
    - Handling background music for different game states
    - Creating and managing window instances for each game state
    
    The class uses a simple state machine pattern where each game state
    corresponds to a different window class that handles the specific
    functionality for that state.
    
    Attributes:
        sfx_folder_path (str): Path to the sound effects folder
        pause_music (bool): Flag to control music pausing
        gamesound (str): Path to the gameplay background music
        menusound (str): Path to the menu background music
        highscoresound (str): Path to the high score screen music
        channel1-4 (pygame.mixer.Channel): Audio channels for different music tracks
        current_window (object): Currently active window/screen instance
        running1 (bool): Main loop control flag
    """

    def __init__(self):
        """
        Initialize the game and set the initial game state.
        
        This method:
        1. Initializes pygame and the audio mixer
        2. Sets up audio channels and loads background music
        3. Sets the initial game state to MAIN_MENU
        4. Starts the main game loop
        
        The audio system uses 4 separate channels:
        - Channel 0: Menu music (main menu, start screen, game over)
        - Channel 1: Unused (reserved for future use)
        - Channel 2: Gameplay music (during active gameplay)
        - Channel 3: High score celebration music
        """
        # Initialize pygame systems
        pg.init()
        pg.mixer.init()
        
        # Set up audio file paths
        self.sfx_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "sfxs")
        )
        
        # Audio control flags
        self.pause_music = False
        
        # Load background music files
        self.gamesound = os.path.join(self.sfx_folder_path, "music5.ogg")
        self.menusound = os.path.join(self.sfx_folder_path, "music7.ogg")
        self.highscoresound = os.path.join(self.sfx_folder_path, "music1.ogg")
        
        # Set up audio channels for different music tracks
        self.channel1 = pg.mixer.Channel(0)  # Menu music
        self.channel2 = pg.mixer.Channel(1)  # Reserved
        self.channel3 = pg.mixer.Channel(2)  # Gameplay music
        self.channel4 = pg.mixer.Channel(3)  # High score music
        
        # Set global volume level
        pg.mixer.music.set_volume(0.4)
        
        # Initialize game state to main menu
        SetGamestate("MAIN_MENU")
        
        # Initialize window management
        self.current_window = None
        self.running1 = True
        
        # Pre-load and pause all music tracks (they'll be unpaused as needed)
        self.channel1.play(pg.mixer.Sound(self.menusound), loops=-1)
        self.channel1.pause()
        self.channel3.play(pg.mixer.Sound(self.gamesound), loops=-1)
        self.channel3.pause()
        self.channel4.play(pg.mixer.Sound(self.highscoresound), loops=-1)
        self.channel4.pause()
        
        # Start the main game loop
        self.main()

    def main(self):
        """
        Main loop to check and transition between game states.
        
        This method implements the core game state machine. It continuously
        checks the current game state and ensures the appropriate window
        class is instantiated and active. Each state corresponds to a
        different screen/window in the game.
        
        State transitions are handled through the database_logic system,
        which other parts of the game can modify to trigger state changes.
        
        Music management is also handled here - each state has its own
        background music track that is automatically managed.
        """
        while self.running1 == True:
            # Get current game state from the database system
            current_state = GetGamestate()

            # MAIN_MENU STATE: Show main menu with game options
            if current_state == "MAIN_MENU":
                if not isinstance(self.current_window, Main_menu):
                    # Unpause menu music if not already paused globally
                    if not self.pause_music:
                        self.channel1.unpause()
                    self.current_window = Main_menu()
                    self.channel1.pause()

            # START_SCREEN STATE: Character selection screen
            elif current_state == "START_SCREEN":
                if not isinstance(self.current_window, Start):
                    if not self.pause_music:
                        self.channel1.unpause()
                    self.current_window = Start()
                    self.channel1.pause()

            # GAME STATE: Active gameplay loop
            elif current_state == "GAME":
                if not isinstance(self.current_window, Loop):
                    # Switch to gameplay music
                    if not self.pause_music:
                        self.channel3.unpause()
                    self.current_window = Loop(self)
                    self.channel3.pause()

            # PAUSED STATE: Game is paused (accessible during gameplay)
            elif current_state == "PAUSED":
                if not isinstance(self.current_window, Pause):
                    # Keep menu music during pause
                    if not self.pause_music:
                        self.channel1.unpause()
                    self.current_window = Pause(self)
                    self.channel1.pause()

            # GAME_OVER STATE: Level completed or player died
            elif current_state == "GAME_OVER":
                if not isinstance(self.current_window, Gameover):
                    # Return to menu music
                    if not self.pause_music:
                        self.channel1.unpause()
                    self.current_window = Gameover()
                    self.channel1.pause()

            # NEW_HIGHSCORE STATE: Special celebration screen for new records
            elif current_state == "NEW_HIGHSCORE":
                if not isinstance(self.current_window, NewHighscore):
                    # Play special celebration music
                    if not self.pause_music:
                        self.channel4.unpause()
                    self.current_window = NewHighscore()
                    self.channel4.pause()

            # EXIT STATE: Terminate the game
            elif current_state == "EXIT":
                self.running1 = False
                pg.mixer.music.stop()
                pg.quit()

    def pause_music_func(self):
        """
        Pause all background music channels.
        
        This method was intended for global music pausing functionality
        but is currently not fully implemented in the game. It's preserved
        for future use or debugging purposes.
        
        When called, it:
        1. Sets the pause_music flag to True
        2. Pauses all four audio channels
        """
        self.pausemusic = True
        self.channel1.pause()
        self.channel2.pause()
        self.channel3.pause()
        self.channel4.pause()


if __name__ == "__main__":
    """
    Main entry point for the Skybound game.
    
    This creates an instance of the Main_Loop class which handles
    the entire game lifecycle from initialization to termination.
    """
    Main_Loop()
