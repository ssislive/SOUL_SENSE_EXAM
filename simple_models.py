# simple_models.py
import sqlite3
from datetime import datetime

def get_scores(username):
    """Get scores for a user using direct SQLite"""
    conn = sqlite3.connect('soulsense_db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT total_score, timestamp, age 
        FROM scores 
        WHERE username = ? 
        ORDER BY timestamp
    """, (username,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_journal_entries(username):
    """Get journal entries for a user"""
    conn = sqlite3.connect('soulsense_db')
    cursor = conn.cursor()
    
    # Check if journal_entries table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal_entries'")
    if not cursor.fetchone():
        conn.close()
        return []
    
    cursor.execute("""
        SELECT sentiment_score, emotional_patterns, created_at 
        FROM journal_entries 
        WHERE username = ? 
        ORDER BY created_at
    """, (username,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def add_sample_scores(username):
    """Add sample scores for testing"""
    conn = sqlite3.connect('soulsense_db')
    cursor = conn.cursor()
    
    # Check if user has any scores
    cursor.execute("SELECT COUNT(*) FROM scores WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    
    if count < 3:
        print(f"Adding sample scores for {username}...")
        sample_scores = [15, 18, 20, 17, 22]
        
        for i, score in enumerate(sample_scores):
            timestamp = (datetime.now() - timedelta(days=(len(sample_scores)-i)*7)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO scores (username, total_score, age, timestamp) VALUES (?, ?, ?, ?)",
                (username, score, 25, timestamp)
            )
        
        conn.commit()
        print(f"Added {len(sample_scores)} sample scores")
    
    conn.close()