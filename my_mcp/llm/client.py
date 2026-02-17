import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # loads .env

class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        self.client = Groq(api_key=api_key)

    def chat(self, messages, tools=None):
        return self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
        )
