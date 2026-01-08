"""
Database Migration Script
Adds timestamp column to existing scores table for EQ progress tracking
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = "soulsense_db"

def migrate_database():
    """Add timestamp column to scores table if it doesn't exist"""
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Nothing to migrate.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if timestamp column exists
        cursor.execute("PRAGMA table_info(scores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "timestamp" not in columns:
            print("Adding timestamp column to scores table...")
            cursor.execute("ALTER TABLE scores ADD COLUMN timestamp TEXT")
            
            # Update existing records with current timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE scores SET timestamp = ? WHERE timestamp IS NULL", (current_time,))
            
            conn.commit()
            print("✅ Migration successful! Timestamp column added.")
        else:
            print("✅ Database already up to date. Timestamp column exists.")
    
    except sqlite3.Error as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()
    print("Migration complete!")
