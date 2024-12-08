import sqlite3
from datetime import datetime


class NotesDB:
    def __init__(self, db_path: str = ".notes.database"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.cursor().execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP NOT NULL
                )
            """
            )
            conn.commit()

    def save_note(self, content: str, category: str = "general") -> int:
        if not content.strip():
            raise ValueError("Note content cannot be empty")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (content, category, created_at) VALUES (?, ?, ?)",
                (content.strip(), category.lower(), datetime.now().isoformat())
            )
            conn.commit()
            return cursor.lastrowid
