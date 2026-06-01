#!/usr/bin/env python3
"""
Skybound permanent upgrade shop economy.

Coins collected during play (persisted in the save) can be spent on permanent
upgrades that carry across runs. This module owns the catalogue and the
buy/cost logic; the shop UI (windows/shop.py) and the player application layer
build on it. Upgrade levels live in the save under "upgrades".
"""

from utils.database_logic import GetCoins, SetCoins
from utils.save_manager import get_save_manager
from constants import MAX_HEALTH

# Upgrade catalogue. cost(level) = base_cost + cost_step * level (level = how
# many already owned), so each tier costs more than the last.
UPGRADES = {
    "max_health": {
        "name": "Max Health",
        "desc": "+1 maximum heart",
        "base_cost": 30,
        "cost_step": 25,
        "max_level": 4,
    },
    "move_speed": {
        "name": "Fleet Footed",
        "desc": "Accelerate a little faster",
        "base_cost": 25,
        "cost_step": 20,
        "max_level": 3,
    },
    "double_jump": {
        "name": "Double Jump",
        "desc": "Start every run with a double jump",
        "base_cost": 80,
        "cost_step": 0,
        "max_level": 1,
    },
}

# Apply-tuning constants.
SPEED_STEP = 0.12  # run-acceleration multiplier added per move_speed level


def get_level(upgrade_id):
    """Current owned level of an upgrade (0 if none)."""
    return int(get_save_manager().get("upgrades").get(upgrade_id, 0))


def is_maxed(upgrade_id):
    return get_level(upgrade_id) >= UPGRADES[upgrade_id]["max_level"]


def cost_for_next(upgrade_id):
    """Coin cost of the next level, or None if already maxed."""
    if is_maxed(upgrade_id):
        return None
    spec = UPGRADES[upgrade_id]
    return spec["base_cost"] + spec["cost_step"] * get_level(upgrade_id)


def can_afford(upgrade_id):
    cost = cost_for_next(upgrade_id)
    return cost is not None and GetCoins() >= cost


def purchase(upgrade_id):
    """Buy the next level of an upgrade. Returns True on success.

    Fails (returns False) if the upgrade is maxed or the player can't afford it.
    """
    cost = cost_for_next(upgrade_id)
    if cost is None or GetCoins() < cost:
        return False
    SetCoins(GetCoins() - cost)
    sm = get_save_manager()
    upgrades = sm.get("upgrades")
    upgrades[upgrade_id] = get_level(upgrade_id) + 1
    sm.set("upgrades", upgrades)
    return True


def apply_upgrades(player):
    """Apply owned upgrades to a freshly-constructed player.

    Runs once per Player construction, layered deterministically on top of the
    base stats so it never compounds across saves:
      - max_health is set from the base constant + level (overriding any stored
        value), with current health clamped into the new cap.
      - run acceleration is boosted (without touching gravity).
      - double jump is granted permanently when owned.
    """
    player.max_health = MAX_HEALTH + get_level("max_health")
    player.health = min(player.health, player.max_health)
    player.run_accel_mult = 1.0 + SPEED_STEP * get_level("move_speed")
    if get_level("double_jump") > 0:
        player.has_double_jump = True
