
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

from app.services.exam_service import ExamSession
from app.models import Base
from app.db import engine

def test_exam_flow():
    print("Testing ExamSession...")
    
    # Mock questions: (id, text, tooltip, min, max)
    questions = [
        (1, "I feel happy often.", "Happy is good", 10, 100),
        (2, "I get angry easily.", "Anger mgmt", 10, 100),
        (3, "I sleep well.", None, 10, 100)
    ]
    
    session = ExamSession("test_user_cli", 25, "Adult", questions)
    session.start_exam()
    
    # Q1
    q1 = session.get_current_question()
    print(f"Q1: {q1}")
    assert q1[0] == "I feel happy often."
    session.submit_answer(3) # Often
    
    # Q2
    q2 = session.get_current_question()
    print(f"Q2: {q2}")
    session.submit_answer(1) # Never
    
    # Q3
    q3 = session.get_current_question()
    print(f"Q3: {q3}")
    
    # Test Back
    print("Testing Back...")
    session.go_back()
    q2_again = session.get_current_question()
    assert q2_again[0] == "I get angry easily."
    session.submit_answer(2) # Sometimes (changed answer)
    
    # Submit Q3
    session.submit_answer(4) # Always
    
    # Reflection
    print("Testing Reflection...")
    session.submit_reflection("I feel great about this test.")
    print(f"Sentiment: {session.sentiment_score}")
    
    # Finish
    success = session.finish_exam()
    print(f"Exam Finished: {success}")
    print(f"Final Score: {session.score}") # 3 + 2 + 4 = 9
    
    assert session.score == 9
    assert session.is_finished()
    
    print("✅ ExamSession Test Passed!")

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    test_exam_flow()
