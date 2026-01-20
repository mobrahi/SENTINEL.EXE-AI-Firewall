import os
from dotenv import load_dotenv
from google import genai

# Load variables from .env
load_dotenv()

# Use the Client object. 
# It automatically looks for 'GOOGLE_API_KEY' if api_key is not passed.
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# Use 'models.generate_content' with the latest production model
response = client.models.generate_content(
    model="gemini-2.5-flash-lite", 
    contents="Give me a cool name for a Tower Defense enemy."
)

print(f"AI Response: {response.text}")
