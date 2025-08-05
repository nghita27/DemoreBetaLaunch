from .db_utils import get_connection
import datetime
import json

def save_message_to_db(msg):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            data TEXT
        )
    """)
    user_id = msg.get("from", "unknown")
    c.execute("INSERT INTO messages (user_id, data) VALUES (?, ?)", (user_id, json.dumps(msg)))
    conn.commit()
    conn.close()

def send_message(from_id, to_id, content, email=""):
    msg = {
        "from": from_id,
        "to": to_id,
        "email": email,
        "content": content,
        "time": datetime.datetime.now().isoformat()
    }
    save_message_to_db(msg)

def load_messages_from_db(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT data FROM messages WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]