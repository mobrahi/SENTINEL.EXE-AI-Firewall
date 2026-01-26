import pygame
import constants as C
import math

class Tower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Align to grid
        grid_x = (x // C.TILE_SIZE) * C.TILE_SIZE + C.TILE_SIZE // 2
        grid_y = (y // C.TILE_SIZE) * C.TILE_SIZE + C.TILE_SIZE // 2
        
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, C.TOWER_COLOR, (0, 0, 30, 30), border_radius=5)
        self.rect = self.image.get_rect(center=(grid_x, grid_y))
        
        self.range = C.TOWER_RANGE
        self.last_shot = pygame.time.get_ticks()

    def update(self, enemies, projectiles):
        now = pygame.time.get_ticks()
        if now - self.last_shot > C.TOWER_COOLDOWN:
            # Find the closest enemy
            target = self.find_target(enemies)
            if target:
                self.fire(target, projectiles)
                self.last_shot = now

    def find_target(self, enemies):
        best_target = None
        min_dist = self.range
        
        for enemy in enemies:
            dist = pygame.Vector2(self.rect.center).distance_to(enemy.rect.center)
            if dist < min_dist:
                min_dist = dist
                best_target = enemy
        return best_target

    def fire(self, target, projectiles):
        # We will create the Projectile class next!
        new_projectile = Projectile(self.rect.center, target)
        projectiles.add(new_projectile)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target):
        super().__init__()
        self.image = pygame.Surface((8, 8))
        self.image.fill(C.ACCENT_COLOR) # Cyan
        self.rect = self.image.get_rect(center=start_pos)
        
        self.pos = pygame.Vector2(start_pos)
        self.target = target
        self.speed = C.PROJECTILE_SPEED

    def update(self):
        if not self.target.alive():
            self.kill()
            return

        # Move toward target enemy
        target_pos = pygame.Vector2(self.target.rect.center)
        direction = (target_pos - self.pos).normalize()
        self.pos += direction * self.speed
        self.rect.center = self.pos