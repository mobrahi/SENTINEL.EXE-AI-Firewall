from google import genai
client = genai.Client(vertexai=True, project="your-project-id", location="asia-southeast1")

# List all available foundation models
for model in client.models.list():
    print(f"Model ID: {model.name}, Supported Actions: {model.supported_actions}")
