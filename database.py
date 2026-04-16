import sqlite3

DB_NAME = "wishlist.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            photo_file_id TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_wish(user_id, title, description, photo_file_id = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO wishes (user_id, title, description, photo_file_id) VALUES (?, ?, ?, ?)",
        (user_id, title, description, photo_file_id)
    )

    conn.commit()
    conn.close()


def get_wishes(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, description, photo_file_id FROM wishes WHERE user_id = ?",
        (user_id,)
    )

    wishes = cursor.fetchall()
    conn.close()
    return wishes


def delete_wish(wish_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM wishes WHERE id = ? AND user_id = ?",
        (wish_id, user_id)
    )

    conn.commit()
    conn.close()


def update_wish(wish_id, user_id, title, description, photo_file_id = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE wishes SET title = ?, description = ?, photo_file_id = ? WHERE id = ? AND user_id = ?",
        (title, description, photo_file_id, wish_id, user_id)
    )

    conn.commit()
    conn.close()