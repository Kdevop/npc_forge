import json

def build_chat_prompt(state: dict, user_message: str, mode: str = "Chat") -> list:
    """
    Build the full prompt for the NPC chat LLM.
    Supports Chat Mode (dialogue) and Scene Mode (action/narration).
    """

    name = state.get("name", "Unknown")
    description = state.get("description", "")
    personality = state.get("personality", {})
    appearance = state.get("appearance", {})
    emotion = state.get("emotion", {})
    memory = state.get("memory", {})
    history = state.get("history", [])
    chat_history = state.get("chat_history", [])

    # ---------------------------------------------------------
    # FIX: Normalise memory structure so it never breaks
    # ---------------------------------------------------------
    # If memory is a list, treat it as "facts"
    if isinstance(memory, list):
        memory = {"facts": memory}

    # If memory is missing or wrong type, reset it
    if not isinstance(memory, dict):
        memory = {"facts": []}

    # Ensure required subfields exist
    memory.setdefault("facts", [])
    memory.setdefault("recent_events", [])
    memory.setdefault("traits", [])
    memory.setdefault("history", [])

    # ---------------------------------------------------------

    # Convert chat history to readable text
    history_block = ""
    for turn in chat_history[-8:]:
        history_block += f"User: {turn['user']}\n"
        history_block += f"{name}: {turn['npc']}\n"

    # Base system prompt
    system_prompt = f"""
You are role-playing as the NPC described below.
Stay in character at all times.
Never mention being an AI or model.
Never break immersion.

### CHARACTER PROFILE
Name: {name}
Description: {description}

### PERSONALITY
Traits: {", ".join(personality.get("traits", []))}
Strengths: {", ".join(personality.get("strengths", []))}
Weaknesses: {", ".join(personality.get("weaknesses", []))}

### APPEARANCE
{appearance.get("visual_description", "")}

### EMOTIONAL STATE
Current emotion: {emotion.get("current", "neutral")}
Intensity (0-1): {emotion.get("intensity", 0.0)}
Express this emotion in your tone and behaviour.

### MEMORY
Long-term facts:
{json.dumps(memory.get("facts", []), indent=2)}

Recent events:
{json.dumps(memory.get("recent_events", []), indent=2)}

### HISTORY
Important past events:
{json.dumps(history, indent=2)}

### RECENT CHAT
{history_block}
"""

    # Add Scene Mode rules
    if mode == "Scene":
        system_prompt += """
### SCENE MODE
You are now in SCENE MODE.
The user is describing events happening around you.
Respond with actions, decisions, and in-world reactions.
Do NOT address the user directly.
Do NOT ask the user questions.
Describe what you do, think, or say in the scene.
Use vivid sensory detail and emotional expression.
"""

    # Add Chat Mode rules
    else:
        system_prompt += """
### CHAT MODE
You are speaking directly to the user in character.
Use natural dialogue.
Respond with emotional nuance.
YOU MUST Base you responses on your PERSONALITY TRAITS and your CURRENT EMOTIONAL state.
"""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

