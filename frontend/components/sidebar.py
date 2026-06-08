# ============================================
# NyayaAI — Sidebar Component
# Shows app info and multiple chat sessions
# User can create new chats and switch between them
# Each chat has its own history in PostgreSQL
# ============================================

import streamlit as st
import uuid
from ai.config import APP_NAME, APP_VERSION, CATEGORIES


def render_sidebar():
    with st.sidebar:
        # app name and version
        st.title(f"⚖️ {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")
        st.divider()

        # ── New Chat Button ───────────────────────────
        if st.button("➕ New Chat", use_container_width=True):
            # generate new session id for new chat
            st.session_state.session_id = str(uuid.uuid4())
            # clear display messages
            st.session_state.messages   = []
            # add new chat to history list
            if "chat_sessions" not in st.session_state:
                st.session_state.chat_sessions = []
            st.session_state.chat_sessions.append({
                "session_id": st.session_state.session_id,
                "title"     : f"Chat {len(st.session_state.chat_sessions) + 1}"
            })
            st.rerun()

        st.divider()

        # ── Chat Sessions List ────────────────────────
        st.subheader("💬 Your Chats")

        # initialize chat sessions if not exists
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = [{
                "session_id": st.session_state.session_id,
                "title"     : "Chat 1"
            }]

        # display all chat sessions
        for chat in st.session_state.chat_sessions:
            # highlight current active chat
            is_active = (
                chat["session_id"] == st.session_state.session_id
            )
            label = f"{'🟢' if is_active else '⚪'} {chat['title']}"

            if st.button(label,
                         key=chat["session_id"],
                         use_container_width=True):
                # switch to selected chat
                st.session_state.session_id = chat["session_id"]
                # clear messages — will reload from API
                st.session_state.messages   = []
                st.rerun()

        st.divider()

        # ── Emergency Contacts ────────────────────────
        st.subheader("🆘 Emergency Contacts")
        st.error("📞 Cybercrime Helpline: **1930**")
        st.markdown(
            "🌐 [cybercrime.gov.in]"
            "(https://www.cybercrime.gov.in)"
        )
        st.markdown("📱 Follow **@cyberdost** on social media")
        st.divider()

        # ── Topics Covered ────────────────────────────
        st.subheader("🏷️ Topics Covered")
        for category in CATEGORIES:
            st.markdown(f"• {category}")
        st.divider()

        # ── Clear Current Chat ────────────────────────
        if st.button("🗑️ Clear Current Chat",
                     use_container_width=True):
            st.session_state.messages = []
            st.rerun()
