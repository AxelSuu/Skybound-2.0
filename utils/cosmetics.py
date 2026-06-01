#!/usr/bin/env python3
"""
Skybound cosmetics catalogue and persistence helpers.

Skins (character recolors) and hats are coin-gated collectibles.  Ownership
and the current selection live in the save under ``owned_skins``,
``owned_hats``, ``skin``, and ``equipped_hat``.  This module is the single
source of truth so the shop, character screen, and player never drift.

Mirrors the pattern in utils/upgrades.py — catalogue dict + thin helpers
over get_save_manager() + GetCoins/SetCoins.

Author: Axel Suu
"""

from utils.database_logic import GetCoins, SetCoins
from utils.save_manager import get_save_manager

# ---------------------------------------------------------------------------
# Catalogues
# ---------------------------------------------------------------------------

# index → display name + spritesheet filename + unlock cost.
# Skin 0 (Classic) is always owned and free.  All recolors share the frame
# layout defined in Playersheet.json — loaded via Spritesheet(sheet,
# meta_filename="Playersheet.json").
SKINS = {
    0: {"name": "Classic", "sheet": "Playersheet.png",  "cost": 0},
    1: {"name": "Green",   "sheet": "player_green.png", "cost": 40},
    2: {"name": "Red",     "sheet": "player_red.png",   "cost": 40},
    3: {"name": "Teal",    "sheet": "player_teal.png",  "cost": 40},
    4: {"name": "Gold",    "sheet": "player_gold.png",  "cost": 80},
}

# id → display name + hat image filename + unlock cost.
# "none" is always owned (bareheaded).  All hats share the blit anchor used
# by the original hat1.png: (0, -8) for left-facing frames, (10, -8) for right.
HATS = {
    "none":   {"name": "None",   "file": None,             "cost": 0},
    "cap":    {"name": "Cap",    "file": "hat_cap.png",    "cost": 30},
    "crown":  {"name": "Crown",  "file": "hat_crown.png",  "cost": 60},
    "wizard": {"name": "Wizard", "file": "hat_wizard.png", "cost": 50},
    "halo":   {"name": "Halo",   "file": "hat_halo.png",   "cost": 70},
    "horns":  {"name": "Horns",  "file": "hat_horns.png",  "cost": 50},
}

# ---------------------------------------------------------------------------
# Skin helpers
# ---------------------------------------------------------------------------

def owned_skins():
    """Return a list of owned skin indices (always contains 0)."""
    raw = get_save_manager().get("owned_skins")
    result = list(raw) if raw else [0]
    if 0 not in result:
        result.insert(0, 0)
    return result


def owns_skin(index):
    """True if the player owns the skin at *index*."""
    return index in owned_skins()


def get_skin():
    """Return the currently-selected skin index (int, default 0)."""
    return int(get_save_manager().get("skin") or 0)


def set_skin(index):
    """Equip a skin the player already owns.  No-op for unowned skins."""
    if owns_skin(index):
        get_save_manager().set("skin", int(index))


def buy_skin(index):
    """Purchase and immediately equip a skin.  Returns True on success."""
    if index not in SKINS or owns_skin(index):
        return False
    cost = SKINS[index]["cost"]
    if GetCoins() < cost:
        return False
    SetCoins(GetCoins() - cost)
    sm = get_save_manager()
    skins = owned_skins()
    if index not in skins:
        skins.append(index)
    sm.set("owned_skins", skins)
    sm.set("skin", int(index))
    return True


# ---------------------------------------------------------------------------
# Hat helpers
# ---------------------------------------------------------------------------

def owned_hats():
    """Return a list of owned hat ids (always contains 'none')."""
    raw = get_save_manager().get("owned_hats")
    result = list(raw) if raw else ["none"]
    if "none" not in result:
        result.insert(0, "none")
    return result


def owns_hat(hat_id):
    """True if the player owns the hat with id *hat_id*."""
    return hat_id in owned_hats()


def get_hat():
    """Return the currently-equipped hat id (str, default 'none')."""
    return str(get_save_manager().get("equipped_hat") or "none")


def set_hat(hat_id):
    """Equip a hat the player already owns.  No-op for unowned hats."""
    if owns_hat(hat_id):
        get_save_manager().set("equipped_hat", str(hat_id))


def buy_hat(hat_id):
    """Purchase and immediately equip a hat.  Returns True on success."""
    if hat_id not in HATS or owns_hat(hat_id):
        return False
    cost = HATS[hat_id]["cost"]
    if GetCoins() < cost:
        return False
    SetCoins(GetCoins() - cost)
    sm = get_save_manager()
    hats = owned_hats()
    if hat_id not in hats:
        hats.append(hat_id)
    sm.set("owned_hats", hats)
    sm.set("equipped_hat", str(hat_id))
    return True
