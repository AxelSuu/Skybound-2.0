#!/usr/bin/env python3
"""
Skybound Database Logic System

This module provides a simple file-based database system for managing
game state and persistent data. All game data is stored in text files
within the 'txts' folder, providing a lightweight persistence solution.

The database system manages:
- Game state (current screen/mode)
- Player progress (current level, score, high score)
- Player customization (character selection, hats)
- Settings and preferences

This approach provides:
- Simple implementation without external dependencies
- Human-readable data files for debugging
- Cross-platform compatibility
- Easy backup and transfer of save data

All functions follow a consistent naming pattern:
- Get[DataType](): Retrieve data from file
- Set[DataType](value): Store data to file

Author: [Your Name]
Date: July 2025
"""

import os

# Constants for file paths
TXT_FOLDER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "txts"))


def GetScore():
    """
    Get the current player score (level progress).
    
    Returns:
        int: Current level number/score
        
    The score represents the player's current level progress, starting from 1.
    This value is used for level selection and difficulty scaling.
    """
    try:
        with open(os.path.join(TXT_FOLDER_PATH, "Score.txt"), "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # Return default score if file doesn't exist or is corrupted
        return 1


def SetScore(score):
    """
    Set the current player score (level progress).
    
    Args:
        score (int): New score/level to set
        
    This function updates the player's current level progress,
    which determines which level they will play next.
    """
    try:
        with open(os.path.join(TXT_FOLDER_PATH, "Score.txt"), "w") as f:
            f.write(str(score))
    except IOError as e:
        print(f"Error saving score: {e}")


##################################################################################


def GetLevel():
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "level.txt"), "r") as f:
        return int(f.read())


def SetLevel(level):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "level.txt"), "w") as f:
        f.write(str(level))


##################################################################################


def GetGamestate():
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Gamestate.txt"), "r") as f:
        return f.read()


def SetGamestate(newGamestate):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Gamestate.txt"), "w") as f:
        f.write(str(newGamestate))


##################################################################################


def GetHighScore():
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Highscore.txt"), "r") as f:
        return int(f.read())  # int(f.read())?


def SetHighScore(newHighScore):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    if newHighScore > int(GetHighScore()):
        with open(os.path.join(txt_folder_path, "Highscore.txt"), "w") as f:
            f.write(str(newHighScore))


def manualSetHighScore(newHighScore):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Highscore.txt"), "w") as f:
        f.write(str(newHighScore))


##################################################################################

# The code below is discontinued

##################################################################################


def Hat():
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Hat.txt"), "r") as f:
        return f.read()  # More logic could be added here to check if the hat is valid.


def SetHat(newHat):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Hat.txt"), "w") as f:
        f.write(str(newHat))


##################################################################################


def SetChar(char):
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Char_selection.txt"), "w") as f:
        f.write(str(char))


def SelectedChar():
    txt_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "txts")
    )
    with open(os.path.join(txt_folder_path, "Char_selection.txt"), "r") as f:
        return int(f.read())


##################################################################################


def GetCoins():
    """
    Get the current player coin count.
    
    Returns:
        int: Current number of coins collected
        
    The coin count represents the total coins collected across all gameplay sessions.
    This value persists between game sessions and is used for achievements and progression.
    """
    try:
        with open(os.path.join(TXT_FOLDER_PATH, "coins.txt"), "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        # Return default coins if file doesn't exist or is corrupted
        return 0


def SetCoins(coins):
    """
    Set the current player coin count.
    
    Args:
        coins (int): New coin count to set
        
    This function updates the player's total coin count,
    which persists across game sessions.
    """
    try:
        with open(os.path.join(TXT_FOLDER_PATH, "coins.txt"), "w") as f:
            f.write(str(coins))
    except IOError as e:
        print(f"Error saving coins: {e}")


def AddCoins(amount):
    """
    Add coins to the current coin count.
    
    Args:
        amount (int): Number of coins to add
        
    Returns:
        int: New total coin count
        
    This function safely adds coins to the current total and saves the result.
    """
    current_coins = GetCoins()
    new_total = current_coins + amount
    SetCoins(new_total)
    return new_total
