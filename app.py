import streamlit as st
from PIL import Image

from orchestrator.chat_orchestrator import process_user_message
from orchestrator.character_builder import create_character_controller
from utilities.streamlit_helpers import decode_base64_image

# For deployment (GCS)
from storage.gcs_storage import list_characters, load_state, load_image


# Title banner
title_banner = Image.open("assets/title_banner.png")

st.markdown("""
    <style>
        .title-banner-wrapper {
            width: 100%;
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        .title-banner-img {
            width: 35%;          /* Adjust this number to change size */
            max-width: 420px;    /* Hard cap for large screens */
            min-width: 250px;    /* Prevent it from shrinking too much */
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title-banner-wrapper">', unsafe_allow_html=True)
st.image(title_banner, output_format="PNG", use_container_width=False, caption=None)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SESSION STATE SETUP
# ---------------------------------------------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Create"

if "current_character_id" not in st.session_state:
    st.session_state.current_character_id = None

if "current_character_image" not in st.session_state:
    st.session_state.current_character_image = None

if "chat_buffer" not in st.session_state:
    st.session_state.chat_buffer = []


# ---------------------------------------------------------
# TAB SWITCHING
# ---------------------------------------------------------
def switch_to_chat(character_id, image_b64):
    st.session_state.current_character_id = character_id
    st.session_state.current_character_image = image_b64
    st.session_state.chat_buffer = []
    st.session_state.active_tab = "Chat"
    st.rerun()


# ---------------------------------------------------------
# CUSTOM TAB BUTTONS
# ---------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("✨ Create Character", type="primary" if st.session_state.active_tab == "Create" else "secondary"):
        st.session_state.active_tab = "Create"
        st.rerun()

with col2:
    if st.button("💬 Chat", type="primary" if st.session_state.active_tab == "Chat" else "secondary"):
        st.session_state.active_tab = "Chat"
        st.rerun()


# ---------------------------------------------------------
# GLOBAL DARK-FANTASY CSS
# ---------------------------------------------------------
st.markdown("""
    <style>

    /* Global container width */
    .block-container {
        max-width: 95% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Reduce column gap */
    .block-container .stColumns {
        gap: 0.75rem !important;
    }

    /* Portrait styling */
    .portrait-img img {
        width: 100% !important;
        height: auto !important;
        border-radius: 10px;
        border: 2px solid #3a2f1f;
        box-shadow: 0 0 12px rgba(0,0,0,0.6);
    }

    /* Chat window */
    .chat-window {
        height: 500px;
        overflow-y: auto;
        padding: 14px;
        border: 2px solid #3a2f1f;
        border-radius: 12px;
        background-color: #1a1a1a;
        box-shadow: inset 0 0 12px rgba(0,0,0,0.7);
    }

    /* User message bubble */
    .user-msg {
        border: 2px solid #e6c76b;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #f5e9c8;
        background-color: rgba(230, 199, 107, 0.08);
    }

    /* NPC message bubble */
    .npc-msg {
        border: 2px solid #b85a5a;
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #f0dada;
        background-color: rgba(184, 90, 90, 0.08);
    }

    /* Tab buttons */
    button[kind="primary"] {
        background-color: #e6c76b !important;
        color: #0e0e0e !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }

    button[kind="secondary"] {
        background-color: #3a2f1f !important;
        color: #f5e9c8 !important;
        border-radius: 6px !important;
        border: 1px solid #e6c76b !important;
    }

    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CREATE CHARACTER TAB
# ---------------------------------------------------------
if st.session_state.active_tab == "Create":
    st.header("✨ Create a New Character")

    concept = st.text_area("Describe your character concept")

    if st.button("Generate Character"):
        with st.spinner("Creating character..."):
            character_data = create_character_controller(concept)

        character_id = character_data["id"]
        image_b64 = character_data.get("image_b64", None)

        st.success(f"Character '{character_data['name']}' created!")

        switch_to_chat(character_id, image_b64)


# ---------------------------------------------------------
# CHAT TAB
# ---------------------------------------------------------
if st.session_state.active_tab == "Chat":
    st.header("💬 NPC Chat")

    # Load characters
    characters = list_characters()
    if not characters:
        st.warning("No characters available. Create one first.")
        st.stop()

    # Character selector
    options = {c["name"]: c["id"] for c in characters}
    selected_name = st.selectbox(
        "Choose a character",
        list(options.keys()),
        index=list(options.values()).index(st.session_state.current_character_id)
        if st.session_state.current_character_id in options.values()
        else 0
    )

    st.session_state.current_character_id = options[selected_name]

    # Load character state + image
    state = load_state(st.session_state.current_character_id)
    image_b64 = load_image(st.session_state.current_character_id)
    st.session_state.current_character_image = image_b64

    # Toggles
    show_emotion = st.checkbox("Show emotional state", value=False)
    mode = st.radio("Mode", ["Chat", "Scene"], horizontal=True)

    if show_emotion:
        emotion = state.get("emotion", {})
        st.info(f"**Emotion:** {emotion.get('current', 'neutral')} (intensity {emotion.get('intensity', 0)})")

    # Layout: portrait left, chat right
    left, right = st.columns([1.3, 2.1])

    # -------------------------
    # LEFT COLUMN (PORTRAIT)
    # -------------------------
    with left:
        if st.session_state.current_character_image:
            img = decode_base64_image(st.session_state.current_character_image)
            st.markdown('<div class="portrait-img">', unsafe_allow_html=True)
            st.image(img, caption=selected_name)
            st.markdown('</div>', unsafe_allow_html=True)

    # -------------------------
    # RIGHT COLUMN (CHAT)
    # -------------------------
    with right:

        # Chat window container
        chat_html = '<div class="chat-window">'

        # Render chat history manually
        for turn in st.session_state.chat_buffer:
            chat_html += f'<div class="user-msg"><b>You:</b> {turn["user"]}</div>'
            if turn["npc"]:
                chat_html += f'<div class="npc-msg"><b>{selected_name}:</b> {turn["npc"]}</div>'

        chat_html += '</div>'

        st.markdown(chat_html, unsafe_allow_html=True)

        # Auto-scroll to bottom
        st.markdown("""
            <script>
            var chatWindow = window.parent.document.querySelector('.chat-window');
            if (chatWindow) {
                chatWindow.scrollTop = chatWindow.scrollHeight;
            }
            </script>
        """, unsafe_allow_html=True)

        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_message = st.text_input("Say something to the NPC:")
            submitted = st.form_submit_button("Send")

        if submitted and user_message:
            st.session_state.chat_buffer.append({"user": user_message, "npc": None})
            st.rerun()

        # Generate NPC reply
        if st.session_state.chat_buffer and st.session_state.chat_buffer[-1]["npc"] is None:
            last_user_msg = st.session_state.chat_buffer[-1]["user"]

            npc_reply = process_user_message(
                last_user_msg,
                st.session_state.current_character_id,
                mode=mode
            )

            st.session_state.chat_buffer[-1]["npc"] = npc_reply
            st.rerun()
