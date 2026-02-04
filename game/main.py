import asyncio
import pygame
import os
import random
import textwrap
import importlib
import threading

# --- THE GHOST LAYER ---
WEB_MODE = os.path.exists('/dev/canvas') or os.path.exists('/home/webuser')

genai = None
client = None

if not WEB_MODE:
    try:
        d_mod = "desktop" + "_imports" 
        desktop = importlib.import_module(d_mod)
        genai = desktop.genai
        client = desktop.client
    except Exception as e:
        print(f"Desktop AI Load Failed: {e}")

try:
    C = importlib.import_module("constants")
    Enemy = importlib.import_module("enemy").Enemy
    Tower = importlib.import_module("tower").Tower
except ImportError as e:
    print(f"Critical Module Load Failure: {e}")

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        pygame.display.set_caption("SENTINEL.EXE | AI Firewall")
        self.font = pygame.font.SysFont(None, 24)
        self.clock = pygame.time.Clock()

        self.core_rect = pygame.Rect(1280//2-20, 720//2-20, 40, 40)
        
        # Stats
        self.cycles = 100
        self.integrity = C.MAX_INTEGRITY
        self.game_over = False
        
        # AI & State Management
        self.state = "START_MENU" 
        self.lore_text = "Press SPACE to initialize Firewall Lore..."
        self.virus_taunt = ""
        self.ai_called_end = False
        
        # Advice System Variables
        self.showing_advice = False
        self.latest_advice = ""
        self.advice_timer = 0
        self.last_ai_request_time = 0

        # Sprite Groups
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        # Wave-tracking
        self.wave = 1
        self.enemies_spawned_this_wave = 0
        self.max_enemies_this_wave = 5 
        self.wave_active = True
     
        self.spawn_timer = 0
        self.score = 0
        self.flash_timer = 0

    # --- AI LOGIC (ASYNC & NON-BLOCKING) ---
    async def fetch_wave_lore(self):
        """Async lore fetch: Uses threads on Desktop, local backup on Web."""
        self.state = "AI_LOADING"
        # 1. Guard for Web or Missing Client
        if WEB_MODE or client is None: 
            self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
        else:
            try:
                def call_api():
                    prompt = "Describe a computer virus wave in one short, gritty sentence."
                    # Ensure you use the correct SDK method here
                    return client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                
                response = await asyncio.to_thread(call_api)
                self.lore_text = response.text
            except Exception:
                self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
        
        self.state = "PLAYING"

    def fetch_ai_advice(self):
        """Guarded thread creation for Desktop only."""
        if WEB_MODE or client is None:
            self.latest_advice = random.choice(C.LOCAL_LORE_BACKUP)
            self.showing_advice = True
            self.advice_timer = pygame.time.get_ticks()
            return # <--- IMPORTANT: Exit before touching 'threading'

        if not self.showing_advice:
            self.latest_advice = "ACCESSING TACTICAL ADVISOR..."
            self.showing_advice = True
            # Only desktop reaches here
            thread = threading.Thread(target=self._get_gemini_advice_thread)
            thread.daemon = True
            thread.start()

    def _get_gemini_advice_thread(self):
        try:
            stats = f"Integrity: {self.integrity}%, Cycles: {self.cycles}"
            prompt = f"Cyber-defense context. Stats: {stats}. 1-sentence tip."
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            self.latest_advice = response.text
        except Exception as e:
            if "429" in str(e):
                self.latest_advice = random.choice([
                    "ADVICE: Conserve cycles for high-density virus waves.",
                    "ADVICE: Overlapping tower ranges maximize efficiency.",
                    "ADVICE: Prioritize nodes for fast moving packets."
                ])
            else:
                self.latest_advice = "AI_OFFLINE: Connection interrupted."
        self.advice_timer = pygame.time.get_ticks()

    def fetch_victory_message(self):
        """Guarded thread creation for Desktop only."""
        if WEB_MODE or client is None:
            self.virus_taunt = "CORE_TERMINATED: ALL DATA BELONGS TO THE HIVE."
            return

        def thread_target():
            try:
                prompt = "The firewall has failed. Act as a victorious computer virus. 1-sentence message."
                response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                self.virus_taunt = response.text
            except Exception:
                self.virus_taunt = "CORE_TERMINATED: ALL DATA BELONGS TO THE HIVE."
        
        threading.Thread(target=thread_target, daemon=True).start()

    # --- CORE LOOP (UPDATED FOR ASYNC) ---

    async def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "START_MENU":
                        # We use 'create_task' so the lore fetches while the game keeps drawing
                        asyncio.create_task(self.fetch_wave_lore())
                    
                    if event.key == pygame.K_r and self.state == "GAME_OVER":
                        self.reset_game()
                    
                    if event.key == pygame.K_h and self.state == "PLAYING":
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_ai_request_time > 15000:
                            self.fetch_ai_advice()
                            self.last_ai_request_time = current_time
                        else:
                            self.latest_advice = "TACTICAL COOLDOWN: Wait for re-sync..."
                            self.showing_advice = True
                            self.advice_timer = pygame.time.get_ticks()
                   
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "PLAYING" and not self.game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    self.attempt_place_tower(mouse_pos)
    
            self.update(dt)
            self.draw()

            pygame.display.flip()
            # CRITICAL: This line allows the browser to process events
            await asyncio.sleep(0) 

        pygame.quit()

    def attempt_place_tower(self, pos):
        if self.cycles >= C.TOWER_COST:
            new_tower = Tower(pos[0], pos[1])
            if not pygame.sprite.spritecollideany(new_tower, self.towers):
                self.towers.add(new_tower)
                self.cycles -= C.TOWER_COST
            else:
                print("PLACEMENT BLOCKED")
        else:
            self.fetch_ai_advice()

    def update(self, dt):
        if self.state == "PLAYING" and not self.game_over:
            self.spawn_timer += dt
            if self.spawn_timer > 1500 and self.enemies_spawned_this_wave < self.max_enemies_this_wave:
                self.enemies.add(Enemy(wave_num=self.wave))
                self.enemies_spawned_this_wave += 1
                self.spawn_timer = 0

            if self.enemies_spawned_this_wave >= self.max_enemies_this_wave and len(self.enemies) == 0:
                self.end_wave()
            
            self.enemies.update()
            self.towers.update(self.enemies, self.projectiles)
            self.projectiles.update()
            
            # Collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, False, True)
            if hits:
                for enemy_hit in hits:
                    enemy_hit.health -= 1
                    if enemy_hit.health <= 0:
                        enemy_hit.kill()
                        self.cycles += C.REWARD_PER_VIRUS
                        self.score += 1
           
            for enemy in self.enemies:
                if enemy.rect.colliderect(self.core_rect):
                    self.integrity -= 0.1 
                    if pygame.time.get_ticks() % 500 < 20: 
                        self.flash_timer = pygame.time.get_ticks()
                if enemy.reached_end:
                    self.integrity -= 10
                    enemy.kill()
            
            if self.integrity <= 0:
                self.integrity = 0
                self.game_over = True
                self.state = "GAME_OVER"
                if not self.ai_called_end:
                    self.fetch_victory_message()
                    self.ai_called_end = True

            if self.showing_advice and self.advice_timer != 0:
                if pygame.time.get_ticks() - self.advice_timer > 5000:
                    self.showing_advice = False

    def end_wave(self):
        self.wave += 1
        self.enemies_spawned_this_wave = 0
        self.max_enemies_this_wave += 2 
        self.cycles += 50  
        asyncio.create_task(self.fetch_wave_lore())

    def draw_text_overlay(self, text, color=C.ACCENT_COLOR):
        if not text: return
        padding = 20
        rect_width = C.SCREEN_WIDTH - (padding * 2)
        overlay_rect = pygame.Rect(padding, C.SCREEN_HEIGHT - 120, rect_width, 100)
        pygame.draw.rect(self.screen, (0, 20, 0), overlay_rect) 
        pygame.draw.rect(self.screen, color, overlay_rect, 2)  

        max_chars = max(1, rect_width // 10) 
        wrapped_lines = textwrap.wrap(text, width=max_chars)
        for i, line in enumerate(wrapped_lines):
            y_offset = overlay_rect.y + 15 + (i * 25)
            if y_offset > overlay_rect.bottom - 20: break
            line_surf = self.font.render(line, True, C.TEXT_COLOR)
            self.screen.blit(line_surf, (overlay_rect.x + 10, y_offset))

    def draw(self):
        self.screen.fill(C.BG_COLOR)
        
        if self.state in ["START_MENU", "AI_LOADING"]:
            msg = "INITIALIZING GEMINI LORE..." if self.state == "AI_LOADING" else self.lore_text
            lines = msg.split('.')
            for i, line in enumerate(lines):
                if line.strip():
                    text_surf = self.font.render(line.strip() + ".", True, C.TEXT_COLOR)
                    self.screen.blit(text_surf, (50, 100 + (i * 30)))
        
        elif self.state in ["PLAYING", "GAME_OVER"]:
            self.towers.draw(self.screen)
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)
            pygame.draw.rect(self.screen, C.CORE_COLOR, (C.SCREEN_WIDTH//2-20, C.SCREEN_HEIGHT//2-20, 40, 40))

            for enemy in self.enemies:
                enemy.draw_health_bar(self.screen)

            # UI
            pygame.draw.rect(self.screen, (50, 0, 0), (20, 20, 200, 20))
            health_fill = (max(0, self.integrity) / C.MAX_INTEGRITY) * 200
            pygame.draw.rect(self.screen, C.ACCENT_COLOR, (20, 20, health_fill, 20))
            
            self.screen.blit(self.font.render(f"INTEGRITY: {int(self.integrity)}%", True, C.TEXT_COLOR), (20, 45))
            self.screen.blit(self.font.render(f"CPU_CYCLES: {self.cycles} Ghz", True, C.ACCENT_COLOR), (C.SCREEN_WIDTH - 255, 0))
            self.screen.blit(self.font.render(f"VIRUS_PURGED: {self.score}", True, C.TEXT_COLOR), (C.SCREEN_WIDTH - 250, 20))

            if self.showing_advice:
                self.draw_text_overlay(self.latest_advice)

            if self.state == "GAME_OVER":
                overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((20, 0, 0, 210))
                self.screen.blit(overlay, (0, 0))
                fail_text = self.font.render("CRITICAL_FAILURE: SYSTEM_REDACTED", True, (255, 50, 50))
                self.screen.blit(fail_text, (C.SCREEN_WIDTH//2 - 200, C.SCREEN_HEIGHT//2 - 60))
                taunt_surf = self.font.render(f"> {self.virus_taunt}", True, (0, 255, 150))
                self.screen.blit(taunt_surf, (50, C.SCREEN_HEIGHT//2 + 10))

        if self.state == "PLAYING" and pygame.time.get_ticks() - self.flash_timer < 100:
            flash_surf = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
            flash_surf.set_alpha(128)
            flash_surf.fill((255, 0, 0))
            self.screen.blit(flash_surf, (0, 0))

    def reset_game(self):
        self.integrity = C.MAX_INTEGRITY
        self.cycles = C.STARTING_CYCLES
        self.game_over = False
        self.ai_called_end = False
        self.score = 0
        self.enemies.empty()
        self.towers.empty()
        self.projectiles.empty()
        self.state = "START_MENU"
        self.lore_text = "Firewall Re-initialized. Press SPACE to start..."

# --- PYGBAG ENTRY POINT ---
async def main():
    game = GameApp()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())
