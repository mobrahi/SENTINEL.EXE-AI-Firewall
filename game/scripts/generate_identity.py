import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Setup
load_dotenv()

# The new SDK looks for GEMINI_API_KEY by default
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Define your Safety Configuration
# You can choose: BLOCK_NONE, BLOCK_ONLY_HIGH, BLOCK_MEDIUM_AND_ABOVE, or BLOCK_LOW_AND_ABOVE
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, # Strict
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, # Strict
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH, # Allow mild sci-fi danger
    ),
]

# Use the client to generate content
def generate_boss_description():
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Describe a level 10 'Logic Bomb' boss for a tower defense game.",
            config=types.GenerateContentConfig(
                safety_settings=safety_settings
            )
        )
        print(response.text)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    generate_boss_description()

def brainstorm_game():
    try:
        # We'll use the newest recommended model for 2026
        # 'gemini-3-flash-preview' is the current portfolio powerhouse
        model_id = "gemini-3-flash-preview"
        
        prompt = (
            "Give me a creative name and a 1-sentence backstory for a Tower Defense game. "
            "Theme: Cyber-security / Computer Viruses. "
            "Format as NAME: [Title] and STORY: [Backstory]"
        )

        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        print("\n--- AI PROJECT BRAINSTORM ---")
        print(response.text)
        print("-----------------------------\n")

    except Exception as e:
        # If Gemini 3 isn't active for you yet, fallback to 2.5
        print(f"Gemini 3 not ready, trying 2.5... (Error: {e})")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print(response.text)

if __name__ == "__main__":
    brainstorm_game()
