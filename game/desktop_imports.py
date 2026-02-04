# This file is NEVER seen by the Pygbag web scanner
try:
    from dotenv import load_dotenv
    import google.generativeai as genai
    import os
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    client = genai
except ImportError:
    genai = None
    client = None