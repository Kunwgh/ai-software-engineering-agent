from app.llm.gemini_client import GeminiClient


gemini = GeminiClient()

response = gemini.generate(
    "Explain in one short sentence what an AI software engineering agent does."
)

print(response)