import streamlit as st

from storage.local_storage import list_characters, load_state
from orchestrator.chat_orchestrator import process_user_message
from orchestrator.character_builder import create_character_controller
from utilities.streamlit_helpers import decode_base64_image

# ---------------------------------------------------------
# Session State Setup
# ---------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Chat"

if "current_character_id" not in st.session_state:
    st.session_state.current_character_id = None

if "current_character_image" not in st.session_state:
    st.session_state.current_character_image = None

# ---------------------------------------------------------
# Tab Navigation Logic
# ---------------------------------------------------------
def switch_to_chat(character_id, image_b64):
    st.session_state.current_character_id = character_id
    st.session_state.current_character_image = image_b64
    st.session_state.active_tab = "Chat"


# ---------------------------------------------------------
# UI Tabs
# ---------------------------------------------------------
tab_chat, tab_create = st.tabs(["💬 Chat", "✨ Create Character"])

# ---------------------------------------------------------
# CHARACTER CREATION TAB
# ---------------------------------------------------------
with tab_create:
    st.header("✨ Create a New Character")

    concept = st.text_area("Describe your character concept")

    if st.button("Generate Character"):
        with st.spinner("Creating character..."):
            character_data = create_character_controller(concept)

        character_id = character_data["id"]
        image_b64 = character_data.get("image_b64", None)

        st.success(f"Character '{character_data['name']}' created!")

        # Auto-switch to chat
        switch_to_chat(character_id, image_b64)

        st.rerun()


# ---------------------------------------------------------
# CHAT TAB
# ---------------------------------------------------------
with tab_chat:
    st.header("💬 NPC Chat")

    characters = list_characters()
    if characters:
        options = {c["name"]: c["id"] for c in characters}
        selected_name = st.selectbox(
            "Choose a character",
            list(options.keys()),
            index=0 if st.session_state.current_character_id is None else
            list(options.values()).index(st.session_state.current_character_id)
        )

        st.session_state.current_character_id = options[selected_name]

        # Load image for selected character
        state = load_state(st.session_state.current_character_id)
        st.session_state.current_character_image = state.get("image_b64")

    else:
        st.warning("No characters available. Create one first.")
        st.stop()

    # Display character image
    if st.session_state.current_character_image:
        img = decode_base64_image(st.session_state.current_character_image)
        st.image(img)

    # Chat input
    user_message = st.text_input("Say something to the NPC:")

    if st.button("Send"):
        reply = process_user_message(
            user_message,
            st.session_state.current_character_id
        )
        st.write("NPC:", reply)
