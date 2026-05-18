import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class AnthropicClient:
    def __init__(self, model="claude-sonnet-4-6"):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def chat(self, messages, max_tokens=1024, **kwargs):
        # Anthropic messages format is slightly different but often compatible
        # for simple cases. System message should be handled separately in Anthropic.
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_msg,
            messages=user_messages,
            **kwargs
        )
        return response.content[0].text

if __name__ == "__main__":
    client = AnthropicClient()
    print(client.chat([{"role": "user", "content": "Hello, how are you?"}]))
