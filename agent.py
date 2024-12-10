import time
import sqlite3
from typing import Optional
from pydantic_ai import Agent
from datetime import datetime

DB_PATH = ".info.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nutrition_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT,
                calories INTEGER,
                protein_g REAL,
                fats_g REAL,
                carbs_g REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weight_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight_kg REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def log_nutrition_to_db(food_name: str, calories: Optional[int] = None,
                       protein: Optional[float] = None, fats: Optional[float] = None,
                       carbs: Optional[float] = None) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nutrition_logs (food_name, calories, protein_g, fats_g, carbs_g)
            VALUES (?, ?, ?, ?, ?)
        """, (food_name, calories, protein, fats, carbs))
        conn.commit()
        return cursor.lastrowid

def log_weight_to_db(weight_kg: float) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO weight_logs (weight_kg) VALUES (?)", (weight_kg,))
        conn.commit()
        return cursor.lastrowid

SYSTEM_PROMPT = """
You are a health tracking assistant that processes transcriptions to extract and log health-related information.
You can handle two types of information:

1. Nutrition information: When food items are mentioned with their nutritional content (calories, protein, fats, carbs)
2. Weight measurements: When body weight is mentioned

For nutrition logging:
- Identify each distinct food item mentioned in the transcription
- For each food item, extract its name and any associated nutritional information
- Call log_nutrition() separately for each food item, even if mentioned together
- Use None for any missing nutritional values
- Example: "I had oatmeal with 300 calories and a protein shake with 20g protein" should trigger two separate log_nutrition() calls

For weight logging:
- Extract weight in kg (convert if given in lbs)
- Use log_weight() to save the measurement

Return a summary of the actions taken, or indicate if no relevant information was found to log.
"""

agent = Agent(
    "openai:gpt-4o-mini",
    result_type=str,
    system_prompt=SYSTEM_PROMPT,
)

@agent.tool
def log_nutrition(food_name: str, calories: Optional[int] = None,
                 protein: Optional[float] = None, fats: Optional[float] = None,
                 carbs: Optional[float] = None) -> int:
    """Logs nutrition information for a food item to the database."""
    return log_nutrition_to_db(food_name, calories, protein, fats, carbs)

@agent.tool
def log_weight(weight_kg: float) -> int:
    """Logs a weight measurement to the database."""
    return log_weight_to_db(weight_kg)

def process(transcription: str) -> str:
    init_db()
    run_result = agent.run_sync(transcription)
    with open("agent_actions.log", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Transcription: {transcription}\nAction: {run_result.data}\n\n")
    return run_result.data

def main():
    conn = sqlite3.connect(".notes.db")
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(id) FROM notes")
    last_id = cursor.fetchone()[0] or 0
    while True:
        cursor.execute("SELECT id, transcription FROM notes WHERE id > ?", (last_id,))
        new_entries = cursor.fetchall()
        for entry_id, transcription in new_entries:
            process(transcription)
            last_id = entry_id
        time.sleep(5)

if __name__ == "__main__":
    main()