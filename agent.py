import sqlite3
import time

def process(transcription: str):
    print(transcription)

def main():
    print("starting")
    conn = sqlite3.connect(".notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM notes")
    last_id = cursor.fetchone()[0] or 0
    print(last_id)
    while True:
        cursor.execute("SELECT id, transcription FROM notes WHERE id > ?", (last_id,))
        new_entries = cursor.fetchall()
        print(new_entries)
        for entry_id, transcription in new_entries:
            process(transcription)
            last_id = entry_id
        time.sleep(5)

if __name__ == "__main__":
    main()