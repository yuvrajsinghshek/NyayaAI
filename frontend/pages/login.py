import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL_AUTH", "http://localhost:8000/auth")


def render_login_page():
    st.title("⚖️ NyayaAI")
    st.subheader("Login to your account")
    st.divider()

    tab1, tab2 = st.tabs(["Login", "Forgot Password"])

    with tab1:
        email    = st.text_input("Email",
                    placeholder="Enter your email")
        password = st.text_input("Password",
                    type="password",
                    placeholder="Enter your password")

        if st.button("Login", use_container_width=True):
            if not email or not password:
                st.error("Please fill all fields")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/login",
                        json    = {
                            "email"   : email,
                            "password": password
                        },
                        timeout = 10
                    )
                    # safe json parsing
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 200:
                        st.session_state.logged_in    = True
                        st.session_state.user_id      = data.get("user_id")
                        st.session_state.user_name    = data.get("name")
                        st.session_state.access_token = data.get("access_token")
                        st.session_state.messages     = []
                        st.success(f"Welcome back, {data.get('name')}!")
                        st.rerun()
                    else:
                        error = data.get("detail", "Login failed")
                        st.error(error)

                except requests.exceptions.ConnectionError:
                    st.error("Backend not running.")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

        st.divider()
        st.markdown("Don't have an account?")
        if st.button("Register here", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    with tab2:
        st.subheader("Reset Password")

        if "forgot_step" not in st.session_state:
            st.session_state.forgot_step = 1

        if st.session_state.forgot_step == 1:
            forgot_email = st.text_input(
                "Enter your registered email",
                placeholder="your@email.com"
            )
            if st.button("Send OTP", use_container_width=True):
                if not forgot_email:
                    st.error("Please enter email")
                else:
                    try:
                        requests.post(
                            f"{API_URL}/forgot-password",
                            json    = {"email": forgot_email},
                            timeout = 10
                        )
                        st.session_state.forgot_email = forgot_email
                        st.session_state.forgot_step  = 2
                        st.success("OTP sent to your email!")
                        st.rerun()
                    except Exception:
                        st.error("Something went wrong")

        elif st.session_state.forgot_step == 2:
            st.info(f"OTP sent to: {st.session_state.forgot_email}")
            otp          = st.text_input("Enter OTP")
            new_password = st.text_input("New Password",
                            type="password")
            confirm      = st.text_input("Confirm Password",
                            type="password")

            if st.button("Reset Password", use_container_width=True):
                if not otp or not new_password or not confirm:
                    st.error("Please fill all fields")
                elif new_password != confirm:
                    st.error("Passwords do not match")
                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/reset-password",
                            json    = {
                                "email"       : st.session_state.forgot_email,
                                "otp"         : otp,
                                "new_password": new_password
                            },
                            timeout = 10
                        )
                        try:
                            data = response.json()
                        except Exception:
                            data = {}

                        if response.status_code == 200:
                            st.success("Password reset successfully!")
                            st.session_state.forgot_step = 1
                            st.rerun()
                        else:
                            error = data.get("detail", "Reset failed")
                            st.error(error)
                    except Exception:
                        st.error("Something went wrong")
