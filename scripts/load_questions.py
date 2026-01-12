import os
from datetime import datetime
from app.db import get_connection
from app.models import ensure_question_bank_schema

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TXT_PATH = os.path.join(BASE_DIR, "data", "question_bank.txt")

def load_questions():
    conn = get_connection()
    cursor = conn.cursor()

    ensure_question_bank_schema(cursor)

    with open(TXT_PATH, "r", encoding="utf-8") as f:
        questions = [q.strip() for q in f if q.strip()]

    for q in questions:
        cursor.execute(
            "INSERT INTO question_bank (question_text, created_at) VALUES (?, ?)",
            (q, datetime.utcnow().isoformat())
        )

    conn.commit()
    conn.close()
    print(f"Loaded {len(questions)} questions into DB")

if __name__ == "__main__":
    load_questions()
