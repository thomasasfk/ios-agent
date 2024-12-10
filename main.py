import sqlite3
from datetime import datetime
from flask import Flask, request
import os, tempfile, openai
from flask.cli import load_dotenv
from functools import wraps

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def init_db(db_path=".notes.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )""")

def save_note(transcription, db_path=".notes.db"):
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO notes VALUES (NULL, ?, ?)",
                    (transcription, datetime.now().isoformat()))

def require_auth_header(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.headers.get(os.getenv("HEADER_KEY")) == os.getenv("HEADER_VALUE"):
            return f(*args, **kwargs)
        return {}, 403
    return decorated

@app.route("/transcribe", methods=["POST"])
@require_auth_header
def transcribe_audio():
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=True) as temp_file:
        temp_file.write(request.data)
        temp_file.flush()
        with open(temp_file.name, "rb") as audio_file:
            transcription = openai.audio.translations.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        save_note(transcription)
        return transcription

init_db()
app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=1337)