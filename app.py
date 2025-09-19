import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
# Add this new import for voice input
from streamlit_mic_recorder import speech_to_text

# Suppress ALTS warnings
logging.getLogger('google.auth').setLevel(logging.ERROR)
logging.getLogger('google.api_core').setLevel(logging.ERROR)

# Load environment variables (local .env or Streamlit Cloud secrets)
load_dotenv()

# Set up Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Error: Add your Gemini API key to .env file or Streamlit Cloud secrets!")
    st.stop()
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit page config for beautiful layout
st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme toggle in sidebar
with st.sidebar:
    st.title("🤖 Chat Settings")
    st.markdown("---")
    model_choice = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro"])
    theme = st.selectbox("Theme", ["Light", "Dark"])
    if theme == "Dark":
        st.markdown('<style> .stApp { background-color: #0e1117; color: white; } </style>', unsafe_allow_html=True)
    else:
        st.markdown('<style> .stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); } </style>', unsafe_allow_html=True)
    if st.button("Clear Chat", type="secondary"):
        st.session_state.messages = []
    st.markdown("---")
    st.caption("Powered by Google Gemini")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# Place the voice recorder at the bottom, just before the chat input
voice_input = speech_to_text(language='en', start_prompt="Start voice chat", stop_prompt="Stop voice chat", just_once=True, use_container_width=True)

# Check for both text input and voice input
if prompt := st.chat_input("Type your message here..."):
    # If the user typed, the prompt is already set
    pass
elif voice_input:
    # If the user spoke, set the prompt from the transcribed text
    prompt = voice_input

# Run the chatbot logic if a prompt exists
if prompt:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Generate AI response
    with st.chat_message("assistant", avatar="🤖"):
        try:
            model = genai.GenerativeModel(model_choice)
            chat_history = [{"role": msg["role"], "parts": [{"text": msg["content"]}]} for msg in st.session_state.messages[:-1]]
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(prompt, stream=False)
            ai_reply = response.text
            st.markdown(ai_reply)
            
            # Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        except Exception as e:
            st.error(f"Oops! Error: {e}")

# Footer
st.markdown('<div class="main-footer">© 2025 Kuldeep Patel AI Chatbot App</div>', unsafe_allow_html=True)