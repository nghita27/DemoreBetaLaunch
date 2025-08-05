# LoginRegister.py (Main UI for Login, Register, Forgot Password)
import streamlit as st
import sqlite3
import os

from auth_db import (
    register_user,
    verify_user_credentials,
    send_password_reset_email,
    get_user_by_id,
    update_remember_me
)

# --- Persistent Session Check (on first load only) ---
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["remember_me"] = False

    # Try to load session from file
    if os.path.exists(".login_session"):
        with open(".login_session", "r") as f:
            data = f.read().strip().split("::")
            if len(data) == 2:
                st.session_state["auth_status"] = True
                st.session_state["user_id"] = data[0]
                st.session_state["username"] = data[1]
    else:
        # Optional: fallback to DB if remember_me
        conn = sqlite3.connect("portfolio.db")
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE remember_me = 1 LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            st.session_state["auth_status"] = True
            st.session_state["user_id"] = row[0]
            st.session_state["username"] = row[1]
            with open(".login_session", "w") as f:
                f.write(f"{row[0]}::{row[1]}")

# --- Top-right dropdown ---
col1, col2 = st.columns([8, 1])
with col2:
    account_action = st.selectbox(
        "Account",
        ["", "Log in", "Register", "Forgot Password", "Logout" if st.session_state["auth_status"] else ""],
        format_func=lambda x: "Account" if x == "" else x,
        label_visibility="collapsed",
        key="account_action_ui"
    )

# --- Log in ---
if account_action == "Log in":
    with st.form("login_form"):
        st.subheader("🔐 Log In")
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember my account")
        submit = st.form_submit_button("Log In")

        if submit:
            user_id = verify_user_credentials(username, password)
            if user_id:
                st.session_state["auth_status"] = True
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username
                st.session_state["remember_me"] = remember
                update_remember_me(user_id, remember)

                # Save to file for persistence
                with open(".login_session", "w") as f:
                    f.write(f"{user_id}::{username}")

                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Incorrect username or password")

# --- Register ---
elif account_action == "Register":
    with st.form("register_form"):
        st.subheader("📝 Register")
        new_username = st.text_input("Username")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

        if submit:
            if register_user(new_username, new_email, new_password):
                st.success("Registration successful! Please log in.")
            else:
                st.error("Username or email already exists")

# --- Forgot Password ---
elif account_action == "Forgot Password":
    with st.form("forgot_form"):
        st.subheader("❓ Forgot Password")
        email = st.text_input("Enter your registered email")
        submit = st.form_submit_button("Send Reset Link")

        if submit:
            if send_password_reset_email(email):
                st.success("Reset link sent! Please check your email.")
            else:
                st.error("Email not found in our system.")

# --- Logout ---
elif account_action == "Logout" and st.session_state["auth_status"]:
    st.session_state["auth_status"] = False
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.session_state["remember_me"] = False

    if os.path.exists(".login_session"):
        os.remove(".login_session")

    st.success("You have been logged out.")
    st.experimental_rerun()

# --- Greeting Banner ---
if st.session_state["auth_status"]:
    st.markdown(
        f"<div style='position:fixed; top:10px; right:30px; z-index:999;'>"
        f"<b>Welcome, {st.session_state['username']}!</b> "
        f"</div>",
        unsafe_allow_html=True
    )

user = verify_user_credentials(username, password)
if user:
    st.session_state["auth_status"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    #st.session_state["role"] = user["role"]
