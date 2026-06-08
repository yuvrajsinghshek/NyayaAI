# ============================================
# NyayaAI — Main Streamlit App
# Now calls FastAPI backend
# Chat history maintained via session state
# Context passed to RAG for follow up questions
# ============================================

import streamlit as st
import requests
import uuid
from ai.config import APP_NAME, validate_config
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat_history, render_answer

# FastAPI backend URL
API_URL = "http://localhost:8000/chat/"

# page config — must be first Streamlit command
st.set_page_config(
    page_title = f"{APP_NAME} — Cybercrime Awareness",
    page_icon  = "⚖️",
    layout     = "wide"
)

# validate config at startup
validate_config()

# ── Session State ─────────────────────────────────────
# messages — full chat history for display
if "messages" not in st.session_state:
    st.session_state.messages = []

# session_id — unique id for this chat session
# used to fetch history from PostgreSQL
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ── Sidebar ───────────────────────────────────────────
render_sidebar()

# ── Main Header ───────────────────────────────────────
st.title("⚖️ NyayaAI")
st.caption("Your Cybercrime Awareness Assistant")
st.divider()

# ── Welcome Message ───────────────────────────────────
if not st.session_state.messages:
    st.info(
        "👋 Welcome to NyayaAI! Ask me anything about:\n"
        "- Digital arrest scams\n"
        "- Banking fraud and money mules\n"
        "- How to report cybercrime\n"
        "- Illegal loan apps\n"
        "- Cybercrime prevention tips"
    )

# ── Chat History Display ──────────────────────────────
render_chat_history(st.session_state.messages)

# ── Chat Input ────────────────────────────────────────
user_question = st.chat_input("Ask me about cybercrime...")

if user_question:
    # add user message to display
    st.session_state.messages.append({
        "role"   : "user",
        "content": user_question
    })

    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                # call FastAPI backend
                # sends session_id for history tracking
                response = requests.post(
                    API_URL,
                    json = {
                        "session_id": st.session_state.session_id,
                        "message"   : user_question
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
                # backend not running
                result = {
                    "answer"  : "Backend server not running. Please start FastAPI first.",
                    "source"  : None,
                    "category": None,
                    "found"   : False
                }

        # display answer
        st.markdown(result["answer"])

        # show source and category if found
        if result.get("found") and result.get("source"):
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.caption(f"📁 **Source:** {result['source']}")
            with col2:
                st.caption(f"🏷️ **Category:** {result['category']}")

    # save to display history
    st.session_state.messages.append(
        render_answer(result)
    )
