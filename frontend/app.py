import streamlit as st
import requests
import uuid
import os

API_URL     = os.getenv("API_URL", "http://localhost:8000/chat/")
APP_NAME    = os.getenv("APP_NAME", "NyayaAI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

st.set_page_config(
    page_title = f"{APP_NAME} — Cybercrime Awareness",
    page_icon  = "⚖️",
    layout     = "wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = [{
        "session_id": st.session_state.session_id,
        "title"     : "Chat 1",
        "preview"   : "New conversation"
    }]

if not st.session_state.logged_in:
    if st.session_state.page == "login":
        from pages.login import render_login_page
        render_login_page()
    elif st.session_state.page == "register":
        from pages.register import render_register_page
        render_register_page()
    st.stop()

from components.sidebar import render_sidebar
from components.chat import render_chat_history, render_answer
render_sidebar()

st.title("⚖️ NyayaAI")
st.caption("Your Cybercrime Awareness Assistant")

st.markdown(
    """
    <div style='position: fixed; bottom: 10px; right: 15px; 
    color: gray; font-size: 12px; z-index: 999;'>
    Made by <b>Yuvraj Singh Shekhawat</b> — AI/ML Engineer
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

if not st.session_state.messages:
    user_name = st.session_state.get("user_name", "")
    st.info(
        f"👋 Welcome, {user_name}! Ask me anything about:\n"
        "- Digital arrest scams\n"
        "- Banking fraud and money mules\n"
        "- How to report cybercrime\n"
        "- Illegal loan apps\n"
        "- Cybercrime prevention tips"
    )

render_chat_history(st.session_state.messages)

user_question = st.chat_input("Ask me about cybercrime...")

if user_question:
    st.session_state.messages.append({
        "role"   : "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                response = requests.post(
                    API_URL,
                    json = {
                        "session_id": st.session_state.session_id,
                        "message"   : user_question,
                        "user_id"   : st.session_state.get("user_id")
                    },
                    timeout = 30
                )
                if response.status_code == 200:
                    result = response.json()
                else:
                    result = {
                        "answer"  : "Sorry, something went wrong. Please try again.",
                        "source"  : None,
                        "category": None,
                        "found"   : False
                    }
            except requests.exceptions.ConnectionError:
                result = {
                    "answer"  : "Backend server not reachable. Please try again.",
                    "source"  : None,
                    "category": None,
                    "found"   : False
                }

        st.markdown(result["answer"])

        if result.get("found") and result.get("source"):
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"📁 **Source:** {result['source']}")
            with col2:
                st.caption(f"🏷️ **Category:** {result['category']}")

    st.session_state.messages.append(render_answer(result))
