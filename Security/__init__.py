# Security/__init__.py

from .auth_db import (
    register_user,
    verify_user_credentials,
    send_password_reset_email,
    get_user_by_id,
    update_remember_me,
)

import sqlite3

def init_user_table():
    """Ensures the 'users' table exists."""
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password TEXT,
        remember_me INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

# Optional: Automatically run the init if the file is imported directly
try:
    init_user_table()
except Exception as e:
    print("⚠️ Failed to initialize 'users' table:", e)
