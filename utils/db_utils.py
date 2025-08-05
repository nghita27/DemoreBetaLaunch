import sqlite3
import json

DB_PATH = "portfolio.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_bookings_from_db(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM bookings WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def save_booking(user_id, booking_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO bookings (user_id, data) VALUES (?, ?)", (user_id, json.dumps(booking_data)))
    conn.commit()
    conn.close()



def update_booking_visited_status(booking_id, visited_value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Load existing data
    c.execute("SELECT data FROM bookings WHERE id = ?", (booking_id,))
    row = c.fetchone()

    if row:
        data = json.loads(row[0])
        data["visited"] = visited_value

        # Save it back
        c.execute("UPDATE bookings SET data = ? WHERE id = ?", (json.dumps(data), booking_id))
        conn.commit()

    conn.close()

def delete_booking_from_db(user_id, booking_id):
    import sqlite3, json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT data FROM bookings WHERE id=? AND user_id=?", (booking_id, user_id))
    row = c.fetchone()
    if row:
        data = json.loads(row[0])
        data["status"] = "cancelled"
        c.execute("UPDATE bookings SET data=? WHERE id=? AND user_id=?", (json.dumps(data), booking_id, user_id))
        conn.commit()
    conn.close()


