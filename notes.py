import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List


class NotesDB:
    def __init__(self, db_path: str = ".notes.database"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    is_current BOOLEAN NOT NULL DEFAULT 0,
                    version INTEGER NOT NULL DEFAULT 1
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS note_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    version INTEGER NOT NULL,
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                )
            """
            )
            cursor.execute(
                """
                CREATE TRIGGER IF NOT EXISTS ensure_single_current
                AFTER UPDATE ON notes
                WHEN NEW.is_current = 1
                BEGIN
                    UPDATE notes SET is_current = 0 
                    WHERE id != NEW.id AND is_current = 1;
                END
            """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_note_history_note_id 
                ON note_history(note_id)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_note_history_version 
                ON note_history(note_id, version)
            """
            )
            conn.commit()

    def create_note(self, initial_content: str = "") -> int:
        """Creates a new note and sets it as the current note"""
        now = datetime.now().isoformat()
        initial_content = initial_content.strip()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notes SET is_current = 0")

            cursor.execute(
                """INSERT INTO notes 
                   (content, created_at, updated_at, is_current, version) 
                   VALUES (?, ?, ?, 1, 1)""",
                (initial_content, now, now)
            )
            note_id = cursor.lastrowid

            cursor.execute(
                """INSERT INTO note_history 
                   (note_id, content, created_at, version)
                   VALUES (?, ?, ?, 1)""",
                (note_id, initial_content, now)
            )

            conn.commit()
            return note_id

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
        new_content = new_content.strip()
        if not new_content:
            raise ValueError("Note content cannot be empty")

        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            current_note = cursor.execute(
                "SELECT id, version FROM notes WHERE is_current = 1"
            ).fetchone()

            if not current_note:
                return None

            note_id, current_version = current_note
            new_version = current_version + 1

            cursor.execute(
                """INSERT INTO note_history 
                   (note_id, content, created_at, version)
                   SELECT id, content, updated_at, version
                   FROM notes WHERE id = ?""",
                (note_id,)
            )

            cursor.execute(
                """UPDATE notes 
                   SET content = ?, updated_at = ?, version = ?
                   WHERE id = ?""",
                (new_content, now, new_version, note_id)
            )

            conn.commit()
            return note_id