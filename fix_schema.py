
import sqlite3
import os

DB_PATH = 'db/soulsense.db'

def check_schema():
    if not os.path.exists(DB_PATH):
        print(f"❌ DB not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Checking schema for 'journal_entries'...")
    try:
        cursor.execute("PRAGMA table_info(journal_entries)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]} (Type: {col[2]})")
            
        col_names = [col[1] for col in columns]
        if 'user_id' not in col_names:
            print("❌ 'user_id' column is MISSING!")
            # Fix it
            print("🔧 Attempting to add 'user_id' column...")
            cursor.execute("ALTER TABLE journal_entries ADD COLUMN user_id INTEGER REFERENCES users(id)")
            conn.commit()
            print("✅ 'user_id' column added.")
        else:
            print("✅ 'user_id' column exists.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
