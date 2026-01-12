from app.questions import load_questions
from app.db import get_session
from app.models import Question

def test_load_questions_from_db(temp_db):
    session = get_session()
    q = Question(question_text="Test question?", is_active=1, min_age=20, max_age=80)
    session.add(q)
    session.commit()
    session.close()

    # Pass temp_db path just for signature compat, though it's ignored now (uses get_session)
    questions = load_questions(age=30)

    assert len(questions) == 1
    # load_questions returns list of (id, text)
    assert questions[0][1] == "Test question?"

def test_load_questions_age_filter(temp_db):
    session = get_session()
    q1 = Question(question_text="Kid question", is_active=1, min_age=1, max_age=10)
    q2 = Question(question_text="Adult question", is_active=1, min_age=20, max_age=80)
    session.add_all([q1, q2])
    session.commit()
    session.close()

    kid_qs = load_questions(age=5)
    assert len(kid_qs) == 1
    assert kid_qs[0][1] == "Kid question"

    adult_qs = load_questions(age=30)
    assert len(adult_qs) == 1
    assert adult_qs[0][1] == "Adult question"
