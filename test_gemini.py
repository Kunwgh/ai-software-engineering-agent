from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.interactions.create(
    model="gemini-3.6-flash",
    input="Say hello in one short sentence."
)

print(response.output_text)