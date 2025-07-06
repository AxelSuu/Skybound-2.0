import pygame as pg
import os
from utils.draw_text import draw_text
from utils.achievements import get_all_achievements, get_completion_percentage

""" Achievement display screen """


class AchievementScreen:
    def __init__(self):
        self.WIDTH = 480
        self.HEIGHT = 600
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.LIGHTBLUE = (135, 206, 235)
        self.GREEN = (0, 255, 0)
        self.GOLD = (255, 215, 0)
        self.GRAY = (128, 128, 128)
        
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.achievements_active = True
        self.scroll_offset = 0
        self.achievements = get_all_achievements()
        
        self.show_achievements()
        
    def show_achievements(self):
        """Display the achievements screen"""
        while self.achievements_active:
            self.screen.fill(self.LIGHTBLUE)
            
            # Title
            draw_text(self.screen, "Achievements", 30, self.WIDTH / 2, 30)
            
            # Completion percentage
            completion = get_completion_percentage()
            draw_text(self.screen, f"Completion: {completion}%", 16, self.WIDTH / 2, 60)
            
            # Progress bar
            bar_width = 200
            bar_height = 10
            bar_x = self.WIDTH / 2 - bar_width / 2
            bar_y = 75
            
            # Background bar
            pg.draw.rect(self.screen, self.WHITE, (bar_x, bar_y, bar_width, bar_height))
            pg.draw.rect(self.screen, self.BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Progress fill
            fill_width = int(bar_width * (completion / 100))
            pg.draw.rect(self.screen, self.GREEN, (bar_x, bar_y, fill_width, bar_height))
            
            # Achievements list
            start_y = 100
            achievement_height = 60
            visible_achievements = (self.HEIGHT - start_y - 50) // achievement_height
            
            for i, achievement in enumerate(self.achievements):
                y_pos = start_y + i * achievement_height - self.scroll_offset
                
                # Skip achievements that are off-screen
                if y_pos < start_y - achievement_height or y_pos > self.HEIGHT:
                    continue
                    
                # Achievement background
                ach_rect = pg.Rect(20, y_pos, self.WIDTH - 40, achievement_height - 5)
                color = self.GOLD if achievement.unlocked else self.GRAY
                pg.draw.rect(self.screen, color, ach_rect)
                pg.draw.rect(self.screen, self.BLACK, ach_rect, 2)
                
                # Achievement icon
                icon_text = achievement.icon if achievement.unlocked else "🔒"
                draw_text(self.screen, icon_text, 24, 50, y_pos + 15)
                
                # Achievement name
                name_color = self.BLACK if achievement.unlocked else self.WHITE
                draw_text(self.screen, achievement.name, 18, 200, y_pos + 10)
                
                # Achievement description
                draw_text(self.screen, achievement.description, 12, 200, y_pos + 25)
                
                # Progress bar for locked achievements
                if not achievement.unlocked:
                    progress_bar_width = 100
                    progress_bar_height = 6
                    progress_x = self.WIDTH - 130
                    progress_y = y_pos + 35
                    
                    # Progress background
                    pg.draw.rect(self.screen, self.WHITE, 
                               (progress_x, progress_y, progress_bar_width, progress_bar_height))
                    
                    # Progress fill
                    progress_fill = int(progress_bar_width * (achievement.progress / achievement.requirement))
                    pg.draw.rect(self.screen, self.GREEN,
                               (progress_x, progress_y, progress_fill, progress_bar_height))
                    
                    # Progress text
                    progress_text = f"{achievement.progress}/{achievement.requirement}"
                    draw_text(self.screen, progress_text, 10, progress_x + progress_bar_width/2, progress_y + 15)
                    
                # Reward text
                if achievement.unlocked:
                    reward_text = f"Reward: {achievement.reward} coins"
                    draw_text(self.screen, reward_text, 10, self.WIDTH - 80, y_pos + 45)
                else:
                    reward_text = f"Reward: {achievement.reward} coins"
                    draw_text(self.screen, reward_text, 10, self.WIDTH - 80, y_pos + 45)
            
            # Instructions
            draw_text(self.screen, "Use UP/DOWN arrows to scroll", 12, self.WIDTH / 2, self.HEIGHT - 40)
            draw_text(self.screen, "Press ESC to return", 12, self.WIDTH / 2, self.HEIGHT - 20)
            
            # Handle events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.achievements_active = False
                    
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.achievements_active = False
                    elif event.key == pg.K_UP:
                        self.scroll_offset = max(0, self.scroll_offset - 30)
                    elif event.key == pg.K_DOWN:
                        max_scroll = max(0, len(self.achievements) * achievement_height - (self.HEIGHT - start_y - 50))
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 30)
                        
                elif event.type == pg.MOUSEWHEEL:
                    # Mouse wheel scrolling
                    if event.y > 0:  # Scroll up
                        self.scroll_offset = max(0, self.scroll_offset - 30)
                    elif event.y < 0:  # Scroll down
                        max_scroll = max(0, len(self.achievements) * achievement_height - (self.HEIGHT - start_y - 50))
                        self.scroll_offset = min(max_scroll, self.scroll_offset + 30)
            
            pg.display.flip()
