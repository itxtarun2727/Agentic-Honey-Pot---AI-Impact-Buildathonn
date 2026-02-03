import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🔍 SEARCHING FOR AVAILABLE MODELS...")

try:
    # Ask Google what models you can use
    for m in genai.list_models():
        # We only want models that can write text (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
            
except Exception as e:
    print(f"❌ Error: {e}")