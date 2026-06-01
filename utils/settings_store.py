#!/usr/bin/env python3
"""
Persistent audio settings, backed by the JSON save.

Previously the settings screen applied volume/toggle changes live to the
sound manager but never wrote them anywhere (save_settings was never even
called), so preferences were lost on restart. This stores them in the save's
"settings" field and applies them to the sound manager on startup.
"""

from utils.save_manager import get_save_manager
from utils.sound_effects import sound_manager

_KEYS = ("sfx_volume", "music_volume", "sfx_enabled", "music_enabled")


def _defaults():
    """Default settings taken from the sound manager's own initial values."""
    return {
        "sfx_volume": sound_manager.sfx_volume,
        "music_volume": sound_manager.music_volume,
        "sfx_enabled": sound_manager.sfx_enabled,
        "music_enabled": sound_manager.music_enabled,
    }


def load_settings():
    """Return the saved settings merged over defaults (all keys present)."""
    settings = _defaults()
    stored = get_save_manager().get("settings") or {}
    for key in _KEYS:
        if key in stored:
            settings[key] = stored[key]
    return settings


def save_settings(settings):
    """Persist a settings dict (only the known keys) to the save."""
    get_save_manager().set("settings", {key: settings[key] for key in _KEYS})


def apply_to_sound_manager(settings):
    """Push settings into the live sound manager."""
    sound_manager.set_sfx_volume(settings["sfx_volume"])
    sound_manager.set_music_volume(settings["music_volume"])
    sound_manager.sfx_enabled = settings["sfx_enabled"]
    sound_manager.music_enabled = settings["music_enabled"]


def load_and_apply():
    """Load saved settings and apply them to the sound manager (call at startup)."""
    settings = load_settings()
    apply_to_sound_manager(settings)
    return settings
