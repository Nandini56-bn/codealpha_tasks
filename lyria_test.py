from google import genai
import os

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY is not set.")
    print("We need to configure the API key first.")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

print("Google GenAI client created successfully.")
print("Now checking available models...")

for model in client.models.list():
    name = getattr(model, "name", "")
    if "lyria" in name.lower():
        print("LYRIA MODEL FOUND:", name)