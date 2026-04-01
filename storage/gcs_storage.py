import json
import base64
from google.cloud import storage
import os

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

client = storage.Client()
bucket = client.bucket(BUCKET_NAME)


# -----------------------------
# Save character JSON
# -----------------------------
def save_character(character_id, data):
    blob = bucket.blob(f"characters/{character_id}.json")
    blob.upload_from_string(json.dumps(data), content_type="application/json")


# -----------------------------
# Load character JSON
# -----------------------------
def load_state(character_id):
    blob = bucket.blob(f"characters/{character_id}.json")
    if not blob.exists():
        return {}
    content = blob.download_as_text()
    return json.loads(content)

# -----------------------------
# List characters
# -----------------------------
def list_characters():
    blobs = bucket.list_blobs(prefix="characters/")
    characters = []

    for blob in blobs:
        if blob.name.endswith(".json"):
            data = json.loads(blob.download_as_text())
            characters.append(data)

    return characters


# -----------------------------
# Save image (base64)
# -----------------------------
def save_image(character_id, image_b64):
    blob = bucket.blob(f"images/{character_id}.txt")
    blob.upload_from_string(image_b64, content_type="text/plain")


# -----------------------------
# Load image (base64)
# -----------------------------
def load_image(character_id):
    blob = bucket.blob(f"images/{character_id}.txt")
    if not blob.exists():
        return None
    return blob.download_as_text()

# -----------------------------
# Create a new character
# -----------------------------
def save_new_character(character_data):
    character_id = character_data["id"]
    save_character(character_id, character_data)
    return character_id


# -----------------------------
# Attach an image to a character
# -----------------------------
def attach_image_to_character(character_id, image_b64):
    save_image(character_id, image_b64)
