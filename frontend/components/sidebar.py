# ============================================
# NyayaAI — Sidebar Component
# Shows app info and category filters
# Displayed on left side of Streamlit app
# ============================================

import streamlit as st
from ai.config import APP_NAME, APP_VERSION, CATEGORIES


def render_sidebar():
    with st.sidebar:
        # app name and version
        st.title(f"⚖️ {APP_NAME}")
        st.caption(f"Version {APP_VERSION}")
        st.divider()

        # about section
        st.subheader("📌 About")
        st.info(
            "NyayaAI is a cybercrime awareness "
            "chatbot powered by RAG technology. "
            "Ask anything about cybercrime, "
            "digital arrest scams, banking fraud, "
            "and how to report complaints."
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

        # categories reference
        st.subheader("🏷️ Topics Covered")
        for category in CATEGORIES:
            st.markdown(f"• {category}")
        st.divider()

        # clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            # reset chat history in session state
            st.session_state.messages = []
            st.rerun()
