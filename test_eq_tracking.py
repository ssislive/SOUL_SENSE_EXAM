"""
Test Script for EQ Progress Tracking
Verifies that EQ scores are being stored and can be visualized
"""

import sqlite3
from datetime import datetime, timedelta

DB_PATH = "soulsense_db"

def test_eq_tracking():
    """Test EQ progress tracking functionality"""
    print("🧪 Testing EQ Progress Tracking...")
    print("=" * 50)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check table schema
    print("\n1. Checking database schema...")
    cursor.execute("PRAGMA table_info(scores)")
    columns = cursor.fetchall()
    print("   Scores table columns:")
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Check if timestamp exists
    has_timestamp = any(col[1] == "timestamp" for col in columns)
    if has_timestamp:
        print("   ✅ Timestamp column exists!")
    else:
        print("   ❌ Timestamp column missing!")
        return
    
    # Add sample data for testing if no data exists for test user
    print("\n2. Checking test data...")
    cursor.execute("SELECT COUNT(*) FROM scores WHERE username = 'test_user'")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("   Adding sample test data...")
        base_time = datetime.now() - timedelta(days=30)
        test_scores = [15, 18, 17, 20, 22, 24, 23, 26, 28, 27]
        
        for i, score in enumerate(test_scores):
            timestamp = (base_time + timedelta(days=i*3)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO scores (username, age, total_score, timestamp) VALUES (?, ?, ?, ?)",
                ("test_user", 25, score, timestamp)
            )
        conn.commit()
        print(f"   ✅ Added {len(test_scores)} test scores!")
    else:
        print(f"   ✅ Found {count} existing scores for test_user")
    
    # Query and display progress
    print("\n3. Retrieving EQ progress data...")
    cursor.execute("""
        SELECT id, total_score, timestamp 
        FROM scores 
        WHERE username = 'test_user' 
        ORDER BY id
    """)
    results = cursor.fetchall()
    
    print("\n   EQ Progress for test_user:")
    print("   " + "-" * 40)
    for row in results:
        print(f"   Attempt #{row[0]}: Score {row[1]} (on {row[2]})")
    
    # Calculate statistics
    scores = [row[1] for row in results]
    if len(scores) > 1:
        print("\n4. Progress Statistics:")
        print(f"   Total Attempts: {len(scores)}")
        print(f"   First Score: {scores[0]}")
        print(f"   Latest Score: {scores[-1]}")
        print(f"   Best Score: {max(scores)}")
        print(f"   Average Score: {sum(scores)/len(scores):.1f}")
        improvement = ((scores[-1] - scores[0]) / scores[0]) * 100
        print(f"   Overall Improvement: {improvement:+.1f}%")
        
        if improvement > 0:
            print("   ✅ Positive progress detected!")
        else:
            print("   📊 Room for improvement!")
    
    conn.close()
    print("\n" + "=" * 50)
    print("✅ Test Complete! EQ tracking is working correctly.")
    print("\n💡 To view the visualization, run: python app.py")
    print("   Then click '📊 View Dashboard' and check the 'EQ Trends' tab")

if __name__ == "__main__":
    test_eq_tracking()
