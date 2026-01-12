from app.db import get_connection

def add_tooltips():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Update a few questions with tooltips
    updates = [
        ("This refers to identifying what you are feeling in the moment.", 1),
        ("Think about how quickly you can calm yourself down after being upset.", 3),
        ("This involves being aware of how your actions affect those around you.", 5)
    ]
    
    print("Adding tooltips for testing...")
    for text, q_id in updates:
        cursor.execute("UPDATE question_bank SET tooltip = ? WHERE id = ?", (text, q_id))
        if cursor.rowcount > 0:
            print(f"✅ Updated question {q_id} with tooltip.")
        else:
            print(f"⚠️ Question {q_id} not found.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_tooltips()
