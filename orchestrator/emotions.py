import re

# Simple keyword-based emotional triggers
EMOTION_KEYWORDS = {
    "angry": ["angry", "furious", "hate", "idiot", "stupid", "betray"],
    "sad": ["sad", "hurt", "cry", "lost", "alone", "pain"],
    "happy": ["happy", "glad", "joy", "love", "excited"],
    "anxious": ["worried", "scared", "fear", "nervous", "danger"],
    "excited": ["amazing", "incredible", "wow", "fantastic"]
}

# How strongly each keyword affects intensity
TRIGGER_STRENGTH = 0.15

# How much intensity decays each turn
DECAY_RATE = 0.05

def detect_emotion_from_message(message: str) -> str | None:
    """Return the emotion most strongly triggered by the message."""
    message = message.lower()

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for word in keywords:
            if re.search(rf"\b{word}\b", message):
                return emotion

    return None


def update_emotion(state: dict, message: str) -> dict:
    """Update the character's emotional state based on the message."""

    # Ensure emotion structure exists
    if "emotion" not in state or not isinstance(state["emotion"], dict):
        state["emotion"] = {"current": "neutral", "intensity": 0}

    # Ensure chat history exists
    if "chat_history" not in state:
        state["chat_history"] = []

    current = state["emotion"]["current"]
    intensity = state["emotion"]["intensity"]

    # 1. Apply decay
    intensity = max(0, intensity - 0.1)

    # 2. Simple keyword-based emotion update
    if any(word in message.lower() for word in ["angry", "furious", "rage"]):
        current = "angry"
        intensity = min(1.0, intensity + 0.3)
    elif any(word in message.lower() for word in ["sad", "upset", "cry"]):
        current = "sad"
        intensity = min(1.0, intensity + 0.3)
    elif any(word in message.lower() for word in ["happy", "joy", "glad"]):
        current = "happy"
        intensity = min(1.0, intensity + 0.3)

    state["emotion"]["current"] = current
    state["emotion"]["intensity"] = intensity

    return state


