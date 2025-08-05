import sqlite3
import bcrypt
import os
from datetime import datetime
from Security.hash_password import check_password
import random
import string


# === Constants ===
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.db")
RESET_LINK_TEMPLATE = "http://yourapp.com/reset-password?token={token}"  # Replace with your real frontend link

import sqlite3
import hashlib
import uuid


def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== REGISTER ==========
# Security/auth_db.py

def register_user(username, email, password):
    user_id = str(uuid.uuid4())
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO users (id, username, email, password)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, email, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()


# ========== LOGIN ==========
def verify_user_credentials(username, password):
    hashed_pw = hash_password(password)
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT id FROM users WHERE username=? AND password=?
    """, (username, hashed_pw))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None  # return user_id or None



import sqlite3
import bcrypt
import os
import random
import string
import smtplib
import ssl
from email.message import EmailMessage
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "portfolio.db")

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# === Send Password Reset Email ===
import random
import string

# === Send Password Reset Email ===
import random
import string

def send_password_reset_email(email):
    email = email.lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Fetch user id and username
    c.execute("SELECT id, username FROM users WHERE LOWER(email) = ?", (email,))
    user = c.fetchone()

    if not user:
        conn.close()
        return False

    user_id, username = user

    # Generate temporary password
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    temp_hash = hash_password(temp_password)

    # Save temp password in DB (keep old password)
    c.execute("UPDATE users SET temp_password=? WHERE LOWER(email)=?", (temp_hash, email))
    conn.commit()
    conn.close()

    # Send email with link
    reset_link = f"https://demorebetalaunch-txreomisdcc3qmjfhvxqhb.streamlit.app/reset_password?email={email}"

    from email.message import EmailMessage
    import ssl, smtplib

    message = EmailMessage()
    message["Subject"] = "🔐 Reset Your BeautyBlend Password"
    message["From"] = "admin@beautyblend.company"
    message["To"] = email
    message.set_content(f"""
Hi {username},

Your temporary password is: {temp_password}

Click this link to set a new password:
{reset_link}

If you did not request this, please ignore this email.
""")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls(context=context)
            server.login("admin@beautyblend.company", "tvuq hyjk lehd hwab")
            server.send_message(message)

        print(f"✅ Reset email sent to {email}")
        return True
    except Exception as e:
        print(f"❌ Error sending reset email: {e}")
        return False

# === Save New Password ===
def save_new_password(email, new_password):
    hashed_pw = hash_password(new_password)
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE LOWER(email)=?", (hashed_pw, email.lower()))
    conn.commit()
    conn.close()


# ========== REMEMBER ME ==========
def update_remember_me(user_id, remember):
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    if remember:
        c.execute("UPDATE users SET remember_me = 0")
        c.execute("UPDATE users SET remember_me = 1 WHERE id = ?", (user_id,))
    else:
        c.execute("UPDATE users SET remember_me = 0 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()


# === Bulk Fix for Emails ===
def lowercase_all_emails():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET email = LOWER(email)")
        conn.commit()
        print("✅ All emails converted to lowercase.")
    except Exception as e:
        print("❌ Error while updating emails:", e)
    finally:
        conn.close()

# === Manual Test Utility ===
if __name__ == "__main__":
    print("=== Manual Test: Lookup Email for Reset ===")
    test_email = input("Enter email to test: ").strip()
    send_password_reset_email(test_email)


def update_user_password_from_token(token, new_password):
    # Extract user_id from mock token
    if not token.startswith("mock-token-"):
        return False
    try:
        user_id = int(token.replace("mock-token-", ""))
    except ValueError:
        return False

    new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()
    return True

# ========== GET USER ==========
def get_remembered_user():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE remember_me=1 LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row  # (user_id, username) or None

def get_user_by_id(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username, email FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def migrate_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]

    if "temp_password" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN temp_password TEXT")
        print("✅ Added temp_password column.")

    conn.commit()
    conn.close()

migrate_database()


def verify_temp_password(email, temp_password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT temp_password FROM users WHERE LOWER(email)=?", (email.lower(),))
    row = c.fetchone()
    conn.close()

    if not row or not row[0]:
        return False

    return hash_password(temp_password) == row[0]

def save_new_password(email, new_password):
    new_hash = hash_password(new_password)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET password=?, temp_password=NULL WHERE LOWER(email)=?", (new_hash, email.lower()))
    conn.commit()
    conn.close()

