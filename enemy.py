import pygame
import math
import constants as C

class Enemy(pygame.sprite.Sprite):
    # def __init__(self):
    #     super().__init__()
    #     self.path = C.ENEMY_PATH
    #     self.waypoints = iter(self.path)
    #     self.target_waypoint = next(self.waypoints)
        
    #     self.image = pygame.Surface((24, 24))
    #     self.image.fill(C.ENEMY_COLOR)
    #     self.rect = self.image.get_rect(center=self.target_waypoint)
        
    #     self.pos = pygame.Vector2(self.rect.center)
    #     self.speed = 2
    #     self.reached_end = False

    def __init__(self, wave_num=1):  # 1. Accept wave_num (default to 1)
        super().__init__()
        self.path = C.ENEMY_PATH
        self.waypoints = iter(self.path)
        self.target_waypoint = next(self.waypoints)
        self.max_health = 3  # Takes 3 hits to kill
        self.health = self.max_health
        
        # 2. Scaling Stats based on Wave
        # Speed: Starts at 2, increases by 0.2 every wave (cap at 6 for playability)
        self.speed = min(2 + (wave_num * 0.2), 6)
        
        # Health: If you have a health system, scale it here
        self.max_hp = 10 + (wave_num * 5)
        self.hp = self.max_hp

        # 3. Visual Feedback (Optional 2026 Polish)
        # Make enemies slightly more red or larger as waves progress
        size = min(24 + wave_num, 40) 
        self.image = pygame.Surface((size, size))
        
        # Shift color towards red as difficulty increases
        red_intensity = min(100 + (wave_num * 10), 255)
        self.image.fill((red_intensity, 50, 50)) 
        
        self.rect = self.image.get_rect(center=self.target_waypoint)
        self.pos = pygame.Vector2(self.rect.center)
        self.reached_end = False

    # Inside enemy.py -> Enemy class -> update()
    def update(self):
        target_vec = pygame.Vector2(self.target_waypoint)
        # Change 'direction' to 'self.direction'
        self.direction = target_vec - self.pos
        
        if self.direction.length() > self.speed:
            self.direction = self.direction.normalize() 
            self.pos += self.direction * self.speed
            self.rect.center = (round(self.pos.x), round(self.pos.y))
        else:
            try:
                self.target_waypoint = next(self.waypoints)
            except StopIteration:
                self.reached_end = True
    # def update(self):
    #     # Move toward target
    #     target_vec = pygame.Vector2(self.target_waypoint)
    #     direction = target_vec - self.pos
    
    #     if direction.length() > self.speed:
    #         direction = direction.normalize() * self.speed
    #         self.pos += direction
    #         self.rect.center = (round(self.pos.x), round(self.pos.y))
    #     else:
    #         # Reached waypoint, get next one
    #         try:
    #             self.target_waypoint = next(self.waypoints)
    #         except StopIteration:
    #             # This triggers the logic in main.py
    #             self.reached_end = True
    
    # Inside enemy.py -> Enemy class

    def draw_health_bar(self, surface):
        """Draws a small health bar above the enemy."""
        if self.health < self.max_health:  # Only show if they've taken damage
            # Position the bar 10 pixels above the enemy rectangle
            bar_x = self.rect.x
            bar_y = self.rect.y - 10
            bar_width = self.rect.width
            bar_height = 4
            
            # 1. Draw the Background (Red - representing lost health)
            pygame.draw.rect(surface, (150, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # 2. Calculate the width of the green portion
            health_ratio = self.health / self.max_health
            current_health_width = bar_width * health_ratio
            
            # 3. Draw the Foreground (Green - representing remaining health)
            pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, current_health_width, bar_height))