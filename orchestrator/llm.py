import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Default model for NPC chat
CHAT_MODEL = "meta-llama/llama-3.1-8b-instruct" 

def generate_chat_reply(messages: list) -> str:
    """
    Sends a chat completion request to OpenRouter and returns the NPC's reply text.
    `messages` must be a list of dicts: [{"role": "...", "content": "..."}]
    """

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0.8,
            top_p=0.9,
        )

        reply = response.choices[0].message.content.strip()
        return reply

    except Exception as e:
        # Fallback message so the app never crashes
        return f"(The NPC hesitates, unable to speak due to an internal error: {e})"
