import json
from pathlib import Path

BASE_PATH = Path("data/characters")
BASE_PATH.mkdir(parents=True, exist_ok=True)
INDEX_PATH = Path("data/index.json")

def list_characters() -> list:
    """Return a list of all characters from index.json."""
    index = load_index()
    return index.get("characters", [])

def load_index() -> dict:
    if not INDEX_PATH.exists():
        return {"characters": []}
    with open(INDEX_PATH, "r") as f:
        return json.load(f)

def save_index(index: dict):
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)

def generate_character_id() -> str:
    index = load_index()
    count = len(index["characters"])
    return f"npc_{count + 1:03d}"

def save_new_character(character_data: dict) -> str:
    index = load_index()

    # Assign ID if missing
    if not character_data.get("id"):
        character_data["id"] = generate_character_id()

    character_id = character_data["id"]
    filepath = BASE_PATH / f"{character_id}.json"

    if filepath.exists():
        raise FileExistsError(f"Character '{character_id}' already exists.")

    # Save character JSON
    with open(filepath, "w") as f:
        json.dump(character_data, f, indent=2)

    # Add to index
    index["characters"].append({
        "id": character_id,
        "name": character_data.get("name", ""),
        "description": character_data.get("description", "")
    })
    save_index(index)

    return character_id


def load_state(character_id: str) -> dict:
    filepath = BASE_PATH / f"{character_id}.json"
    if not filepath.exists():
        return {"id": character_id, "memory": [], "emotion": "neutral", "history": []}
    with open(filepath, "r") as f:
        return json.load(f)

def save_state(character_id: str, state: dict):
    filepath = BASE_PATH / f"{character_id}.json"
    with open(filepath, "w") as f:
        json.dump(state, f, indent=2)

def attach_image_to_character(character_id: str, b64_data: str):
    """Load an existing character JSON, attach base64 image data, and save it."""
    state = load_state(character_id)

    # Add or replace the image field
    state["image_b64"] = b64_data

    save_state(character_id, state)
    return state
