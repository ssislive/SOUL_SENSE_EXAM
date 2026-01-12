import sqlite3
import os

DB_PATH = os.path.join("db", "soulsense_db")

def check():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("TABLES:", [t[0] for t in tables])

    # Check question_bank columns
    cursor.execute("PRAGMA table_info(question_bank)")
    print("\nQUESTION_BANK COLS:", cursor.fetchall())

    # Check question_category columns if it exists
    if ('question_category',) in tables:
        cursor.execute("PRAGMA table_info(question_category)")
        print("\nQUESTION_CATEGORY COLS:", cursor.fetchall())

    conn.close()

if __name__ == "__main__":
    check()
