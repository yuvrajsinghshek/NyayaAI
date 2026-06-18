import streamlit as st
import requests
import uuid
import os
APP_NAME    = os.getenv("APP_NAME", "NyayaAI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
CATEGORIES  = [
    "Digital Arrest",
    "Banking Fraud",
    "Illegal Loan Apps",
    "OTP Fraud",
    "Cybercrime Reporting",
    "Social Media Fraud",
    "Identity Theft",
    "General Cybercrime"
]

import os
API_URL = os.getenv("API_URL", "http://localhost:8000/chat")


def save_current_chat_summary():
    # saves summary of current chat before switching
    if (st.session_state.get("session_id") and
        st.session_state.get("user_id") and
        st.session_state.get("messages")):
        try:
            requests.post(
                f"{API_URL}/summary/{st.session_state.session_id}",
                params  = {"user_id": st.session_state.user_id},
                timeout = 10
            )
        except Exception:
            pass


def render_sidebar():
    with st.sidebar:
        # app name and version
        st.title(f"⚖️ {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")

        # user greeting
        if st.session_state.get("user_name"):
            st.success(f"👤 {st.session_state.user_name}")

        st.divider()

        # ── New Chat Button ───────────────────────────
        if st.button("➕ New Chat", use_container_width=True):
            # save summary of current chat first
            save_current_chat_summary()

            # create new session
            new_session_id = str(uuid.uuid4())
            new_title      = f"Chat {len(st.session_state.chat_sessions) + 1}"

            st.session_state.chat_sessions.append({
                "session_id": new_session_id,
                "title"     : new_title,
                "preview"   : "New conversation"
            })

            st.session_state.session_id = new_session_id
            st.session_state.messages   = []
            st.rerun()

        st.divider()

        # ── Chat Sessions ─────────────────────────────
        st.subheader("💬 Chats")

        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = [{
                "session_id": st.session_state.session_id,
                "title"     : "Chat 1",
                "preview"   : "New conversation"
            }]

        for i, chat in enumerate(st.session_state.chat_sessions):
            is_active = (
                chat["session_id"] == st.session_state.session_id
            )

            if is_active:
                st.markdown(f"**🟢 {chat['title']}**")
                st.caption(chat.get("preview", "New conversation"))
            else:
                if st.button(
                    f"⚪ {chat['title']}",
                    key                 = f"chat_{chat['session_id']}",
                    use_container_width = True
                ):
                    # save current chat summary before switching
                    save_current_chat_summary()

                    st.session_state.session_id = chat["session_id"]
                    st.session_state.messages   = []

                    # load history from API
                    try:
                        resp = requests.get(
                            f"{API_URL}/history/{chat['session_id']}",
                            timeout = 5
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            for conv in data.get("conversations", []):
                                st.session_state.messages.append({
                                    "role"   : "user",
                                    "content": conv["user_message"]
                                })
                                st.session_state.messages.append({
                                    "role"    : "assistant",
                                    "content" : conv["bot_response"],
                                    "source"  : conv.get("source"),
                                    "category": conv.get("category")
                                })
                    except Exception:
                        pass

                    st.rerun()

            # update preview with first user message
            if (is_active and
                st.session_state.messages and
                st.session_state.chat_sessions[i].get("preview") == "New conversation"):
                first_msg = next(
                    (m["content"] for m in st.session_state.messages
                     if m["role"] == "user"), None
                )
                if first_msg:
                    st.session_state.chat_sessions[i]["preview"] = (
                        first_msg[:30] + "..."
                        if len(first_msg) > 30
                        else first_msg
                    )

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

        # ── Bottom Buttons ────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            # clear current chat
            if st.button("🗑️ Clear",
                         use_container_width=True):
                try:
                    requests.delete(
                        f"{API_URL}/history/"
                        f"{st.session_state.session_id}",
                        timeout = 5
                    )
                except Exception:
                    pass
                st.session_state.messages = []
                st.rerun()

        with col2:
            # logout button
            if st.button("🚪 Logout",
                         use_container_width=True):
                # save summary before logout
                save_current_chat_summary()

                # clear all session data
                st.session_state.logged_in    = False
                st.session_state.user_id      = None
                st.session_state.user_name    = None
                st.session_state.access_token = None
                st.session_state.messages     = []
                st.session_state.session_id   = str(uuid.uuid4())
                st.session_state.chat_sessions = []
                st.session_state.page         = "login"
                st.rerun()
