# ============================================
# NyayaAI — Main Streamlit App
# Entry point for the chatbot frontend
# Run with: streamlit run frontend/app.py
# ============================================

import streamlit as st
import sys
from pathlib import Path
# ensure the root directory is in sys.path so we can import 'ai'
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.config import APP_NAME, validate_config
from ai.rag.retriever import retrieve_chunks
from ai.rag.generator import generate_answer
from frontend.components.sidebar import render_sidebar
from frontend.components.chat import render_chat_history, render_answer

# ── Page Config ───────────────────────────────────────
# must be first Streamlit command in the file
st.set_page_config(
    page_title = f"{APP_NAME} — Cybercrime Awareness",
    page_icon  = "⚖️",
    layout     = "wide"
)

# ── Validate Config ───────────────────────────────────
# check all required keys present at startup
validate_config()

# ── Session State ─────────────────────────────────────
# session state persists data across reruns
# messages stores full chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ───────────────────────────────────────────
render_sidebar()

# ── Main Header ───────────────────────────────────────
st.title("⚖️ NyayaAI")
st.caption("Your Cybercrime Awareness Assistant")
st.divider()

# ── Welcome Message ───────────────────────────────────
# shown only when chat is empty
if not st.session_state.messages:
    st.info(
        "👋 Welcome to NyayaAI! Ask me anything about:\n"
        "- Digital arrest scams\n"
        "- Banking fraud and money mules\n"
        "- How to report cybercrime\n"
        "- Illegal loan apps\n"
        "- Cybercrime prevention tips"
    )

# ── Chat History ──────────────────────────────────────
# display all previous messages
render_chat_history(st.session_state.messages)

# ── Chat Input ────────────────────────────────────────
# st.chat_input shows input box at bottom of page
# returns None if user has not typed anything
user_question = st.chat_input(
    "Ask me about cybercrime..."
)

if user_question:
    # add user message to chat history
    st.session_state.messages.append({
        "role"   : "user",
        "content": user_question
    })

    # display user message immediately
    with st.chat_message("user"):
        st.markdown(user_question)

    # show loading spinner while generating answer
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):

            # step 1 — retrieve relevant chunks from ChromaDB
            chunks = retrieve_chunks(user_question)

            # step 2 — generate answer using Groq
            result = generate_answer(user_question, chunks)

        # display answer
        st.markdown(result["answer"])

        # show source and category if answer was found
        if result["found"] and result["source"]:
            st.divider()
            col1, col2 = st.columns(2)

            with col1:
                st.caption(
                    f"📁 **Source:** {result['source']}"
                )
            with col2:
                st.caption(
                    f"🏷️ **Category:** {result['category']}"
                )

    # add assistant message to chat history
    st.session_state.messages.append(
        render_answer(result)
    )
