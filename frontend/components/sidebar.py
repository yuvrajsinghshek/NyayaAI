import streamlit as st
import uuid
import requests
from ai.config import APP_NAME, APP_VERSION, CATEGORIES

API_URL = "http://localhost:8000/chat"


def render_sidebar():
    with st.sidebar:
        st.title(f"⚖️ {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")
        st.divider()

        # initialize chat sessions list
        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = [{
                "session_id": st.session_state.session_id,
                "title"     : "Chat 1",
                "preview"   : "New conversation"
            }]

        # new chat button
        if st.button("➕ New Chat", use_container_width=True):
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

        # chat sessions list
        st.subheader("💬 Chats")

        for i, chat in enumerate(st.session_state.chat_sessions):
            is_active = (
                chat["session_id"] == st.session_state.session_id
            )

            # active chat highlighted differently
            if is_active:
                st.markdown(
                    f"**🟢 {chat['title']}**"
                )
                st.caption(chat.get("preview", ""))
            else:
                if st.button(
                    f"⚪ {chat['title']}",
                    key      = f"chat_{chat['session_id']}",
                    use_container_width = True
                ):
                    # switch to this chat
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
                st.session_state.chat_sessions[i]["preview"] == "New conversation"):
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

        # emergency contacts
        st.subheader("🆘 Emergency Contacts")
        st.error("📞 Cybercrime Helpline: **1930**")
        st.markdown(
            "🌐 [cybercrime.gov.in]"
            "(https://www.cybercrime.gov.in)"
        )
        st.markdown("📱 Follow **@cyberdost** on social media")
        st.divider()

        # topics covered
        st.subheader("🏷️ Topics Covered")
        for category in CATEGORIES:
            st.markdown(f"• {category}")
        st.divider()

        # clear current chat button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
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
