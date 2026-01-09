
import logging
from datetime import datetime
from app.db import get_session
from app.models import JournalEntry

logging.basicConfig(level=logging.INFO)

def test_journal_insert():
    print("Testing Journal Entry Insertion...")
    session = get_session()
    try:
        entry = JournalEntry(
            username="test_user",
            entry_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            content="This is a test entry from the debug script.",
            sentiment_score=50.0,
            emotional_patterns="Test pattern"
        )
        session.add(entry)
        session.commit()
        print("✅ Successfully inserted journal entry.")
        
        # Verify
        saved_entry = session.query(JournalEntry).filter_by(username="test_user").order_by(JournalEntry.id.desc()).first()
        print(f"✅ Verified read back: {saved_entry.content}")
        
    except Exception as e:
        print(f"❌ Failed to insert journal entry: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    test_journal_insert()
