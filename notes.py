import sqlite3
from datetime import datetime
from typing import Optional, Tuple


class NotesDB:
    def __init__(self, db_path: str = ".notes.database"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT 0
                )
            """)
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS ensure_single_current
                AFTER UPDATE ON notes
                WHEN NEW.is_current = 1
                BEGIN
                    UPDATE notes SET is_current = 0 
                    WHERE id != NEW.id AND is_current = 1;
                END
            """)
            conn.commit()

    def create_note(self, initial_content: str = "") -> int:
        """Creates a new note and sets it as the current note"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET is_current = 0")
            cursor.execute(
                """INSERT INTO notes 
                   (content, created_at, updated_at, is_current) 
                   VALUES (?, ?, ?, 1)""",
                (initial_content.strip(), now, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get_current_note(self) -> Optional[Tuple[int, str, str, str]]:
        """Returns the current note's (id, content, created_at, updated_at) or None if no current note exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute(
                """SELECT id, content, created_at, updated_at 
                   FROM notes WHERE is_current = 1"""
            ).fetchone()
            return result

    def update_current_note(self, new_content: str) -> Optional[int]:
        """Updates the current note's content and timestamp. Returns note id or None if no current note."""
        if not new_content.strip():
            raise ValueError("Note content cannot be empty")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE notes 
                   SET content = ?, updated_at = ? 
                   WHERE is_current = 1
                   RETURNING id""",
                (new_content.strip(), datetime.now().isoformat())
            )
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None