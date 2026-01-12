
import sqlite3
import os
from app.config import DB_PATH

def check_and_fix_schema():
    print(f"Checking schema for {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("DB file not found. It will be created fresh.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get columns for scores
    cursor.execute("PRAGMA table_info(scores)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Columns in scores: {columns}")
    
    needed_columns = {
        "sentiment_score": "REAL DEFAULT 0.0",
        "reflection_text": "TEXT",
        "is_rushed": "BOOLEAN DEFAULT 0",
        "is_inconsistent": "BOOLEAN DEFAULT 0",
        "detailed_age_group": "TEXT",
        "user_id": "INTEGER"
    }
    
    for col, definition in needed_columns.items():
        if col not in columns:
            print(f"Missing column '{col}'. Adding...")
            try:
                cursor.execute(f"ALTER TABLE scores ADD COLUMN {col} {definition}")
                print(f"Added {col}.")
            except Exception as e:
                print(f"Failed to add {col}: {e}")
                
    conn.commit()
    conn.close()
    print("Schema check complete.")

if __name__ == "__main__":
    check_and_fix_schema()
