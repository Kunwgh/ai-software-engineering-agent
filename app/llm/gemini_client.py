import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt,
        )

        return response.output_text