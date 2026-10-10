import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="A Talk About",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ A Talk About")
st.markdown("A dedicated space for real inquiry, honest thought, and deep verbal dialogue.")

# Initialize session states
if "rooms" not in st.session_state:
    st.session_state.rooms = {"General": []}
if "active_keyword" not in st.session_state:
    st.session_state.active_keyword = "General"

# Sidebar setup
with st.sidebar:
    st.header("⚙️ Workspace Setup")

    # Check Secrets first, fall back to text input
    secret_key = st.secrets.get("GEMINI_API_KEY", "")
    if secret_key:
        api_key = secret_key
        st.success("API Key loaded automatically from Secrets!")
    else:
        api_key = st.text_input("Enter Gemini API Key", type="password")

    st.header("👤 Personalization")
    user_name = st.text_input("Your First Name", value="Ray")
    ai_title = st.text_input("What do you want to call me?", value="Rocky")

    st.header("🔑 Keyword Rooms")
    new_room = st.text_input("Add New Topic Keyword (e.g., #GenesisLegal)")
    if st.button("Create / Open Room") and new_room:
        clean_room = new_room.strip()
        if clean_room not in st.session_state.rooms:
            st.session_state.rooms[clean_room] = []
        st.session_state.active_keyword = clean_room

    room_list = list(st.session_state.rooms.keys())
    selected_room = st.selectbox("Current Active Room", room_list, index=room_list.index(st.session_state.active_keyword))
    st.session_state.active_keyword = selected_room

active_room = st.session_state.active_keyword
st.subheader(f"Room: #{active_room}")

# Configure Gemini API
if api_key:
    genai.configure(api_key=api_key)
    
    # Initialize assistant welcome message if empty
    if not st.session_state.rooms[active_room]:
        st.session_state.rooms[active_room].append({
            "role": "assistant",
            "content": f"Hey {user_name}, {ai_title} here! Welcome to your session on **#{active_room}**. Tap the microphone below to speak or type a message. Let's talk about it."
        })

    # Display chat messages for active room
    for msg in st.session_state.rooms[active_room]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Updated active model supporting audio & text
    model_name = "gemini-3.8-flash"

    st.markdown("---")
    st.markdown(f"### 💬 Talk with {ai_title}")

    # --- VOICE INPUT WIDGET ---
    audio_value = st.audio_input(f"Tap to record your voice message to {ai_title}")

    if audio_value:
        st.audio(audio_value)
        with st.spinner(f"{ai_title} is listening..."):
            try:
                audio_bytes = audio_value.read()
                model = genai.GenerativeModel(model_name)
                
                response = model.generate_content([
                    f"You are {ai_title}, a grounded, engaging personal AI talking to {user_name}. Respond naturally to this voice input:",
                    {"mime_type": "audio/wav", "data": audio_bytes}
                ])
                
                ai_text = response.text
                st.session_state.rooms[active_room].append({"role": "user", "content": "🎙️ *(Spoken Voice Message)*"})
                st.session_state.rooms[active_room].append({"role": "assistant", "content": ai_text})
                st.rerun()
            except Exception as e:
                st.error(f"Error processing audio: {e}")

    # --- TEXT INPUT FALLBACK ---
    if text_input := st.chat_input(f"Let's talk about it, {user_name}..."):
        st.session_state.rooms[active_room].append({"role": "user", "content": text_input})
        with st.spinner(f"{ai_title} is thinking..."):
            try:
                model = genai.GenerativeModel(model_name)
                history = [
                    {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                    for m in st.session_state.rooms[active_room][:-1]
                ]
                chat = model.start_chat(history=history)
                res = chat.send_message(text_input)
                st.session_state.rooms[active_room].append({"role": "assistant", "content": res.text})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Please enter your Gemini API key in the sidebar or save it in Streamlit Secrets to begin.")
