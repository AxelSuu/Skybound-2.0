#!/usr/bin/env python3
"""
Skybound persistence facade.

Historically this module read and wrote one value per text file in ``txts/``.
It is now a thin facade over ``utils.save_manager.SaveManager`` (a single JSON
save loaded into memory), keeping the original Get*/Set* function names so the
rest of the game keeps working unchanged.

The first time a value is read or written, the SaveManager migrates any legacy
``txts/*.txt`` files into ``save.json`` automatically.

All functions follow the original naming pattern:
- Get[DataType](): retrieve a value
- Set[DataType](value): store a value

Author: Axel Suu
"""

from utils.save_manager import get_save_manager


def GetScore():
    """Current player level/score (default 1)."""
    return int(get_save_manager().get("score"))


def SetScore(score):
    get_save_manager().set("score", int(score))


def GetLevel():
    """Which level layout to load (default 1)."""
    return int(get_save_manager().get("level"))


def SetLevel(level):
    get_save_manager().set("level", int(level))


def GetGamestate():
    """Current screen/state (runtime only, not persisted)."""
    return get_save_manager().gamestate


def SetGamestate(newGamestate):
    get_save_manager().gamestate = str(newGamestate)


def GetHighScore():
    """Best level reached (default 0)."""
    return int(get_save_manager().get("highscore"))


def SetHighScore(newHighScore):
    """Update the high score only if it beats the stored one."""
    if int(newHighScore) > GetHighScore():
        get_save_manager().set("highscore", int(newHighScore))


def manualSetHighScore(newHighScore):
    """Force-set the high score regardless of the current value."""
    get_save_manager().set("highscore", int(newHighScore))


def Hat():
    """Selected hat ("0" = none, "hat" = hat)."""
    return str(get_save_manager().get("hat"))


def SetHat(newHat):
    get_save_manager().set("hat", str(newHat))


def SetChar(char):
    get_save_manager().set("char", int(char))


def SelectedChar():
    return int(get_save_manager().get("char"))


def WearsHat():
    """True only when the hat is both unlocked and currently equipped.

    Ownership lives in ``hat`` (set by the shop on purchase); the equipped
    selection lives in ``char`` (set in character selection). The player wears
    the hat only when both agree — owning the hat but selecting "Normal" shows
    no hat. This is the single source of truth so the shop, the character
    screen and the player can never drift out of sync.
    """
    return Hat() == "hat" and SelectedChar() == 1


def GetCoins():
    """Total coins collected across sessions (default 0)."""
    return int(get_save_manager().get("coins"))


def SetCoins(coins):
    get_save_manager().set("coins", int(coins))


def AddCoins(amount):
    """Add coins to the running total and return the new total."""
    return int(get_save_manager().add("coins", int(amount)))


def ResetProgress():
    """Wipe all gameplay progress back to a fresh save.

    Resets coins, score, level, highscore, cosmetics and upgrades to their
    defaults while deliberately leaving audio ``settings`` and ``daily_bests``
    untouched. Used by the main-menu Restart button.
    """
    get_save_manager().reset(
        "score", "highscore", "level", "coins", "hat", "char", "upgrades"
    )
