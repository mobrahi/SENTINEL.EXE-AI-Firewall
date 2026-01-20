import pygame
import constants as C
import os
import random
import threading
import textwrap
from dotenv import load_dotenv
from google import genai
from enemy import Enemy
from tower import Tower

# Initialize AI
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        pygame.display.set_caption("SENTINEL.EXE | AI Firewall")
        self.font = pygame.font.SysFont("Courier", 18)
        self.clock = pygame.time.Clock()
        
        # Stats
        self.cycles = C.STARTING_CYCLES
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

        # Add wave-tracking
        self.wave = 1
        self.enemies_spawned_this_wave = 0
        self.max_enemies_this_wave = 5 # Start small
        self.wave_active = True
     
        self.spawn_timer = 0
        self.score = 0

    # --- AI LOGIC (NON-BLOCKING) ---

    def fetch_wave_lore(self):
        """Standard lore fetch (Blocking because it's during a menu transition)"""
        try:
            prompt = "Describe a computer virus wave in one short, gritty sentence for a cyber-security game."
            response = client.models.generate_content(
                model="gemini-2.5-flash", # Use the GA stable version
                contents=prompt
            )
            self.lore_text = response.text
        except Exception:
            self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
        self.state = "PLAYING"

    def fetch_ai_advice(self):
        """Starts a background thread to get advice without freezing the game."""
        if not self.showing_advice: # Prevent multiple spam threads
            self.latest_advice = "ACCESSING TACTICAL ADVISOR..."
            self.showing_advice = True
            thread = threading.Thread(target=self._get_gemini_advice_thread)
            thread.daemon = True
            thread.start()

    def _get_gemini_advice_thread(self):
        """Worker thread with 429 error handling and local fallback."""
        try:
            stats = f"Integrity: {self.integrity}%, Cycles: {self.cycles}"
            prompt = f"Cyber-defense context. Stats: {stats}. 1-sentence tip."
        
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )
            self.latest_advice = response.text
            self.advice_timer = pygame.time.get_ticks()

        except Exception as e:
            # Check if the error is a Rate Limit (429)
            if "429" in str(e):
                print("[!] AI Quota Exceeded. Using local tactical subroutines.", flush=True)
                # Use a list of pre-written game tips from constants.py
                self.latest_advice = random.choice([
                    "ADVICE: Conserve cycles for high-density virus waves.",
                    "ADVICE: Overlapping tower ranges maximize firewall efficiency.",
                    "ADVICE: Prioritize speed-reduction nodes for fast moving packets."
                ])
            else:
                self.latest_advice = "AI_OFFLINE: Connection interrupted."
        
            self.advice_timer = pygame.time.get_ticks()

    def fetch_victory_message(self):
        """Asynchronous fetch for game over taunt."""
        def thread_target():
            try:
                prompt = "The firewall has failed. Act as a victorious computer virus. 1-sentence chilling victory message."
                response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                self.virus_taunt = response.text
            except Exception:
                self.virus_taunt = "CORE_TERMINATED: ALL DATA BELONGS TO THE HIVE."
        
        threading.Thread(target=thread_target, daemon=True).start()

    # --- CORE LOOP ---

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    # Existing space and help logic...
                    if event.key == pygame.K_SPACE and self.state == "START_MENU":
                        self.state = "AI_LOADING"
                        self.fetch_wave_lore()
                    
                    # NEW: Restart logic
                    if event.key == pygame.K_r and self.state == "GAME_OVER":
                        self.reset_game()
                    
                    if event.key == pygame.K_h and self.state == "PLAYING":
                        current_time = pygame.time.get_ticks()
                        # Only allow one request every 15 seconds to respect free tier RPM
                        if current_time - self.last_ai_request_time > 15000:
                            self.fetch_ai_advice()
                            self.last_ai_request_time = current_time
                        else:
                            self.latest_advice = "TACTICAL COOLDOWN: Wait for re-sync..."
                            self.showing_advice = True
                            self.advice_timer = pygame.time.get_ticks()
                   
                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "PLAYING" and not self.game_over:
                    if self.cycles >= C.TOWER_COST:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.towers.add(Tower(mouse_x, mouse_y))
                        self.cycles -= C.TOWER_COST
                    else:
                        print("INSUFFICIENT CYCLES!") 
    
            self.update(dt)
            self.draw()

            # Flip Buffer
            pygame.display.flip()

        pygame.quit()

    def update(self, dt):
            # Update spawn logic in your run loop
        if self.state == "PLAYING" and not self.game_over and self.wave_active:
            self.spawn_timer += dt
            # Spawn every 1.5 seconds if we haven't reached the wave cap
            if self.spawn_timer > 1500 and self.enemies_spawned_this_wave < self.max_enemies_this_wave:
                # Pass current wave to scale enemy difficulty
                self.enemies.add(Enemy(wave_num=self.wave))
                self.enemies_spawned_this_wave += 1
                self.spawn_timer = 0

            # End wave if all enemies are spawned and none are left on screen
            if self.enemies_spawned_this_wave >= self.max_enemies_this_wave and len(self.enemies) == 0:
                self.end_wave()
            
            # Sprite Updates
            self.enemies.update()
            self.towers.update(self.enemies, self.projectiles)
            self.projectiles.update()
            
            # Collisions
            hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, True, True)
            if hits:
                for enemy_hit in hits:
                    self.cycles += C.REWARD_PER_VIRUS
                    self.score += 1 # Increase score for every kill

            # Breach Detection
            for enemy in self.enemies:
                if enemy.reached_end:
                    self.integrity -= 10
                    enemy.kill()
            
            # Game Over Check
            if self.integrity <= 0:
                self.integrity = 0
                self.game_over = True
                self.state = "GAME_OVER"
                if not self.ai_called_end:
                    self.fetch_victory_message()
                    self.ai_called_end = True

            # Advice Timer Check
            if self.showing_advice and self.advice_timer != 0:
                if pygame.time.get_ticks() - self.advice_timer > 5000:
                    self.showing_advice = False
                    self.advice_timer = 0
        import textwrap

    def end_wave(self):
        """Logic for transitioning between waves."""
        self.wave += 1
        print(f"Wave {self.wave-1} Clear! Initializing Wave {self.wave}...")
        
        self.enemies_spawned_this_wave = 0
        # Increase enemy count by 2 per wave
        self.max_enemies_this_wave += 2 
        self.cycles += 50  # Bonus for completing a wave
    
        # Optionally: Pause and fetch new AI lore for the upcoming wave
        self.fetch_wave_lore()

    def draw_text_overlay(self, text, color=C.ACCENT_COLOR):
        """Renders wrapped text safely inside a UI box."""
        # Safety Check: If there is no text, don't try to wrap or draw
        if not text:
            return

        padding = 20
        rect_width = C.SCREEN_WIDTH - (padding * 2)
        overlay_rect = pygame.Rect(padding, C.SCREEN_HEIGHT - 120, rect_width, 100)
    
        # Draw the background
        pygame.draw.rect(self.screen, (0, 20, 0), overlay_rect) 
        pygame.draw.rect(self.screen, color, overlay_rect, 2)  

        # Wrap logic (Safety: Ensure width is at least 1)
        max_chars = max(1, rect_width // 10) 
        wrapped_lines = textwrap.wrap(text, width=max_chars)

        # Render lines
        for i, line in enumerate(wrapped_lines):
            # Calculate vertical position
            y_offset = overlay_rect.y + 15 + (i * 25)
        
            # Stop drawing if we exceed the box height
            if y_offset > overlay_rect.bottom - 20:
                break
            
            line_surf = self.font.render(line, True, C.TEXT_COLOR)
            self.screen.blit(line_surf, (overlay_rect.x + 10, y_offset))

    def draw(self):
        # Clear Screen
        self.screen.fill(C.BG_COLOR)
        
        if self.state in ["START_MENU", "AI_LOADING"]:
            lines = self.lore_text.split('.')
            for i, line in enumerate(lines):
                if line.strip():
                    text_surf = self.font.render(line.strip() + ".", True, C.TEXT_COLOR)
                    self.screen.blit(text_surf, (50, 100 + (i * 30)))
        
        elif self.state in ["PLAYING", "GAME_OVER"]:
            # Draw World FIRST (So UI stays on top)
            self.towers.draw(self.screen)
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)
            pygame.draw.rect(self.screen, C.CORE_COLOR, (C.SCREEN_WIDTH//2-20, C.SCREEN_HEIGHT//2-20, 40, 40))

            # Draw UI Bar
            pygame.draw.rect(self.screen, (50, 0, 0), (20, 20, 200, 20)) # Dark Red BG
            health_fill = (self.integrity / C.MAX_INTEGRITY) * 200
            pygame.draw.rect(self.screen, C.ACCENT_COLOR, (20, 20, health_fill, 20)) # Health Fill
            
            # Draw UI Text (With slight black shadow for 2026 visibility standards)
            integrity_str = f"INTEGRITY: {self.integrity}%"
            cycles_str = f"CPU_CYCLES: {self.cycles} Ghz"
            cost_str = f"NODE_COST: {C.TOWER_COST}" # Added the specific node cost

            # Draw integrity
            self.screen.blit(self.font.render(integrity_str, True, C.TEXT_COLOR), (20, 45))
            
            # Draw cycles (currency) - ensure color contrast
            self.screen.blit(self.font.render(cycles_str, True, C.ACCENT_COLOR), (20, 70))
            
            # Draw individual tower cost (so player knows how much they need)
            self.screen.blit(self.font.render(cost_str, True, (200, 200, 200)), (20, 95))

            # --- INSERT SCORE HERE (Top Right) ---
            score_text = self.font.render(f"VIRUS_PURGED: {self.score}", True, C.TEXT_COLOR)
            self.screen.blit(score_text, (C.SCREEN_WIDTH - 250, 20))

            # Overlays (Drawn last to be on very top)
            if self.showing_advice:
                self.draw_text_overlay(self.latest_advice)

            if self.state == "GAME_OVER":
                # 1. Darken the background
                overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((20, 0, 0, 210)) # Deep red tinted darkness
                self.screen.blit(overlay, (0, 0))
            
                # 2. Critical Status Text
                status_text = self.font.render("FIREWALL STATUS: [OFFLINE]", True, (255, 0, 0))
                self.screen.blit(status_text, (C.SCREEN_WIDTH//2 - 150, C.SCREEN_HEIGHT//2 - 100))
            
                # 3. FAILURE Header
                fail_text = self.font.render("CRITICAL_FAILURE: SYSTEM_REDACTED", True, (255, 50, 50))
                self.screen.blit(fail_text, (C.SCREEN_WIDTH//2 - 200, C.SCREEN_HEIGHT//2 - 60))
            
                # 4. The AI Virus Taunt (Indented to look like a console output)
                taunt_surf = self.font.render(f"> {self.virus_taunt}", True, (0, 255, 150))
                self.screen.blit(taunt_surf, (50, C.SCREEN_HEIGHT//2 + 10))
            
                # 5. REBOOT Instruction (Centered at bottom)
                reboot_text = self.font.render("--- PRESS 'R' TO REBOOT SYSTEM ---", True, (255, 255, 255))
                self.screen.blit(reboot_text, (C.SCREEN_WIDTH//2 - 180, C.SCREEN_HEIGHT - 80))
    
    def reset_game(self):
        """Resets all game variables for a new session."""
        self.integrity = C.MAX_INTEGRITY
        self.cycles = C.STARTING_CYCLES
        self.game_over = False
        self.ai_called_end = False
        self.spawn_timer = 0
        self.virus_taunt = ""
        self.score = 0
        
        # Clear all active sprites
        self.enemies.empty()
        self.towers.empty()
        self.projectiles.empty()
        
        # Go back to the lore screen or main menu
        self.state = "START_MENU"
        self.lore_text = "Firewall Re-initialized. Press SPACE to start..."

if __name__ == "__main__":
    game = GameApp()
    game.run()
