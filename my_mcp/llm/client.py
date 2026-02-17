from groq import Groq

class LLMClient:
    def __init__(self):
        self.client = Groq()

    def chat(self, messages, tools=None):
        return self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
        )
