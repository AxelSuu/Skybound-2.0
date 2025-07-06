#!/usr/bin/env python3
"""
Skybound Achievement System

This module implements a comprehensive achievement system that tracks
player accomplishments and provides rewards for various gameplay milestones.

The achievement system includes:
- Progress tracking for various game metrics
- Persistent storage of unlocked achievements
- Reward system for unlocking achievements
- Visual notifications and feedback
- Achievement browsing and statistics

Achievement Categories:
- Level Progression: Completing levels and reaching milestones
- Collection: Gathering coins and items
- Combat: Defeating enemies and survival challenges
- Skill: Speed runs, no-damage runs, and special challenges
- Exploration: Finding secrets and hidden areas

The system is designed to encourage player engagement through meaningful
goals and recognition of player skill and dedication.

Author: Axel Suu
Date: July 2025
"""

import os
import json
from datetime import datetime


class Achievement:
    """
    Individual achievement class representing a single accomplishment.
    
    Each achievement has:
    - Unique identifier and display information
    - Progress tracking towards completion
    - Unlock status and date tracking
    - Optional rewards for completion
    
    Achievements can be either binary (unlocked/locked) or progressive
    (with tracked progress towards a goal).
    
    Attributes:
        id (str): Unique identifier for the achievement
        name (str): Display name for the achievement
        description (str): Detailed description of requirements
        icon (str): Icon identifier for visual representation
        requirement (int): Target value for unlocking
        reward (int): Reward value (usually coins) for unlocking
        unlocked (bool): Whether the achievement is unlocked
        progress (int): Current progress towards requirement
        unlock_date (str): Date when achievement was unlocked
    """
    
    def __init__(self, id, name, description, icon, requirement, reward=0):
        """
        Initialize an achievement with specified parameters.
        
        Args:
            id (str): Unique identifier
            name (str): Display name
            description (str): Requirement description
            icon (str): Icon identifier
            requirement (int): Target value for completion
            reward (int): Reward for unlocking (default: 0)
        """
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.requirement = requirement
        self.reward = reward
        self.unlocked = False
        self.progress = 0
        self.unlock_date = None
        
    def check_unlock(self, current_value):
        """
        Check if achievement should be unlocked based on current progress.
        
        Args:
            current_value (int): Current progress value to check
            
        Returns:
            bool: True if achievement was newly unlocked, False otherwise
        """
        if not self.unlocked:
            # Update progress (capped at requirement)
            self.progress = min(current_value, self.requirement)
            
            # Check if requirement is met
            if current_value >= self.requirement:
                self.unlock()
                return True
        return False
        
    def unlock(self):
        """Unlock this achievement"""
        self.unlocked = True
        self.unlock_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def get_progress_percentage(self):
        """Get progress as percentage"""
        return min(100, int((self.progress / self.requirement) * 100))
        
    def to_dict(self):
        """Convert achievement to dictionary for saving"""
        return {
            'id': self.id,
            'unlocked': self.unlocked,
            'progress': self.progress,
            'unlock_date': self.unlock_date
        }
        
    def from_dict(self, data):
        """Load achievement from dictionary"""
        self.unlocked = data.get('unlocked', False)
        self.progress = data.get('progress', 0)
        self.unlock_date = data.get('unlock_date', None)


class AchievementManager:
    """Manages all achievements"""
    def __init__(self):
        self.achievements = {}
        self.txt_folder_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "txts")
        )
        self.achievements_file = os.path.join(self.txt_folder_path, "achievements.json")
        
        self.init_achievements()
        self.load_achievements()
        
    def init_achievements(self):
        """Initialize all achievements"""
        achievements_data = [
            {
                'id': 'first_level',
                'name': 'First Steps',
                'description': 'Complete your first level',
                'icon': '🎯',
                'requirement': 1,
                'reward': 5
            },
            {
                'id': 'level_5',
                'name': 'Getting Started',
                'description': 'Reach level 5',
                'icon': '🏃',
                'requirement': 5,
                'reward': 10
            },
            {
                'id': 'level_10',
                'name': 'Skilled Jumper',
                'description': 'Reach level 10',
                'icon': '🦘',
                'requirement': 10,
                'reward': 20
            },
            {
                'id': 'level_25',
                'name': 'Sky Master',
                'description': 'Reach level 25',
                'icon': '👑',
                'requirement': 25,
                'reward': 50
            },
            {
                'id': 'collect_100_coins',
                'name': 'Coin Collector',
                'description': 'Collect 100 coins',
                'icon': '🪙',
                'requirement': 100,
                'reward': 15
            },
            {
                'id': 'collect_500_coins',
                'name': 'Treasure Hunter',
                'description': 'Collect 500 coins',
                'icon': '💰',
                'requirement': 500,
                'reward': 50
            },
            {
                'id': 'no_damage_level',
                'name': 'Untouchable',
                'description': 'Complete a level without taking damage',
                'icon': '🛡️',
                'requirement': 1,
                'reward': 25
            },
            {
                'id': 'use_10_powerups',
                'name': 'Power User',
                'description': 'Use 10 power-ups',
                'icon': '⚡',
                'requirement': 10,
                'reward': 15
            },
            {
                'id': 'defeat_10_enemies',
                'name': 'Monster Slayer',
                'description': 'Survive 10 enemy encounters',
                'icon': '⚔️',
                'requirement': 10,
                'reward': 20
            },
            {
                'id': 'speed_run',
                'name': 'Speed Demon',
                'description': 'Complete a level in under 30 seconds',
                'icon': '🏎️',
                'requirement': 1,
                'reward': 30
            },
            {
                'id': 'jump_master',
                'name': 'Jump Master',
                'description': 'Make 1000 jumps',
                'icon': '🦘',
                'requirement': 1000,
                'reward': 25
            },
            {
                'id': 'hat_collector',
                'name': 'Fashion Forward',
                'description': 'Buy your first hat',
                'icon': '🎩',
                'requirement': 1,
                'reward': 10
            }
        ]
        
        for data in achievements_data:
            achievement = Achievement(
                data['id'],
                data['name'],
                data['description'],
                data['icon'],
                data['requirement'],
                data['reward']
            )
            self.achievements[data['id']] = achievement
            
    def load_achievements(self):
        """Load achievement progress from file"""
        try:
            with open(self.achievements_file, 'r') as f:
                data = json.load(f)
                for achievement_data in data:
                    achievement_id = achievement_data['id']
                    if achievement_id in self.achievements:
                        self.achievements[achievement_id].from_dict(achievement_data)
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is corrupted, use defaults
            pass
            
    def save_achievements(self):
        """Save achievement progress to file"""
        try:
            data = [achievement.to_dict() for achievement in self.achievements.values()]
            with open(self.achievements_file, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass  # Ignore save errors
            
    def check_achievement(self, achievement_id, current_value):
        """Check if an achievement should be unlocked"""
        if achievement_id in self.achievements:
            was_unlocked = self.achievements[achievement_id].check_unlock(current_value)
            if was_unlocked:
                self.save_achievements()
                return self.achievements[achievement_id]
        return None
        
    def get_achievement(self, achievement_id):
        """Get an achievement by ID"""
        return self.achievements.get(achievement_id)
        
    def get_all_achievements(self):
        """Get all achievements"""
        return list(self.achievements.values())
        
    def get_unlocked_achievements(self):
        """Get all unlocked achievements"""
        return [ach for ach in self.achievements.values() if ach.unlocked]
        
    def get_locked_achievements(self):
        """Get all locked achievements"""
        return [ach for ach in self.achievements.values() if not ach.unlocked]
        
    def get_completion_percentage(self):
        """Get overall completion percentage"""
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())
        return int((unlocked / total) * 100) if total > 0 else 0
        
    def get_total_rewards_earned(self):
        """Get total rewards earned from achievements"""
        return sum(ach.reward for ach in self.achievements.values() if ach.unlocked)


# Global achievement manager instance
achievement_manager = AchievementManager()


# Convenience functions for easy access
def check_level_achievement(level):
    """Check level-based achievements"""
    unlocked = []
    unlocked.append(achievement_manager.check_achievement('first_level', level))
    unlocked.append(achievement_manager.check_achievement('level_5', level))
    unlocked.append(achievement_manager.check_achievement('level_10', level))
    unlocked.append(achievement_manager.check_achievement('level_25', level))
    return [ach for ach in unlocked if ach is not None]


def check_coin_achievement(total_coins):
    """Check coin collection achievements"""
    unlocked = []
    unlocked.append(achievement_manager.check_achievement('collect_100_coins', total_coins))
    unlocked.append(achievement_manager.check_achievement('collect_500_coins', total_coins))
    return [ach for ach in unlocked if ach is not None]


def check_powerup_achievement(total_powerups):
    """Check power-up usage achievements"""
    return achievement_manager.check_achievement('use_10_powerups', total_powerups)


def check_enemy_achievement(total_enemies):
    """Check enemy encounter achievements"""
    return achievement_manager.check_achievement('defeat_10_enemies', total_enemies)


def check_no_damage_achievement():
    """Check no damage achievement"""
    return achievement_manager.check_achievement('no_damage_level', 1)


def check_speed_run_achievement():
    """Check speed run achievement"""
    return achievement_manager.check_achievement('speed_run', 1)


def check_jump_achievement(total_jumps):
    """Check jump-based achievements"""
    return achievement_manager.check_achievement('jump_master', total_jumps)


def check_hat_achievement():
    """Check hat purchase achievement"""
    return achievement_manager.check_achievement('hat_collector', 1)


def get_all_achievements():
    """Get all achievements"""
    return achievement_manager.get_all_achievements()


def get_unlocked_achievements():
    """Get all unlocked achievements"""
    return achievement_manager.get_unlocked_achievements()


def get_completion_percentage():
    """Get completion percentage"""
    return achievement_manager.get_completion_percentage()


def get_total_rewards_earned():
    """Get total rewards earned"""
    return achievement_manager.get_total_rewards_earned()
