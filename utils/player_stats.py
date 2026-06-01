"""
Per-run player state (health, power-up timers, double-jump).

This carries a player's state *between levels within a single play session*.
It is intentionally **in-memory only** — quitting and relaunching the game
starts a fresh run. Coins are no longer tracked here; they live in the single
wallet in ``save.json`` (see ``utils.database_logic.GetCoins``).
"""

import copy


class PlayerStats:
    """In-memory carry of per-run player state across levels."""

    def __init__(self):
        self.default_stats = {
            "health": 3,
            "max_health": 5,
            "has_double_jump": False,
            "speed_boost_timer": 0,
            "jump_boost_timer": 0,
            "shield_timer": 0,
            "double_jump_timer": 0,
            "shield_active": False,
        }
        self._stats = copy.deepcopy(self.default_stats)

    def save_stats(self, player):
        """Snapshot the player's current state for the next level."""
        self._stats = {
            "health": player.health,
            "max_health": player.max_health,
            "has_double_jump": player.has_double_jump,
            "speed_boost_timer": player.speed_boost_timer,
            "jump_boost_timer": player.jump_boost_timer,
            "shield_timer": player.shield_timer,
            "double_jump_timer": player.double_jump_timer,
            "shield_active": player.shield_active,
        }

    def apply_stats_to_player(self, player):
        """Apply the carried run state to a freshly created player."""
        stats = self._stats
        player.health = stats["health"]
        player.max_health = stats["max_health"]
        player.has_double_jump = stats["has_double_jump"]
        player.speed_boost_timer = stats["speed_boost_timer"]
        player.jump_boost_timer = stats["jump_boost_timer"]
        player.shield_timer = stats["shield_timer"]
        player.double_jump_timer = stats["double_jump_timer"]
        player.shield_active = stats["shield_active"]

    def reset_stats(self):
        """Reset the run state to defaults (e.g. on death or restart)."""
        self._stats = copy.deepcopy(self.default_stats)


# Global instance
player_stats = PlayerStats()
