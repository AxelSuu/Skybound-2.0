#!/usr/bin/env python3
"""
Skybound save system.

Replaces the previous scatter of one-value-per-file text saves with a single
JSON file loaded once into memory. Benefits:

- One atomic write (temp file + os.replace) — no half-written saves.
- Defensive defaults for every field — a missing or corrupt save falls back to
  sane values instead of crashing (the old GetLevel/GetGamestate/GetHighScore
  had no error handling and would raise on a missing file).
- State lives in memory, so reads are free — the main loop no longer hits the
  disk every frame to check the game state.

``database_logic.py`` delegates to the module-level ``get_save_manager()``
singleton, so existing call sites keep working unchanged.

Author: Axel Suu (revived 2026)
"""

import json
import os
import tempfile

# Persisted fields and their defaults. ``gamestate`` is deliberately *not*
# here — it is runtime-only (see SaveManager.gamestate); persisting "PAUSED"
# or "GAME" across restarts would be wrong, and the menu resets it anyway.
DEFAULTS = {
    "score": 1,       # current level the player is on
    "highscore": 0,   # best level reached
    "level": 1,       # which level layout to load (1 = handcrafted, >1 = procedural)
    "coins": 0,       # total coins collected across sessions
    "hat": "0",       # cosmetic hat selection ("0" = none, "hat" = hat)
    "char": 0,        # selected character index
}

# Old text files to import on first run, keyed by save field.
_LEGACY_TXT = {
    "score": ("Score.txt", int),
    "highscore": ("Highscore.txt", int),
    "level": ("level.txt", int),
    "coins": ("coins.txt", int),
    "hat": ("Hat.txt", str),
    "char": ("Char_selection.txt", int),
}


class SaveManager:
    """In-memory game save backed by a single JSON file."""

    def __init__(self, path, txt_folder=None):
        self.path = path
        self.txt_folder = txt_folder
        self.data = dict(DEFAULTS)
        self.gamestate = "MAIN_MENU"  # runtime only, never persisted
        self.load()

    def load(self):
        """Load the JSON save, or migrate from legacy txt files, or default."""
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    loaded = json.load(f)
            except (json.JSONDecodeError, OSError, ValueError):
                # Corrupt or unreadable save -> defaults, don't crash.
                self.data = dict(DEFAULTS)
                return
            if isinstance(loaded, dict):
                for key, default in DEFAULTS.items():
                    self.data[key] = loaded.get(key, default)
            else:
                self.data = dict(DEFAULTS)
        elif self.txt_folder and os.path.isdir(self.txt_folder):
            self._migrate_from_txt()
            self.save()

    def _migrate_from_txt(self):
        """One-time import of the legacy txts/*.txt save files."""
        for key, (fname, cast) in _LEGACY_TXT.items():
            fpath = os.path.join(self.txt_folder, fname)
            try:
                with open(fpath) as f:
                    self.data[key] = cast(f.read().strip())
            except (OSError, ValueError):
                pass  # keep the default for this field

    def save(self):
        """Atomically persist the current data to disk."""
        directory = os.path.dirname(self.path) or "."
        try:
            fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w") as f:
                json.dump(self.data, f, indent=2)
            os.replace(tmp_path, self.path)
        except OSError:
            # Never let a failed save crash the game.
            if "tmp_path" in dir() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()


# --- Module-level singleton ------------------------------------------------

SAVE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "save.json"))
TXT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "txts"))

_manager = None


def get_save_manager():
    """Return the process-wide SaveManager, creating it lazily on first use."""
    global _manager
    if _manager is None:
        _manager = SaveManager(SAVE_PATH, TXT_FOLDER)
    return _manager
