import streamlit as st
from datetime import datetime
import re
import requests
from dotenv import load_dotenv
import os

# API call function (unchanged)
def call_groq_api(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    load_dotenv("MyProject")
 

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return " API key not found."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": message}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        return reply.strip()
    except Exception as e:
        return f" Error: {str(e)}"


# Page setup
st.set_page_config(page_title="TalkTonic", layout="centered")

# Sidebar Navigation and Theme selector
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select the Option", ["Chat", "About"])

st.sidebar.subheader("Theme")
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
st.session_state.theme = st.sidebar.selectbox(
    "Choose Theme", ["Dark", "Light", "Midnight"], index=["Dark", "Light", "Midnight"].index(st.session_state.theme)
)

def get_theme_colors(theme):
    if theme == "Light":
        return {
            "chat_bg": "#f0f0f0",
            "user_bg": "#4caf50",
            "user_color": "white",
            "bot_bg": "#d3d3d3",
            "bot_color": "black",
            "clear_btn_bg": "#f44336",
            "clear_btn_color": "white"
        }
    elif theme == "Midnight":
        return {
            "chat_bg": "#0b0c10",
            "user_bg": "#66fcf1",
            "user_color": "#0b0c10",
            "bot_bg": "#1f2833",
            "bot_color": "#c5c6c7",
            "clear_btn_bg": "#45a29e",
            "clear_btn_color": "#0b0c10"
        }
    else:  # Dark
        return {
            "chat_bg": "#1f1f1f",
            "user_bg": "#4caf50",
            "user_color": "white",
            "bot_bg": "#333",
            "bot_color": "#f1f1f1",
            "clear_btn_bg": "#f44336",
            "clear_btn_color": "white"
        }

def strip_html_tags(text):
    return re.sub(r'<[^>]*>', '', text)

if page == "Chat":
    colors = get_theme_colors(st.session_state.theme)

    # Custom CSS for chat UI
    st.markdown(f"""
    <style>
    .chat-container {{
        height: 400px;
        overflow-y: auto;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 10px;
        background-color: {colors['chat_bg']};
        color: {colors['bot_color']};
        position: relative;
        overflow: auto;
    }}
    .user-message {{
        background-color: {colors['user_bg']};
        color: {colors['user_color']};
        padding: 8px 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        max-width: 70%;
        float: right;
        clear: both;
        word-wrap: break-word;
        font-size: 15px;
    }}
    .bot-message {{
        background-color: {colors['bot_bg']};
        color: {colors['bot_color']};
        padding: 8px 12px;
        border-radius: 10px;
        margin-bottom: 8px;
        max-width: 70%;
        float: left;
        clear: both;
        word-wrap: break-word;
        font-size: 15px;
    }}
    small {{
        display: block;
        font-size: 11px;
        opacity: 0.7;
        margin-top: 3px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Header
    with st.container():
        col1, col2, col3 = st.columns([1,5,4])
        with col1:
            st.markdown("<div style='margin-top: 10px; font-size: 40px;'>🤖</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h1 style='margin-bottom: 0;'>TalkTonic</h1>", unsafe_allow_html=True)
        with col3:
            current_time = datetime.now().strftime("%b %d, %Y - %I:%M %p")
            st.markdown(f"""
                <div style='text-align: right; font-size:13px; margin-top: 10px;'>
                    Theme: <b>{st.session_state.theme}</b><br>
                    <span style='color: #33ff77;'>🟢</span> Bot Status: <b>Online</b><br>
                    {current_time}
                </div>
            """, unsafe_allow_html=True)

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "pending_input" not in st.session_state:
        st.session_state.pending_input = ""

    # Clear chat and download buttons
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_input = ""
    with col2:
        if st.session_state.messages:
            clean_chat = "\n".join(
                f"{sender.upper()}: {strip_html_tags(message)}"
                for sender, message in st.session_state.messages
            )
            st.download_button(
                "💾 Download Chat", clean_chat, file_name="talktonic_chat.txt", use_container_width=True
            )

    # User input
    user_input = st.chat_input("Type your message...")
    if user_input:
        st.session_state.pending_input = user_input.strip()

    # Process input and generate bot reply
    if st.session_state.pending_input:
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append(("user", f"{st.session_state.pending_input}<small>{timestamp}</small>"))
        bot_reply = call_groq_api(st.session_state.pending_input)
        st.session_state.messages.append(("bot", f"{bot_reply}<small>{timestamp}</small>"))
        st.session_state.pending_input = ""

    # Display chat messages
    chat_html = f"""
    <div id="chatbox" class="chat-container">
    """
    for sender, msg in st.session_state.messages:
        if sender == "user":
            chat_html += f'<div class="user-message">{msg}</div>'
        else:
            chat_html += f'<div class="bot-message">{msg}</div>'
    chat_html += "</div>"

    st.markdown(chat_html, unsafe_allow_html=True)

    # Scroll chat to bottom with JS
    st.markdown("""
    <script>
    var chatbox = document.getElementById("chatbox");
    if(chatbox){
        chatbox.scrollTop = chatbox.scrollHeight;
    }
    </script>
    """, unsafe_allow_html=True)

elif page == "About":
    st.subheader("About TalkTonic")
    st.markdown("""
    *TalkTonic* is a modern chatbot UI built with Streamlit.  
    It supports multiple themes, chat history, and smart auto-scroll.

    - Built for students, devs, and creators  
    - Easily integrates with GPT models or custom AI logic  
    - Fully customizable with themes, avatars, and more  
    """)
