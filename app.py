import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(page_title="A Talk About", page_icon="💬", layout="wide")

# Master System Prompt
MASTER_SYSTEM_PROMPT = """You are Rocky, a helpful, grounded, and engaging AI companion. You speak directly, warmly, and authentically."""

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
    st.session_state.active_keyword = st.selectbox(
        "Current Active Room", 
        room_list, 
        index=room_list.index(st.session_state.active_keyword) if st.session_state.active_keyword in room_list else 0
    )

# Validate required inputs
if not api_key or not user_name or not ai_title:
    st.info("🔑 Please ensure your **API Key**, **First Name**, and **AI Title** are provided in the sidebar.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)

# Main Chat Interface
active_room = st.session_state.active_keyword
history = st.session_state.rooms[active_room]

st.title("💬 A Talk About")
st.caption("A dedicated space for real inquiry, honest thought, and deep dialogue.")
st.subheader(f"Room: #{active_room}")

# Welcome message for empty room
if len(history) == 0:
    st.chat_message("assistant").write(
        f"Hey {user_name}, {ai_title} here! Welcome to your new session on **#{active_room}**. What's on your mind right now? Let's talk about it."
    )
else:
    with st.expander("💬 Need a 10-second recap of where we left off?"):
        st.write(f"We have {len(history)} messages saved in this thread.")

# Display existing chat history
for message in history:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).write(message["content"])

# Chat input and response handling
if user_input := st.chat_input(f"Let's talk about it, {user_name}..."):
    st.chat_message("user").write(user_input)
    st.session_state.rooms[active_room].append({"role": "user", "content": user_input})

    try:
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=f"{MASTER_SYSTEM_PROMPT}\n\nThe user's name is {user_name}. You are {ai_title}."
        )

        formatted_contents = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.rooms[active_room]]

        with st.spinner("Thinking..."):
            response = model.generate_content(formatted_contents)
            bot_reply = response.text

        st.chat_message("assistant").write(bot_reply)
        st.session_state.rooms[active_room].append({"role": "model", "content": bot_reply})

    except Exception as e:
        st.error(f"Error communicating with AI model: {e}")
