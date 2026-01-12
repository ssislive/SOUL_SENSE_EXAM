import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.config import DB_PATH
    print(f"DB_PATH resolved to: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("ERROR: Database file does not exist at path.")
    else:
        print("Database file exists.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {[t[0] for t in tables]}")
    
    if 'scores' not in [t[0] for t in tables]:
        print("CRITICAL: 'scores' table is MISSING.")
    else:
        # Try the query from refresh_analytics
        cursor.execute("SELECT COUNT(*), AVG(total_score) FROM scores")
        result = cursor.fetchone()
        print(f"Query Result: {result}")
        print("Query successful.")
        
    conn.close()

except Exception as e:
    print(f"EXCEPTION: {e}")
