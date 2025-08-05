import sqlite3
import os

class FaceSketchDB:
    def __init__(self, db_path="portfolio.db"):
        self.db_path = db_path
        self._init_table()

    def _init_table(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Check schema
        c.execute("PRAGMA table_info(face_sketches)")
        existing_columns = [col[1] for col in c.fetchall()]

        # Auto-upgrade if table doesn't exist
        if not existing_columns:
            c.execute('''
                CREATE TABLE IF NOT EXISTS face_sketches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    image BLOB NOT NULL,
                    metadata TEXT,
                    category TEXT,
                    UNIQUE(user_id, metadata)
                )
            ''')
        conn.commit()
        conn.close()

    def save_face_sketch(self, user_id, image_bytes, metadata=None, category=None):
        if not user_id or not image_bytes:
            raise ValueError("user_id and image_bytes are required")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO face_sketches (user_id, image, metadata, category) VALUES (?, ?, ?, ?)",
            (user_id, image_bytes, metadata, category),
        )
        conn.commit()
        conn.close()

    def load_user_sketches(self, user_id, category_filter=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if category_filter:
            c.execute("SELECT id, image, metadata, category FROM face_sketches WHERE user_id=? AND category=?", (user_id, category_filter))
        else:
            c.execute("SELECT id, image, metadata, category FROM face_sketches WHERE user_id=?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def delete_sketch(self, sketch_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM face_sketches WHERE id=?", (sketch_id,))
        conn.commit()
        conn.close()

    def update_sketch(self, sketch_id, metadata=None, category=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if metadata is not None and category is not None:
            c.execute("UPDATE face_sketches SET metadata=?, category=? WHERE id=?", (metadata, category, sketch_id))
        elif metadata is not None:
            c.execute("UPDATE face_sketches SET metadata=? WHERE id=?", (metadata, sketch_id))
        elif category is not None:
            c.execute("UPDATE face_sketches SET category=? WHERE id=?", (category, sketch_id))
        conn.commit()
        conn.close()

    def create_table_if_needed(self):
        self._init_table()

def load_in_progress_sketch(user_id):
    conn = sqlite3.connect(self.db_path)
    c = conn.cursor()
    c.execute("SELECT image FROM face_sketches WHERE user_id=? AND metadata='In Progress'", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None
def load_in_progress_sketch(user_id):
    return _db.load_in_progress_sketch(user_id)
def save_face_sketch(self, user_id, image_bytes, metadata=None, category=None):
    if not user_id or not image_bytes:
        raise ValueError("user_id and image_bytes are required")
    
    conn = sqlite3.connect(self.db_path)
    c = conn.cursor()

    # Check for existing "In Progress" sketch
    if metadata == "In Progress":
        c.execute("""
            SELECT id FROM face_sketches WHERE user_id=? AND metadata='In Progress'
        """, (user_id,))
        existing = c.fetchone()
        if existing:
            c.execute("""
                UPDATE face_sketches
                SET image=?, category=?
                WHERE id=?
            """, (image_bytes, category, existing[0]))
        else:
            c.execute("""
                INSERT INTO face_sketches (user_id, image, metadata, category)
                VALUES (?, ?, ?, ?)
            """, (user_id, image_bytes, metadata, category))
    else:
        c.execute("""
            INSERT INTO face_sketches (user_id, image, metadata, category)
            VALUES (?, ?, ?, ?)
        """, (user_id, image_bytes, metadata, category))

    conn.commit()
    conn.close()

def load_in_progress_sketch(self, user_id):
    conn = sqlite3.connect(self.db_path)
    c = conn.cursor()
    c.execute("SELECT image FROM face_sketches WHERE user_id=? AND metadata='In Progress'", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

# ---- FUNCTION WRAPPERS FOR EASY IMPORT ----
_db = FaceSketchDB()

def save_face_sketch(user_id, image_bytes, metadata=None, category=None):
    _db.save_face_sketch(user_id, image_bytes, metadata, category)

def load_user_sketches(user_id, category_filter=None):
    return _db.load_user_sketches(user_id, category_filter)

def delete_sketch(sketch_id):
    _db.delete_sketch(sketch_id)

def update_sketch(sketch_id, metadata=None, category=None):
    _db.update_sketch(sketch_id, metadata, category)

def create_face_sketches_table():
    _db.create_table_if_needed()

def initialize_all_tables():
    create_face_sketches_table()
    # Future expansion point for other modules
