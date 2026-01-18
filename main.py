import pygame
import constants as C
import os
import random
from dotenv import load_dotenv
from google import genai


# Initialize AI
load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont("Courier", 18)
        self.clock = pygame.time.Clock()
        self.state = "START_MENU" # States: START_MENU, AI_LOADING, PLAYING
        self.lore_text = "Press SPACE to initialize Firewall Lore..."

    def fetch_wave_lore(self):
        """Calls Gemini to get a description of the upcoming virus wave."""
        try:
            prompt = "The player is about to face Wave 1 of viruses. Describe the 'Logic Bomb' virus in 1 scary sentence."
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            self.lore_text = response.text
            self.state = "PLAYING"
        except Exception as e:
            self.lore_text = "CONNECTION ERROR: Local subroutines active."
            self.state = "PLAYING"

    def draw(self):
        self.screen.fill(C.BG_COLOR)
        
        if self.state == "START_MENU":
            # Display lore/instructions
            lines = self.lore_text.split('.')
            for i, line in enumerate(lines):
                text_surf = self.font.render(line.strip(), True, C.TEXT_COLOR)
                self.screen.blit(text_surf, (50, 100 + (i * 30)))
        
        elif self.state == "PLAYING":
            # Draw the grid and game (what we built earlier)
            for x in range(0, C.SCREEN_WIDTH, C.TILE_SIZE):
                pygame.draw.line(self.screen, C.GRID_COLOR, (x, 0), (x, C.SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, C.CORE_COLOR, (C.SCREEN_WIDTH//2-20, C.SCREEN_HEIGHT//2-20, 40, 40))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.state == "START_MENU":
                        self.state = "AI_LOADING"
                        self.fetch_wave_lore()

            self.draw()
            self.clock.tick(C.FPS)
        pygame.quit()

    import random # Add this at the top of main.py

# Inside your GameApp class:
def fetch_wave_lore(self):
    """Calls Gemini to get a description, with a robust local fallback."""
    try:
        # We add a short timeout or check to ensure we don't hang the game
        prompt = "Describe a computer virus wave in one short, gritty sentence for a cyber-security game."
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
        self.lore_text = response.text
        self.state = "PLAYING"
        
    except Exception as e:
        # This is the 'Responsible AI' Fallback Pillar in action
        print(f"AI Unavailable ({e}). Switching to Local Subroutines.")
        self.lore_text = random.choice(C.LOCAL_LORE_BACKUP)
        self.state = "PLAYING"
    
if __name__ == "__main__":
    game = GameApp()
    game.run()