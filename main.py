import sqlite3
from datetime import datetime
from flask import Flask, request
import os, tempfile, openai, sys
from flask.cli import load_dotenv
from functools import wraps
from loguru import logger
from logging import Handler


logger.remove()
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}")
logger.add("app.log", rotation="500 MB", retention="5 days")

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")


class LoguruHandler(Handler):
    def emit(self, record):
        logger.opt(depth=6, exception=record.exc_info)\
            .log(record.levelname, record.getMessage())

app.logger.handlers = []
app.logger.addHandler(LoguruHandler())

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
        logger.warning(f"Rejected IP: {request.remote_addr}")
        return {}, 403
    return decorated

@app.route("/transcribe", methods=["POST"])
@require_auth_header
def transcribe_audio():
    logger.info("Processing audio transcription")
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

if __name__ == "__main__":
    init_db()
    logger.info("Starting Flask server")
    app.run(debug=bool(os.getenv("DEBUG")), host="0.0.0.0", port=1337)