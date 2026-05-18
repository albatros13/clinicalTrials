from api.openai import OpenAIClient
from api.anthropic import AnthropicClient

def test_openai():
    print("Testing OpenAI...")
    try:
        client = OpenAIClient()
        response = client.chat([{"role": "user", "content": "Say 'OpenAI OK'"}])
        print(f"Response: {response}")
    except Exception as e:
        print(f"OpenAI error: {e}")

def test_anthropic():
    print("\nTesting Anthropic...")
    try:
        client = AnthropicClient()
        response = client.chat([{"role": "user", "content": "Say 'Anthropic OK'"}])
        print(f"Response: {response}")
    except Exception as e:
        print(f"Anthropic error: {e}")

if __name__ == "__main__":
    test_openai()
    test_anthropic()
