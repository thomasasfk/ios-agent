import sqlite3
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

class NotesDB:
    def __init__(self, db_path: str = ".notes.db"):
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    transcription TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)

    def create_note(self, title: str, transcription: str) -> int:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (title, transcription, created_at) VALUES (?, ?, ?)",
                (title, transcription, now)
            )
            conn.commit()
            return cursor.lastrowid

@dataclass
class Dependencies:
    notes_db: NotesDB = NotesDB()

class NoteResponse(BaseModel):
    title: str
    note_id: int

SYSTEM_PROMPT = "You are a note-taking assistant. Save transcriptions with relevant titles using create_note()."

agent = Agent(
    "openai:gpt-4o-mini",
    deps_type=Dependencies,
    result_type=NoteResponse,
    system_prompt=SYSTEM_PROMPT,
)

@agent.tool
def create_note(ctx: RunContext[Dependencies], title: str, transcription: str) -> int:
    """Creates a new note with the given title and transcription."""
    return ctx.deps.notes_db.create_note(title, transcription)

def run_agent(transcription: str) -> str:
    """Runs the agent with the given transcription and returns the response as JSON"""
    run_result = agent.run_sync(transcription, deps=Dependencies())
    return run_result.data.model_dump_json()