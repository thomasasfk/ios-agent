import sqlite3
from datetime import datetime

import logfire
from flask.cli import load_dotenv

logfire.configure()
load_dotenv()

class NotesDB:
    def __init__(self, db_path: str = ".notes.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transcription TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)

    def create_note(self, transcription: str) -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (transcription, created_at) VALUES (?, ?)",
                (transcription, now)
            )
            conn.commit()
            return cursor.lastrowid