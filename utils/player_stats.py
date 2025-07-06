"""
Player statistics persistence system.
Handles saving and loading player stats (health, coins, power-ups) between levels.
"""

import os
import json

class PlayerStats:
    """Handles persistent player statistics across game sessions."""
    
    def __init__(self):
        self.stats_file = os.path.join(os.path.dirname(__file__), "..", "txts", "player_stats.txt")
        self.default_stats = {
            "health": 3,
            "max_health": 5,
            "coins": 0,
            "has_double_jump": False,
            "speed_boost_timer": 0,
            "jump_boost_timer": 0,
            "shield_timer": 0,
            "double_jump_timer": 0,
            "shield_active": False
        }
    
    def save_stats(self, player):
        """Save player stats to file."""
        stats = {
            "health": player.health,
            "max_health": player.max_health,
            "coins": player.coins,
            "has_double_jump": player.has_double_jump,
            "speed_boost_timer": player.speed_boost_timer,
            "jump_boost_timer": player.jump_boost_timer,
            "shield_timer": player.shield_timer,
            "double_jump_timer": player.double_jump_timer,
            "shield_active": player.shield_active
        }
        
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f)
        except Exception as e:
            print(f"Error saving player stats: {e}")
    
    def load_stats(self):
        """Load player stats from file."""
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    # Ensure all required keys exist
                    for key, default_value in self.default_stats.items():
                        if key not in stats:
                            stats[key] = default_value
                    return stats
            else:
                return self.default_stats.copy()
        except Exception as e:
            print(f"Error loading player stats: {e}")
            return self.default_stats.copy()
    
    def apply_stats_to_player(self, player):
        """Apply loaded stats to a player object."""
        stats = self.load_stats()
        player.health = stats["health"]
        player.max_health = stats["max_health"]
        player.coins = stats["coins"]
        player.has_double_jump = stats["has_double_jump"]
        player.speed_boost_timer = stats["speed_boost_timer"]
        player.jump_boost_timer = stats["jump_boost_timer"]
        player.shield_timer = stats["shield_timer"]
        player.double_jump_timer = stats["double_jump_timer"]
        player.shield_active = stats["shield_active"]
    
    def reset_stats(self):
        """Reset stats to default values."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.default_stats, f)
        except Exception as e:
            print(f"Error resetting player stats: {e}")
    
    def clear_stats_file(self):
        """Remove the stats file completely."""
        try:
            if os.path.exists(self.stats_file):
                os.remove(self.stats_file)
        except Exception as e:
            print(f"Error clearing player stats file: {e}")

# Global instance
player_stats = PlayerStats()
