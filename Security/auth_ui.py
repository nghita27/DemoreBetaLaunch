# Security/auth_ui.py
import streamlit as st
from Security.auth_db import (
    register_user, verify_user_credentials,
    send_password_reset_email, update_user_password_from_token
)

def render_account_dropdown():
    col1, col2 = st.columns([8, 1])
    with col2:
        return st.selectbox(
            "Account",
            ["", "Log in", "Register", "Logout"],
            format_func=lambda x: "Account" if x == "" else x,
            label_visibility="collapsed",
            key="account_action_dropdown"
        )

def render_login_ui():
    st.subheader("🔐 Log In")
    username = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        user_id = verify_user_credentials(username, password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("✅ Logged in successfully!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def render_register_ui():
    st.subheader("🖌️ Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(username, email, password):
            st.success("✅ Registered successfully! Please log in.")
        else:
            st.error("❌ Username or email already exists.")

def render_logout():
    st.session_state.user_id = None
    st.success("✅ You have been logged out.")
    st.query_params.update({"logged_out": "1"})

def require_login():
    if "user_id" not in st.session_state or st.session_state.user_id is None:
        st.warning("🔒 Please log in to access this page.")
        st.stop()
