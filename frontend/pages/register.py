import streamlit as st
import requests

import os
API_URL = os.getenv("API_URL_AUTH", "http://localhost:8000/auth")

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam",
    "Bihar", "Chhattisgarh", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu & Kashmir", "Ladakh"
]


def render_register_page():
    st.title("⚖️ NyayaAI")
    st.subheader("Create your account")
    st.divider()

    if "register_step" not in st.session_state:
        st.session_state.register_step = 1

    steps = ["Account Details", "Verify Email", "Your Info"]
    st.progress(
        (st.session_state.register_step - 1) / 2,
        text = f"Step {st.session_state.register_step} of 3 — {steps[st.session_state.register_step - 1]}"
    )
    st.divider()

    if st.session_state.register_step == 1:
        st.subheader("Step 1 — Account Details")

        email    = st.text_input("Email",
                    placeholder="your@email.com")
        password = st.text_input("Password",
                    type="password",
                    placeholder="Min 6 characters")
        confirm  = st.text_input("Confirm Password",
                    type="password",
                    placeholder="Repeat password")

        if st.button("Send OTP", use_container_width=True):
            if not email or not password or not confirm:
                st.error("Please fill all fields")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != confirm:
                st.error("Passwords do not match")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/register",
                        json    = {
                            "email"   : email,
                            "password": password
                        },
                        timeout = 30
                    )
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.reg_email     = email
                        st.session_state.reg_otp       = str(data.get("otp", ""))
                        st.session_state.register_step = 2
                        st.rerun()
                    elif response.status_code == 400 and "already registered" in data.get("detail", "").lower():
                        st.session_state.reg_email     = email
                        st.session_state.register_step = 2
                        st.info("Email already registered. OTP sent again — check your email.")
                        st.rerun()
                    else:
                        error = data.get("detail", "Registration failed")
                        st.error(error)

                except requests.exceptions.ConnectionError:
                    st.error("Backend not running")
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    elif st.session_state.register_step == 2:
        st.subheader("Step 2 — Verify Email")
        st.info(f"OTP sent to: {st.session_state.reg_email}")
        if st.session_state.get("reg_otp"):
            st.warning(f"Your OTP: {st.session_state.reg_otp}")

        otp = st.text_input("Enter OTP",
                placeholder="6 digit OTP")

        if st.button("Verify OTP", use_container_width=True):
            if not otp:
                st.error("Please enter OTP")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/verify-otp",
                        json    = {
                            "email": st.session_state.reg_email,
                            "otp"  : otp
                        },
                        timeout = 30
                    )
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 200:
                        st.session_state.register_step = 3
                        st.success("Email verified!")
                        st.rerun()
                    else:
                        error = data.get("detail", "Invalid OTP")
                        st.error(error)
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

        if st.button("Resend OTP", use_container_width=True):
            try:
                requests.post(
                    f"{API_URL}/forgot-password",
                    json    = {"email": st.session_state.reg_email},
                    timeout = 30
                )
                st.success("OTP resent!")
            except Exception:
                st.error("Something went wrong")

    elif st.session_state.register_step == 3:
        st.subheader("Step 3 — Tell us about yourself")

        name  = st.text_input("Full Name",
                    placeholder="Your name")
        age   = st.number_input("Age",
                    min_value=10,
                    max_value=100,
                    value=25)
        city  = st.text_input("City",
                    placeholder="Your city")
        state = st.selectbox("State",
                    options=["Select State"] + INDIAN_STATES)

        if st.button("Complete Registration",
                     use_container_width=True):
            if not name:
                st.error("Please enter your name")
            elif state == "Select State":
                st.error("Please select your state")
            else:
                try:
                    response = requests.post(
                        f"{API_URL}/user-info",
                        json    = {
                            "email": st.session_state.reg_email,
                            "name" : name,
                            "age"  : age,
                            "city" : city,
                            "state": state
                        },
                        timeout = 30
                    )
                    try:
                        data = response.json()
                    except Exception:
                        data = {}

                    if response.status_code == 200:
                        st.session_state.logged_in     = True
                        st.session_state.user_id       = data.get("user_id")
                        st.session_state.user_name     = data.get("name")
                        st.session_state.access_token  = data.get("access_token")
                        st.session_state.messages      = []
                        st.session_state.register_step = 1
                        st.success(f"Welcome to NyayaAI, {name}!")
                        st.rerun()
                    else:
                        error = data.get("detail", "Failed")
                        st.error(error)
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    st.divider()
    st.markdown("Already have an account?")
    if st.button("Login here", use_container_width=True):
        st.session_state.page          = "login"
        st.session_state.register_step = 1
        st.rerun()
