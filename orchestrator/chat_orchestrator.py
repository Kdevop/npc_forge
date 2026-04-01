from storage.local_storage import load_state, save_state
from orchestrator.emotions import update_emotion
from orchestrator.llm import generate_chat_reply
from utilities.chat_helpers import build_chat_prompt

MAX_TURNS = 20

def process_user_message(message: str, character_id: str, mode: str = "Chat") -> str:
    state = load_state(character_id)
    state = update_emotion(state, message)
    prompt = build_chat_prompt(state, message, mode)
    reply = generate_chat_reply(prompt)
    state["chat_history"].append({"user": message, "npc": reply})
    save_state(character_id, state)
    return reply

