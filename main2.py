import pygame
import constants as C
import os
import random
import threading
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
        self.cycles = C.STARTING_CYCLES
        
        # Stats
        self.integrity = C.MAX_INTEGRITY
        self.game_over = False
        self.virus_taunt = "" # Stores the AI's victory message      
        self.ai_called_end = False # Flag to prevent multiple calls

        # Game State
        self.state = "START_MENU" 
        self.lore_text = "Press SPACE to initialize Firewall Lore..."
        
        # Sprite Groups
        self.enemies = pygame.sprite.Group()
        self.towers = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        self.spawn_timer = 0
        self.advice_timer = 0

        # Initialize the new state variables
        self.showing_advice = False
        self.latest_advice = None

    def fetch_wave_lore(self):
        """Calls Gemini to get a description, with a robust local fallback."""
        try:
            prompt = "Describe a computer virus wave in one short, gritty sentence for a cyber-security game."
            response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
            self.lore_text = response.text
            self.state = "PLAYING"
        except Exception as e:
            # This is the 'Responsible AI' Fallback Pillar in action
            print(f"AI Unavailable ({e}). Switching to Local Subroutines.")
            self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
            self.state = "PLAYING"
            # self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
            # self.state = "PLAYING"

    def fetch_victory_message(self):
        """Generates a taunt from the virus persona upon winning."""
        try:
            #prompt = "Act as a victorious sentient computer virus. Write a 1-sentence chilling victory message."
            prompt = (
                "The firewall has failed. Act as a victorious sentient computer virus "
                "that just bypassed the final security layer. Write a 1-sentence, "
                "chilling victory message to the human user."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=prompt
            )
            self.virus_taunt = response.text
        except Exception as e:
            print(f"AI Taunt Failed: {e}")
            self.virus_taunt = "CORE_TERMINATED: ALL DATA BELONGS TO THE HIVE."

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS) # Get time between frames

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "START_MENU":
                        self.state = "AI_LOADING"
                        self.fetch_wave_lore()
                    
                    if event.key == pygame.K_h and self.state == "PLAYING":
                        self.fetch_ai_advice()
                        self.showing_advice = True

                if event.type == pygame.MOUSEBUTTONDOWN and self.state == "PLAYING" and not self.game_over:
                    if self.cycles >= C.TOWER_COST:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.towers.add(Tower(mouse_x, mouse_y))
                        self.cycles -= C.TOWER_COST
                        print(f"Tower Deployed. Cycles remaining: {self.cycles}")
                    else:
                        print("INSUFFICIENT CYCLES!")                    

            # --- UPDATE LOGIC ---
            if self.state == "PLAYING" and not self.game_over:
                # Spawn an enemy every 2 seconds (2000 ms)
                self.spawn_timer += dt
                if self.spawn_timer > 2000:
                    self.enemies.add(Enemy())
                    self.spawn_timer = 0
                
                self.enemies.update()
                self.towers.update(self.enemies, self.projectiles)
                self.projectiles.update()
                
                # This checks if any projectile hit any enemy. 
                # True, True means BOTH the projectile and the enemy get removed (killed).
                hits = pygame.sprite.groupcollide(self.enemies, self.projectiles, True, True)
    
                if hits:
                    # 'hits' is a dictionary. Each key is an enemy that was hit.
                    for enemy_hit in hits:
                        self.cycles += C.REWARD_PER_VIRUS
                        print(f"Virus Purged! +{C.REWARD_PER_VIRUS} Cycles. Total: {self.cycles}")

                for enemy in self.enemies:
                    if enemy.reached_end:
                        self.integrity -= 10
                        enemy.kill() # Remove so it doesn't keep damaging
                        print(f"INTEGRITY BREACH! Current Integrity: {self.integrity}")
                
                if self.integrity <= 0:
                    self.integrity = 0
                    self.state = "GAME_OVER"
                    if not self.ai_called_end:
                        self.fetch_victory_message()
                        self.ai_called_end = True

                if self.showing_advice:
                    current_time = pygame.time.get_ticks()
                    # If 5 seconds (5000ms) have passed, hide the advice
                    if current_time - self.advice_timer > 5000:
                        self.showing_advice = False

                # if self.state == "SHOWING_ADVICE":
                #     if pygame.time.get_ticks() - self.advice_timer > 5000: # 5 seconds
                #         self.state = "PLAYING"

            self.draw()

        pygame.quit()

    def draw(self):
        #self.draw_game_world()
        self.screen.fill(C.BG_COLOR)
        
        if self.state == "START_MENU" or self.state == "AI_LOADING":
            # Display lore/instructions
            lines = self.lore_text.split('.')
            for i, line in enumerate(lines):
                text_surf = self.font.render(line.strip(), True, C.TEXT_COLOR)
                self.screen.blit(text_surf, (50, 100 + (i * 30)))
            # text_surf = self.font.render(self.lore_text, True, C.TEXT_COLOR)
            # self.screen.blit(text_surf, (50, C.SCREEN_HEIGHT // 2))
        
        elif self.state == "PLAYING" or self.state == "GAME_OVER":
            # Grid
            for x in range(0, C.SCREEN_WIDTH, C.TILE_SIZE):
                pygame.draw.line(self.screen, C.GRID_COLOR, (x, 0), (x, C.SCREEN_HEIGHT))
            for y in range(0, C.SCREEN_HEIGHT, C.TILE_SIZE):
                pygame.draw.line(self.screen, C.GRID_COLOR, (0, y), (C.SCREEN_WIDTH, y))

            # Entities
            pygame.draw.rect(self.screen, C.CORE_COLOR, (C.SCREEN_WIDTH//2-20, C.SCREEN_HEIGHT//2-20, 40, 40))
            self.towers.draw(self.screen)
            self.enemies.draw(self.screen)
            self.projectiles.draw(self.screen)

            # Health Bar
            pygame.draw.rect(self.screen, (50, 0, 0), (20, 20, 200, 20))
            health_fill = (self.integrity / C.MAX_INTEGRITY) * 200
            pygame.draw.rect(self.screen, C.ACCENT_COLOR, (20, 20, health_fill, 20))
            label = self.font.render(f"SYSTEM_INTEGRITY: {self.integrity}%", True, C.TEXT_COLOR)
            self.screen.blit(label, (20, 45))

            cycle_text = self.font.render(f"CPU_CYCLES: {self.cycles} Ghz", True, C.ACCENT_COLOR)
            self.screen.blit(cycle_text, (20, 70))

            # Add a small hint
            cost_text = self.font.render(f"NODE_COST: {C.TOWER_COST}", True, (150, 150, 150))
            self.screen.blit(cost_text, (20, 95))

        if self.state == "GAME_OVER":
            overlay = pygame.Surface((C.SCREEN_WIDTH, C.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200)) 
            self.screen.blit(overlay, (0,0))
            
            fail_text = self.font.render("CRITICAL_FAILURE: SYSTEM_REDACTED", True, (255, 50, 50))
            self.screen.blit(fail_text, (C.SCREEN_WIDTH//2 - 200, C.SCREEN_HEIGHT//2 - 50))
            
            # Virus Taunt
            taunt_surf = self.font.render(f"> {self.virus_taunt}", True, (0, 255, 150))
            self.screen.blit(taunt_surf, (50, C.SCREEN_HEIGHT//2 + 20))

        if self.state == "SHOWING_ADVICE":
            # Draw a semi-transparent box for the advice
            overlay = pygame.Surface((C.SCREEN_WIDTH, 100), pygame.SRCALPHA)
            overlay.fill((0, 40, 80, 200)) # Dark blue tech feel
            self.screen.blit(overlay, (0, C.SCREEN_HEIGHT - 100))
            
            # Render the advice text
            advice_surf = self.font.render(self.lore_text, True, (0, 255, 255))
            self.screen.blit(advice_surf, (50, C.SCREEN_HEIGHT - 60))

        if self.showing_advice:
            self.draw_text_overlay(self.lore_text)

        # if self.showing_advice and self.latest_advice:
        #  self.draw_advice_overlay(self.latest_advice)

        pygame.display.flip()

    def fetch_ai_advice(self):
        """Starts a background thread to get advice without freezing the game."""
        # Show a loading state so the player knows something is happening
        self.lore_text = "ACCESSING AI ADVISOR..."
        self.showing_advice = True 
    
        # Start the network request in a separate thread
        thread = threading.Thread(target=self._get_gemini_response)
        thread.daemon = True  # Ensures the thread closes if you exit the game
        thread.start()

    def _get_gemini_response(self):
        """The actual network call running in the background."""
        try:
            stats = f"Integrity: {self.integrity}%, Cycles: {self.cycles}, Towers: {len(self.towers)}"
            prompt = (f"Context: Cyber-defense game. Stats: {stats}. "
                        "Act as tactical AI. 1-sentence tip.")
        
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt
            )
            # Update the text once the response arrives
            self.lore_text = f"AI_ADVICE: {response.text}"
            # Set a timer to automatically hide the advice after 5 seconds
            self.advice_timer = pygame.time.get_ticks() 
        except Exception:
            self.lore_text = "AI_OFFLINE: Connection lost."

    # def fetch_ai_advice(self):
    #     """Sends game stats to Gemini to get a strategic tip."""
    #     try:
    #         # Create a data-driven prompt
    #         stats = f"Integrity: {self.integrity}%, Cycles: {self.cycles}, Towers: {len(self.towers)}"
    #         prompt = (
    #             f"Context: The player is in a cyber-defense game. Stats: {stats}. "
    #             "Act as a tactical AI advisor. Give a 1-sentence strategic tip based on these stats."
    #         )
            
    #         response = client.models.generate_content(
    #             model="gemini-2.5-flash-lite",
    #             contents=prompt
    #         )
    #         self.lore_text = f"AI_ADVICE: {response.text}"
    #         # Temporarily switch state to show advice on the lore screen
    #         self.state = "SHOWING_ADVICE"
    #         self.advice_timer = pygame.time.get_ticks()
    #     except Exception as e:
    #         self.lore_text = "AI_OFFLINE: Conserve resources and maintain firewall."

if __name__ == "__main__":
    game = GameApp()
    game.run()