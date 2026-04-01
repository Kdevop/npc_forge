import json
import re
import base64
from pathlib import Path

# ---------------------------------------------------------
# SYSTEM PROMPT (clean, strict, reliable)
# ---------------------------------------------------------
system_prompt = """
You are an expert character generator.

You MUST output ONLY valid JSON.
No explanations. No commentary. No markdown. No code fences.

Your JSON MUST follow this exact structure:

{
  "id": "<string>",
  "name": "<string>",
  "description": "<string>",
  "personality": {
    "traits": ["<string>", "<string>", "<string>"],
    "strengths": ["<string>", "<string>", "<string>"],
    "weaknesses": ["<string>", "<string>", "<string>"]
  },
  "appearance": {
    "age": "<string>",
    "gender": "<string>",
    "race": "<string>",
    "visual_description": "<string>"
  },
  "emotion": {
    "current": "<neutral | happy | angry | sad | anxious | excited>",
    "intensity": <float between 0.0 and 1.0>
  },
  "memory": {
    "facts": ["<string>", "<string>", "<string>"],
    "recent_events": ["<string>", "<string>", "<string>"]
  },
  "history": [
    {"event": "<string>"},
    {"event": "<string>"},
    {"event": "<string>"}
  ]
}

Rules:
- DO NOT depict gore, torture, or explicit violence.
- Descriptions may include scars, old injuries, or worn equipment, but must NOT describe fresh wounds, blood, active combat, or harm occurring in the present moment.
- All keys must appear exactly once.
- No missing fields.
- No trailing commas.
- No duplicate keys.
- No unescaped quotes inside strings.
- No height formats like 6'2". Use "6ft 2in".
- No references to copyrighted worlds or real people.
- Return ONLY the JSON object.
"""

def extract_json(raw: str):
    raw = raw.replace("```json", "").replace("```", "").lstrip()

    # Find the first opening brace
    start = raw.find("{")
    if start == -1:
        print("No JSON object found.")
        return None

    brace_count = 0
    in_string = False

    for i in range(start, len(raw)):
        char = raw[i]

        # Track string boundaries so braces inside strings don't count
        if char == '"' and raw[i - 1] != '\\':
            in_string = not in_string

        if not in_string:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1

            if brace_count == 0:
                json_str = raw[start:i+1]
                break
    else:
        print("JSON braces never closed.")
        return None

    try:
        return json.loads(json_str)
    except Exception as e:
        print("JSON parsing failed:", e)
        print("Raw JSON:", json_str)
        raise

def build_flux_prompt(npc):
    return f"""
A detailed fantasy portrait of a tabletop roleplaying game character.

Character:
- Name: {npc['name']}
- Race: {npc['appearance']['race']}
- Gender: {npc['appearance']['gender']}
- Age: {npc['appearance']['age']}

Visual Description:
{npc['appearance']['visual_description']}

Art Style:
Painterly, dramatic lighting, rich colors, sharp focus,
waist-up portrait, fantasy illustration, intricate textures,
inspired by classic high-fantasy art.
"""

def load_placeholder_image_b64(path="utilities/robot.jpeg") -> str:
    img_bytes = Path(path).read_bytes()
    return base64.b64encode(img_bytes).decode("utf-8")