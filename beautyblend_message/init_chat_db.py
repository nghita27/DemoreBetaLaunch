import sqlite3

def init_chat_database():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # ----- USERS -----
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT,
        hashed_password TEXT,
        display_name TEXT,
        avatar_url TEXT,
	bio TEXT
    )
    """)

    # ----- MESSAGES -----
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_room_id INTEGER,
        sender_id TEXT,
        receiver_id TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0,
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(receiver_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized with users and messages tables.")

if __name__ == "__main__":
    init_chat_database()
