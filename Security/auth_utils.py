# Security/auth_utils.py
import sqlite3
import os
import streamlit as st

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "portfolio.db"))

def init_auth_session():
    if "auth_status" not in st.session_state:
        st.session_state["auth_status"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.session_state["remember_me"] = False

        # Check "remember me" from DB if available
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE remember_me = 1 LIMIT 1")
        row = c.fetchone()
        conn.close()
        if row:
            st.session_state["auth_status"] = True
            st.session_state["user_id"] = row[0]
            st.session_state["username"] = row[1]
            st.session_state["remember_me"] = True
