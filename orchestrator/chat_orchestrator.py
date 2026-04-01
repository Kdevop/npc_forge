from storage.local_storage import load_state, save_state
from orchestrator.emotions import update_emotion
from orchestrator.strategy import choose_strategy
from orchestrator.llm import generate_reply

def process_user_message(message: str, character_id: str) -> str:
    state = load_state(character_id)

    state = update_emotion(state, message)
    strategy = choose_strategy(state, message)
    reply = generate_reply(strategy, state, message)

    state["history"].append({"user": message, "npc": reply})
    save_state(character_id, state)

    return reply
