from .db_utils import get_connection

def compute_and_save_analytics(user_id, bookings):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    total = len(bookings)
    visited = sum(1 for b in bookings if b.get("visited", "Yes") == "Yes")
    missed = total - visited
    cancelled = sum(1 for b in bookings if b.get("status") == "cancelled")

    service_counts = {}
    for b in bookings:
        if b.get("visited", "Yes") == "Yes":
            svc = b.get("service")
            if svc:
                service_counts[svc] = service_counts.get(svc, 0) + 1

    visit_rate = (visited / total * 100) if total else 0
    most_booked = max(service_counts, key=service_counts.get) if service_counts else "N/A"

    c.execute("DELETE FROM analytics WHERE user_id=?", (user_id,))
    c.execute("""
        INSERT INTO analytics (user_id, total_bookings, cancelled_count, visited_count, missed_count, visit_rate, most_booked_service)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, total, cancelled, visited, missed, visit_rate, most_booked))

    conn.commit()
    conn.close()

    return total, cancelled, visited, missed, service_counts

    





def fetch_analytics(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM analytics WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result