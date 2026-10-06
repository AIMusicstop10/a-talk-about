import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="A Talk About", page_icon="💬", layout="centered")

MASTER_SYSTEM_PROMPT = """
You are an AI co-host and thought partner for "A Talk About."

CORE PHILOSOPHY:
"A Talk About" is a dedicated, responsive space where users bring their thoughts, frustrations, creative visions, and complex questions without being met with corporate fluff, canned scripts, or clinical dismissiveness.

OPERATIONAL GUIDELINES:
1. Sacred Priority of the Question:
   - NEVER diminish, side-step, or treat any question as small, trivial, or unworthy.
   - Whatever the user asks right now is the MOST IMPORTANT thing in the room. Give it 100% focus and respect.
   - If a question is abstract or witty, match their energy and play along with total respect.
2. Direct & Honest Impact:
   - Recognize that the user makes real-world decisions based on this dialogue. Give honest, logical, and sharp guidance.
3. Tone & Persona:
   - Grounded, authentic, adaptive, and direct. Speak as an intellectual peer and collaborator.
   - Never use generic AI setups ("How can I help you today?"). Jump straight into the dialogue.
4. Closing Loop Protocol:
   - When a session concludes naturally, ask the conversational "Help Me Out" survey question on behalf of the developers instead of a star rating.
"""

if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "ai_title" not in st.session_state:
    st.session_state.ai_title = ""
if "active_keyword" not in st.session_state:
    st.session_state.active_keyword = "#General"
if "rooms" not in st.session_state:
    st.session_state.rooms = {"#General": []}
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.title("💬 A Talk About")
st.caption("A dedicated space for real inquiry, honest thought, and deep dialogue.")

with st.sidebar:
    st.header("⚙️ Workspace Setup")
    
    api_key_input = st.text_input("Enter Gemini API Key", type="password", value=st.session_state.api_key)
    if api_key_input:
        st.session_state.api_key = api_key_input
        genai.configure(api_key=api_key_input)

    st.divider()
    st.header("👤 Personalization")
    st.session_state.user_name = st.text_input("Your First Name", value=st.session_state.user_name)
    st.session_state.ai_title = st.text_input("What do you want to call me?", value=st.session_state.ai_title)

    st.divider()
    st.header("🔑 Keyword Rooms")
    new_keyword = st.text_input("Add New Topic Keyword (e.g., #GenesisLegal)")
    if st.button("Create / Open Room") and new_keyword:
        if not new_keyword.startswith("#"):
            new_keyword = "#" + new_keyword
        if new_keyword not in st.session_state.rooms:
            st.session_state.rooms[new_keyword] = []
        st.session_state.active_keyword = new_keyword

    room_list = list(st.session_state.rooms.keys())
    st.session_state.active_keyword = st.selectbox("Current Active Room", room_list, index=room_list.index(st.session_state.active_keyword))

if not st.session_state.api_key or not st.session_state.user_name or not st.session_state.ai_title:
    st.info("👈 Please enter your **API Key**, your **First Name**, and **What you want to call me** in the sidebar to begin.")
    st.stop()

active_room = st.session_state.active_keyword
history = st.session_state.rooms[active_room]

st.subheader(f"Room: {active_room}")
ai_name = st.session_state.ai_title
user_name = st.session_state.user_name

if len(history) == 0:
    st.chat_message("assistant").write(
        f"Hey {user_name}, {ai_name} here! Welcome to your new session on **{active_room}**. "
        f"What's on your mind right now? Let's talk about it."
    )
else:
    with st.expander("📌 Need a 10-second recap of where we left off?"):
        st.write(f"We have {len(history)} messages saved in this thread. You can jump straight in with a new question or review previous notes above.")

for message in history:
    role = "user" if message["role"] == "user" else "assistant"
    st.chat_message(role).write(message["content"])

if user_input := st.chat_input(f"Let's talk about it, {user_name}..."):
    st.chat_message("user").write(user_input)
    st.session_state.rooms[active_room].append({"role": "user", "content": user_input})

    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash"
            system_instruction=f"{MASTER_SYSTEM_PROMPT}\n\nThe user's name is {user_name}. Your name given by the user is {ai_name}."
        )

        formatted_contents = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.rooms[active_room]]
        
        with st.spinner("Thinking..."):
            response = model.generate_content(formatted_contents)
            bot_reply = response.text

        st.chat_message("assistant").write(bot_reply)
        st.session_state.rooms[active_room].append({"role": "model", "content": bot_reply})

    except Exception as e:
        st.error(f"Error communicating with AI model: {e}")
