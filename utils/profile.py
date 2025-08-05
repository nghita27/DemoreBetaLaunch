# utils/profile.py

import sqlite3

from .db_utils import get_connection

def load_user_profile(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT artist_name, profile_img FROM profile WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()

    if result:
        return {"display_name": result[0], "avatar_url": result[1]}
    return {"display_name": "Unknown", "avatar_url": None}

def save_profile_info(user_id, name, bio, avatar_data):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        UPDATE users
        SET display_name = ?, bio = ?, avatar_url = ?
        WHERE id = ?
    """, (name, bio, avatar_data, user_id))
    conn.commit()
    conn.close()

def get_unread_count(user_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM messages 
        WHERE receiver_id = ? AND is_read = 0
    """, (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_profile(user_id):
    import sqlite3
    conn = sqlite3.connect("portfolio.db")
    c = conn.cursor()
    c.execute("SELECT * FROM profile WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_profile_dict(user_id):
    row = get_profile(user_id)
    if row:
        return {
            "user_id": row[0],
            "about": row[1],
            "about_public": row[2],
            "social_links": row[3],
            "social_public": row[4],
            "profile_img": row[5],
            "artist_name": row[6],
            "roles": row[7]
        }
    return None
