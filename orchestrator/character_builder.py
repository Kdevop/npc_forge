from openai import OpenAI
import google.genai as genai

import os
import json
import requests
import re
import json

from utilities.character_gen_helpers import system_prompt, extract_json, build_flux_prompt, load_placeholder_image_b64
from storage.local_storage  import save_new_character, attach_image_to_character

from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    base_url='https://openrouter.ai/api/v1',
    api_key=OPENROUTER_API_KEY,
)

def generate_character(concept: str = "") -> dict:
    """
    Generates a new NPC character using the LLM and saves it to local storage.
    Returns the final character JSON (including assigned ID).
    """

    # Call the LLM
    model_resp = client.chat.completions.create(
        model="mistralai/ministral-8b-2512",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": concept}
        ]
    )

    raw_response = model_resp.choices[0].message.content
    print("Raw LLM Response Char Gen: ", raw_response)
    # Extract JSON from the LLM output
    character_data = extract_json(raw_response)

    # Save the character (assigns ID if missing)
    character_id = save_new_character(character_data)

    # Ensure the returned JSON includes the final ID
    character_data["id"] = character_id

    return character_data

def generate_image_openrouter(prompt: str):
    print("This is the prompt for image generation:", prompt)

    if not prompt or not prompt.strip():
        raise ValueError("Image prompt is empty")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemini-2.5-flash-image",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload).json()
    print("This is the data for image:", response)

    try:
        message = response["choices"][0]["message"]

        if "images" in message and message["images"]:
            image_url = message["images"][0]["image_url"]["url"]
            return image_url

        print("Image extraction failed:", response)
        raise ValueError("No image returned")

    except Exception:
        print("Image extraction failed:", response)
        raise ValueError("No image returned")

def create_character_controller(prompt: str):
    # 1. Generate NPC JSON
    character_data = generate_character(prompt)

    # 2. Build image prompt
    image_prompt = build_flux_prompt(character_data)

    # Toggle placeholder vs real image
    USE_PLACEHOLDER = False

    if USE_PLACEHOLDER:
        b64_image = load_placeholder_image_b64()
    else:
        print(image_prompt)
        b64_image = generate_image_openrouter(image_prompt)

    attach_image_to_character(character_data["id"], b64_image)
    return character_data